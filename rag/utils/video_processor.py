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

import cv2
import os
import numpy as np
from typing import List, Tuple, Optional
import logging
import gc

logger = logging.getLogger(__name__)


class VideoProcessor:
    """
    Production-optimized video processor for RAGFlow.
    Handles frame extraction with memory efficiency for large videos.
    """
    
    def __init__(self, video_path: str, max_resolution: Tuple[int, int] = (1280, 720)):
        """
        Initialize video processor with production optimizations.
        
        Args:
            video_path: Path to the video file
            max_resolution: Maximum resolution for processing (width, height)
        """
        self.video_path = video_path
        self.max_resolution = max_resolution
        self.cap = cv2.VideoCapture(video_path)
        
        if not self.cap.isOpened():
            raise ValueError(f"Failed to open video: {video_path}")
        
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.total_frames / self.fps if self.fps > 0 else 0
        self.original_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.original_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Calculate downsampling factor
        self.scale_factor = min(
            max_resolution[0] / self.original_width,
            max_resolution[1] / self.original_height,
            1.0  # Don't upscale
        )
        
        self.target_width = int(self.original_width * self.scale_factor)
        self.target_height = int(self.original_height * self.scale_factor)
        
        logger.info(f"Initialized video processor: {self.duration:.1f}s, {self.fps:.1f}fps")
        logger.info(f"Resolution: {self.original_width}x{self.original_height} -> {self.target_width}x{self.target_height}")
    
    def _resize_frame(self, frame: np.ndarray) -> np.ndarray:
        """Resize frame to target resolution for memory efficiency."""
        if self.scale_factor < 1.0:
            return cv2.resize(frame, (self.target_width, self.target_height), 
                            interpolation=cv2.INTER_AREA)
        return frame
    
    def extract_frames_at_timestamps(self, timestamps: List[float], 
                                    buffer_size: int = 10) -> List[Tuple[float, np.ndarray]]:
        """
        Extract frames at specific timestamps with memory management.
        
        Args:
            timestamps: List of timestamps in seconds
            buffer_size: Maximum frames to keep in memory at once
        
        Returns:
            List of (timestamp, frame) tuples
        """
        frames = []
        processed_count = 0
        
        try:
            for i, timestamp in enumerate(timestamps):
                # Memory management: clear buffer periodically
                if processed_count >= buffer_size:
                    gc.collect()
                    processed_count = 0
                
                frame_num = int(timestamp * self.fps)
                
                # Bounds checking
                if frame_num >= self.total_frames:
                    logger.warning(f"Timestamp {timestamp:.2f}s beyond video duration")
                    continue
                
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                ret, frame = self.cap.read()
                
                if ret and frame is not None:
                    # Resize frame for memory efficiency
                    frame = self._resize_frame(frame)
                    frames.append((timestamp, frame))
                    processed_count += 1
                    
                    if (i + 1) % 10 == 0:
                        logger.info(f"Extracted {i + 1}/{len(timestamps)} frames")
                else:
                    logger.warning(f"Failed to extract frame at {timestamp:.2f}s")
            
            logger.info(f"Successfully extracted {len(frames)} frames")
            return frames
            
        except Exception as e:
            logger.error(f"Frame extraction failed: {e}")
            # Return what we have so far
            return frames
    
    def extract_frames_at_interval(self, interval_seconds: float = 5.0,
                                  max_frames: int = 100) -> List[Tuple[float, np.ndarray]]:
        """
        Extract frames at fixed intervals with frame limit.
        
        Args:
            interval_seconds: Interval between frames in seconds
            max_frames: Maximum number of frames to extract
        
        Returns:
            List of (timestamp, frame) tuples
        """
        frames = []
        interval_frames = int(interval_seconds * self.fps)
        
        if interval_frames == 0:
            interval_frames = 1
        
        frame_count = 0
        extracted = 0
        
        try:
            while frame_count < self.total_frames and extracted < max_frames:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count)
                ret, frame = self.cap.read()
                
                if ret and frame is not None:
                    timestamp = frame_count / self.fps
                    frame = self._resize_frame(frame)
                    frames.append((timestamp, frame))
                    extracted += 1
                    
                    if extracted % 10 == 0:
                        logger.info(f"Extracted {extracted} frames at {timestamp:.1f}s")
                        gc.collect()  # Periodic memory cleanup
                
                frame_count += interval_frames
            
            logger.info(f"Extracted {len(frames)} frames at {interval_seconds}s intervals")
            return frames
            
        except Exception as e:
            logger.error(f"Interval extraction failed: {e}")
            return frames
    
    def extract_keyframes(self, threshold: float = 0.3, 
                         min_interval: float = 2.0,
                         max_frames: int = 50) -> List[Tuple[float, np.ndarray]]:
        """
        Extract keyframes using scene change detection.
        
        Args:
            threshold: Scene change threshold (0-1)
            min_interval: Minimum interval between keyframes in seconds
            max_frames: Maximum number of keyframes to extract
        
        Returns:
            List of (timestamp, frame) tuples
        """
        keyframes = []
        prev_frame = None
        last_keyframe_time = -min_interval
        frame_count = 0
        
        try:
            # Reset to beginning
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            while len(keyframes) < max_frames:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                timestamp = frame_count / self.fps
                frame_count += 1
                
                # Skip if too close to last keyframe
                if timestamp - last_keyframe_time < min_interval:
                    continue
                
                # Resize for processing
                frame_resized = self._resize_frame(frame)
                gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
                
                if prev_frame is not None:
                    # Calculate scene change metric
                    diff = cv2.absdiff(prev_frame, gray)
                    mean_diff = np.mean(diff) / 255.0
                    
                    if mean_diff > threshold:
                        keyframes.append((timestamp, frame_resized))
                        last_keyframe_time = timestamp
                        logger.info(f"Keyframe at {timestamp:.2f}s (diff: {mean_diff:.3f})")
                        
                        # Memory management
                        if len(keyframes) % 10 == 0:
                            gc.collect()
                else:
                    # Always include first frame
                    keyframes.append((timestamp, frame_resized))
                    last_keyframe_time = timestamp
                
                prev_frame = gray
            
            logger.info(f"Extracted {len(keyframes)} keyframes")
            return keyframes
            
        except Exception as e:
            logger.error(f"Keyframe extraction failed: {e}")
            return keyframes
    
    def get_thumbnail(self, timestamp: float = 0.0, size: Tuple[int, int] = (320, 240)) -> Optional[np.ndarray]:
        """
        Get a thumbnail at specific timestamp.
        
        Args:
            timestamp: Timestamp in seconds
            size: Thumbnail size (width, height)
        
        Returns:
            Thumbnail frame or None
        """
        try:
            frame_num = int(timestamp * self.fps)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = self.cap.read()
            
            if ret and frame is not None:
                thumbnail = cv2.resize(frame, size, interpolation=cv2.INTER_AREA)
                return thumbnail
            
        except Exception as e:
            logger.error(f"Thumbnail extraction failed: {e}")
        
        return None
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'cap') and self.cap is not None:
            self.cap.release()
            logger.debug("Released video capture resources")