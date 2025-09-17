#
#  Copyright 2025 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import re
import os
import tempfile
import logging
from typing import List, Dict, Any, Tuple
from io import BytesIO
import hashlib

from api.db import LLMType
from api.db.services.llm_service import LLMBundle
from rag.nlp import rag_tokenizer, tokenize
from rag.utils.video_processor import VideoProcessor
from rag.utils.image_captioner import ImageCaptioner

logger = logging.getLogger(__name__)

# Video processing configuration
VIDEO_CONFIG = {
    'max_resolution': (1280, 720),  # Downsample for processing
    'frame_buffer_size': 10,        # Max frames in memory
    'whisperx_sampling': True,      # Primary method
    'fallback_interval': 5.0,       # If no speech detected
    'cleanup_temp_files': True,     
    'processing_timeout': 1300,     # 30 minutes max
    'model_name': "gpt-5-nano-2025-08-07",
}


def chunk(filename, binary, tenant_id, lang, callback=None, **kwargs):
    """
    Process video file and create chunks with frames and transcriptions.
    
    Args:
        filename: Name of the video file
        binary: Video file content as bytes
        tenant_id: Tenant ID for multi-tenancy
        lang: Language for transcription
        callback: Progress callback function
        **kwargs: Additional configuration options
    
    Returns:
        List of chunks containing transcribed text and associated video frames
    """
    chunks = []
    
    try:
        # Save video to temporary file for processing
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(filename)[1], delete=False) as tmp_file:
            tmp_file.write(binary)
            tmp_video_path = tmp_file.name
        
        try:
            # Step 1: Process audio with WhisperX
            callback(0.1, "Extracting and transcribing audio with WhisperX...")
            seq2txt_mdl = LLMBundle(tenant_id, LLMType.SPEECH2TEXT, lang=lang)
            # Disable diarization for video mode (keep it for audio mode)
            try:
                mdl = getattr(seq2txt_mdl, 'mdl', None)
                if mdl and hasattr(mdl, 'enable_diarization'):
                    mdl.enable_diarization = False
            except Exception:
                pass
            
            # Extract audio and transcribe
            transcription_result = seq2txt_mdl.transcription(binary)
            audio_text = transcription_result if isinstance(transcription_result, str) else transcription_result[0]
            
            # Check if transcription failed
            if audio_text.startswith("**ERROR**"):
                raise Exception(f"Audio transcription failed: {audio_text}")
            
            callback(0.3, f"Transcription complete: {audio_text[:100]}...")
            
            # Step 2: Initialize video processor
            video_processor = VideoProcessor(tmp_video_path)
            
            # Step 3: Build windows based on audio segments (preferred), else fixed intervals
            segments = []
            windows: List[Tuple[float, float]] = []
            timestamps: List[float] = []
            if VIDEO_CONFIG['whisperx_sampling'] and hasattr(seq2txt_mdl, 'get_segments'):
                try:
                    segments = seq2txt_mdl.get_segments() or []
                    # Normalize and sort segments
                    segments = [s for s in segments if isinstance(s, dict) and s.get('start') is not None and s.get('end') is not None]
                    segments.sort(key=lambda s: s['start'])
                    # Create non-overlapping windows directly from audio segments
                    windows = [(float(s['start']), float(s['end'])) for s in segments if s['end'] > s['start']]
                    # One frame at the start of each segment
                    timestamps = [float(s['end']) for s in segments]
                    callback(0.4, f"Using WhisperX segment windows: {len(windows)} windows")
                except Exception:
                    segments = []
                    windows = []
                    timestamps = []
            # Fallback to fixed interval windows if no audio segments
            if not timestamps:
                duration = max(0.0, float(video_processor.duration))
                interval = float(VIDEO_CONFIG['fallback_interval'])
                if interval <= 0:
                    interval = 5.0 # 5 seconds
                t = 0.0
                while t < duration:
                    start_t = t
                    end_t = min(t + interval, duration)
                    windows.append((start_t, end_t))
                    timestamps.append((start_t + end_t) / 2.0)
                    t = end_t
                callback(0.4, f"Using fixed windows: {len(windows)} x {interval:.1f}s")
            # Debug logging for windows and timestamps
            try:
                logger.info(f"[video.chunk] segments={len(segments)} windows={len(windows)} ts={len(timestamps)} duration={getattr(video_processor,'duration',None)}")
                logger.debug(f"[video.chunk] first_windows={(windows[:5])} first_ts={(list(map(lambda x: round(x,2), timestamps[:5])))}")
            except Exception:
                pass
            
            # Step 4: Extract frames at timestamps
            callback(0.5, "Extracting video frames...")
            frames = video_processor.extract_frames_at_timestamps(timestamps)
            try:
                logger.info(f"[video.chunk] extracted_frames={len(frames)}")
                if len(frames) > 0:
                    logger.debug(f"[video.chunk] first_frames_ts={(list(map(lambda x: round(x[0],2), frames[:5])))}")
            except Exception:
                pass

            callback(0.6, f"Extracted {len(frames)} frames")
            
            # Step 5: Initialize image captioner with GPT-5-nano
            callback(0.7, "Initializing GPT-5-nano for frame captioning...")
            openai_api_key = kwargs.get('openai_api_key', os.getenv('OPENAI_API_KEY'))
            
            if openai_api_key:
                image_captioner = ImageCaptioner(openai_api_key, model=VIDEO_CONFIG['model_name'])
                
                # Process frames for captioning
                frame_data = []
                for idx, (timestamp, frame) in enumerate(frames):
                    frame_data.append({
                        'timestamp': timestamp,
                        'image': frame,
                        'window': windows[idx] if idx < len(windows) else (timestamp, timestamp)
                    })
                
                # Get captions for frames with transcript context
                callback(0.8, "Generating frame captions with GPT-5-nano...")
                
                # Create simple segments from transcription for context
                audio_segments = [{
                    'start': 0,
                    'end': video_processor.duration,
                    'text': audio_text
                }]
                
                captioned_frames = image_captioner.process_frame_batch(
                    frame_data, 
                    batch_size=3,
                    transcript_segments=audio_segments
                )
            else:
                # No OpenAI key, skip captioning
                captioned_frames = []
                for timestamp, frame in frames:
                    captioned_frames.append({
                        'timestamp': timestamp,
                        'caption': f"Frame at {timestamp:.1f}s",
                        'frame': frame
                    })
            
            # Step 6: Create chunks with frames and non-overlapping transcript per frame window
            callback(0.9, "Creating video chunks...")
            # Ensure deterministic ordering by timestamp
            if captioned_frames:
                captioned_frames = sorted(captioned_frames, key=lambda x: x['timestamp'])
            if segments:
                segments = sorted(segments, key=lambda s: (0 if s.get('start') is None else s.get('start')))

            # Helper: get transcript strictly between (prev_ts, ts], using full segment texts (sentence-like)
            def window_text(prev_ts: float, ts: float) -> str:
                if not segments:
                    return ""
                # Prefer full segment texts that overlap this window
                texts: List[str] = []
                for seg in segments:
                    try:
                        s = seg.get('start'); e = seg.get('end')
                        if s is None or e is None:
                            continue
                        # Overlap: any intersection with (prev_ts, ts]
                        if (s < ts) and (e > prev_ts):
                            t = (seg.get('text') or '').strip()
                            if t:
                                texts.append(t)
                    except Exception:
                        continue
                if texts:
                    return " ".join(texts).strip()
                return ""

            def fmt_hms(seconds: float) -> str:
                try:
                    s = max(0, int(seconds))
                    hh = s // 3600
                    mm = (s % 3600) // 60
                    ss = s % 60
                    return f"{hh:02d}:{mm:02d}:{ss:02d}"
                except Exception:
                    return "00:00:00"

            # Create chunks by matching frames with transcript in (prev_ts, ts]
            prev_ts = 0.0
            seen_text_hashes = set()

            def overlapping_segments(ws: float, we: float) -> List[Dict[str, Any]]:
                res = []
                for seg in segments or []:
                    try:
                        s = seg.get('start'); e = seg.get('end')
                        if s is None or e is None:
                            continue
                        if (s < we) and (e > ws):
                            res.append(seg)
                    except Exception:
                        continue
                return res
            for i, frame_info in enumerate(captioned_frames):
                chunk = {
                    "docnm_kwd": filename,
                    "title_tks": rag_tokenizer.tokenize(re.sub(r"\.[a-zA-Z]+$", "", filename))
                }
                
                # Build non-overlapping transcript for this frame window (prev_ts, ts] or provided window
                if 'window' in frame_info:
                    ws, we = frame_info['window']
                    ts = we
                    segment_text = window_text(ws, we)
                    try:
                        ov = overlapping_segments(ws, we)
                        logger.debug(f"[video.chunk] window={i} [{ws:.2f},{we:.2f}] seg_count={len(ov)} text_len={len(segment_text)} caption={'yes' if frame_info.get('caption') else 'no'}")
                    except Exception:
                        pass
                else:
                    ts = frame_info['timestamp']
                    # Use the previous ts as window start, do not advance prev_ts yet
                    ws, we = prev_ts, ts
                    segment_text = window_text(ws, we)
                    try:
                        ov = overlapping_segments(ws, we)
                        logger.debug(f"[video.chunk] window={i} (prev,{ts:.2f}] seg_count={len(ov)} text_len={len(segment_text)} caption={'yes' if frame_info.get('caption') else 'no'}")
                    except Exception:
                        pass
                
                # Combine transcript and caption for chunk text in required format:
                # [absolute seconds][hr:min:ss] - [hr:min:ss]: [transcript] [caption]
                try:
                    abs_sec = float(frame_info.get('timestamp', ts))
                except Exception:
                    abs_sec = float(ts)
                left_hms = fmt_hms(float(ws))
                right_hms = fmt_hms(float(we))
                cap = frame_info['caption'] if frame_info.get('caption') else 'no caption found'
                chunk_text = f"[{abs_sec:.2f}][{left_hms}] - [{right_hms}]: {segment_text} \n[Caption]:{cap}"
                # Tokenize the combined text
                chunk["title_sm_tks"] = rag_tokenizer.fine_grained_tokenize(chunk["title_tks"])
                tokenize(chunk, chunk_text, lang.lower() == "english")
                
                # Store frame as chunk image (like PDF section layout)
                if 'frame' in frame_info:
                    chunk["image"] = frame_info['frame']
                    chunk["caption"] = cap if cap else ''

                # Store timestamp and window metadata
                try:
                    chunk["timestamp"] = float(abs_sec)
                except Exception:
                    chunk["timestamp"] = 0.0
                try:
                    chunk["ts_start"] = float(ws)
                    chunk["ts_end"] = float(we)
                except Exception:
                    chunk["ts_start"], chunk["ts_end"] = 0.0, chunk["timestamp"]
                chunk["page_num"] = i  # Frame sequence number

                # Append chunk (even if empty transcript, keep caption/frame)
                chunks.append(chunk)
                # Advance the previous window end for the next iteration
                prev_ts = we
            
            callback(1.0, f"Created {len(chunks)} video chunks")
            
        finally:
            # Cleanup temporary file
            if VIDEO_CONFIG['cleanup_temp_files'] and os.path.exists(tmp_video_path):
                os.unlink(tmp_video_path)
                
    except Exception as e:
        logger.error(f"Video processing failed: {e}")
        callback(prog=-1, msg=str(e))
        
        # Fallback: treat as audio-only if video processing fails
        try:
            callback(0.5, "Video processing failed, falling back to audio-only...")
            seq2txt_mdl = LLMBundle(tenant_id, LLMType.SPEECH2TEXT, lang=lang)
            audio_result = seq2txt_mdl.transcription(binary)
            
            # Check if audio transcription also failed
            audio_text = audio_result if isinstance(audio_result, str) else audio_result[0]
            if audio_text.startswith("**ERROR**"):
                raise Exception(f"Audio fallback transcription also failed: {audio_text}")
            
            chunk = {
                "docnm_kwd": filename,
                "title_tks": rag_tokenizer.tokenize(re.sub(r"\.[a-zA-Z]+$", "", filename))
            }
            chunk["title_sm_tks"] = rag_tokenizer.fine_grained_tokenize(chunk["title_tks"])
            tokenize(chunk, audio_text, lang.lower() == "english")
            chunks = [chunk]
            
            callback(1.0, "Audio-only processing complete")
        except Exception as audio_error:
            logger.error(f"Audio fallback also failed: {audio_error}")
            
            # Final fallback: create a basic chunk with file metadata only
            try:
                callback(0.7, "Audio transcription unavailable, creating metadata-only chunk...")
                chunk = {
                    "docnm_kwd": filename,
                    "title_tks": rag_tokenizer.tokenize(re.sub(r"\.[a-zA-Z]+$", "", filename))
                }
                chunk["title_sm_tks"] = rag_tokenizer.fine_grained_tokenize(chunk["title_tks"])
                
                # Create basic content from filename
                basic_content = f"Video file: {filename}\nNote: Audio transcription service is currently unavailable."
                tokenize(chunk, basic_content, lang.lower() == "english")
                chunks = [chunk]
                
                callback(1.0, "Metadata-only processing complete (transcription service unavailable)")
                logger.warning(f"Created metadata-only chunk for {filename} due to transcription service unavailability")
            except Exception as final_error:
                logger.error(f"Final fallback also failed: {final_error}")
                callback(prog=-1, msg=f"All processing methods failed: {final_error}")
    
    return chunks