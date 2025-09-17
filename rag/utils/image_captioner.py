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

import openai
import base64
import logging
from typing import List, Dict, Any
import cv2
import numpy as np
from PIL import Image
import io

logger = logging.getLogger(__name__)


class ImageCaptioner:
    """
    Image captioning using GPT-5-nano with original video-captioning prompts.
    Optimized for production use with batching and error handling.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-5-nano-2025-08-07"):
        """
        Initialize OpenAI client with GPT-5-nano.
        
        Args:
            api_key: OpenAI API key
            model: Model name (default: gpt-5-nano-2025-08-07)
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        logger.info(f"Initialized OpenAI client with model: {model}")
    
    def encode_image_to_base64(self, image: np.ndarray, quality: int = 85) -> str:
        """
        Convert OpenCV image to base64 string with quality control.
        
        Args:
            image: OpenCV image (numpy array)
            quality: JPEG quality (1-100)
        
        Returns:
            Base64 encoded image string
        """
        try:
            # Encode with quality control for smaller payloads
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            _, buffer = cv2.imencode('.jpg', image, encode_param)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            return image_base64
        except Exception as e:
            logger.error(f"Image encoding failed: {e}")
            raise
    
    def caption_single_image(self, image: np.ndarray, context: str = "") -> str:
        """
        Generate caption for a single image using original prompts.
        
        Args:
            image: OpenCV image (numpy array)
            context: Optional transcript context
        
        Returns:
            Generated caption string
        """
        try:
            image_base64 = self.encode_image_to_base64(image)
            
            # Original prompts preserved from video-captioning
            prompt = "Provide a brief 1-sentence summary of this meeting moment."
            
            if context:
                prompt += f"\nTranscript: {context}"
            
            prompt += "\nFocus on: WHO is doing WHAT and key discussion points"
            prompt += "\nKeep it under 15 words. Be specific about actions and topics. Must use same language as the transcript."
            
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": prompt},
                            {
                                "type": "input_image",
                                "image_url": f"data:image/jpeg;base64,{image_base64}",
                            },
                        ],
                    }
                ],
            )
            
            caption = response.output_text
            logger.debug(f"Generated caption: {caption[:100]}")
            return caption
            
        except Exception as e:
            logger.error(f"Single image captioning failed: {e}")
            return f"Error generating caption: {str(e)}"
    
    def caption_multiple_images(self, images: List[np.ndarray], context: str = "") -> str:
        """
        Generate caption for multiple images as a sequence.
        
        Args:
            images: List of OpenCV images
            context: Optional transcript context
        
        Returns:
            Generated caption string
        """
        try:
            # Limit to 10 images for API constraints
            if len(images) > 10:
                logger.warning(f"Too many images ({len(images)}), taking first 10")
                images = images[:10]
            
            # Original multi-frame prompt preserved
            content_parts = [
                {
                    "type": "input_text",
                    "text": (
                        f"Provide a brief 1-sentence summary of this {len(images)}-frame meeting segment.\n"
                        f"{context if context else ''}\n"
                        "Focus on: WHO is doing WHAT, main discussion points, key actions taken.\n"
                        "Keep under 20 words. Be specific and action-oriented."
                    ),
                }
            ]
            
            # Add images with reduced quality for faster processing
            for image in images:
                image_base64 = self.encode_image_to_base64(image, quality=75)
                content_parts.append(
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{image_base64}",
                    }
                )
            
            response = self.client.responses.create(
                model=self.model,
                input=[{"role": "user", "content": content_parts}],
            )
            
            caption = response.output_text
            logger.debug(f"Generated batch caption for {len(images)} images")
            return caption
            
        except Exception as e:
            logger.error(f"Multi-image captioning failed: {e}")
            return f"Error generating caption: {str(e)}"
    
    def process_frame_batch(self, frames: List[Dict[str, Any]], 
                          batch_size: int = 3,
                          transcript_segments: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Process frames in batches for captioning with transcript context.
        
        Args:
            frames: List of frame data with 'timestamp' and 'image'
            batch_size: Number of frames to process together (default: 3)
            transcript_segments: Optional transcript segments with 'start', 'end', 'text'
        
        Returns:
            List of dictionaries with timestamp, caption, and frame
        """
        captioned_frames = []
        
        def get_transcript_context(timestamp: float, window_seconds: float = 5.0) -> str:
            """Get relevant transcript text around a timestamp."""
            if not transcript_segments:
                return ""
            
            context_segments = []
            for segment in transcript_segments:
                # Include segments that overlap with timestamp window
                if (segment.get('start', 0) <= timestamp + window_seconds and 
                    segment.get('end', float('inf')) >= timestamp - window_seconds):
                    context_segments.append(segment.get('text', ''))
            
            return " ".join(context_segments).strip() if context_segments else ""
        
        total_frames = len(frames)
        processed = 0
        
        try:
            for i in range(0, total_frames, batch_size):
                batch = frames[i:i + batch_size]
                
                if len(batch) == 1:
                    # Single frame
                    frame_data = batch[0]
                    transcript_context = get_transcript_context(frame_data['timestamp'])
                    
                    caption = self.caption_single_image(
                        frame_data['image'], 
                        transcript_context
                    )
                    
                    captioned_frames.append({
                        'timestamp': frame_data['timestamp'],
                        'caption': caption,
                        'frame': frame_data['image']
                    })
                else:
                    # Multiple frames - batch processing
                    images = [frame_data['image'] for frame_data in batch]
                    timestamps = [frame_data['timestamp'] for frame_data in batch]
                    
                    # Get context for batch time range
                    avg_timestamp = sum(timestamps) / len(timestamps)
                    transcript_context = get_transcript_context(avg_timestamp, window_seconds=10.0)
                    
                    batch_caption = self.caption_multiple_images(images, transcript_context)
                    
                    # Apply same caption to all frames in batch
                    for frame_data in batch:
                        captioned_frames.append({
                            'timestamp': frame_data['timestamp'],
                            'caption': batch_caption,
                            'frame': frame_data['image']
                        })
                
                processed += len(batch)
                
                # Progress logging
                if processed % 10 == 0 or processed == total_frames:
                    logger.info(f"Processed {processed}/{total_frames} frames")
            
            logger.info(f"Caption generation complete: {len(captioned_frames)} frames")
            return captioned_frames
            
        except Exception as e:
            logger.error(f"Frame batch processing failed: {e}")
            
            # Return frames with fallback captions
            for frame_data in frames[len(captioned_frames):]:
                captioned_frames.append({
                    'timestamp': frame_data['timestamp'],
                    'caption': f"Frame at {frame_data['timestamp']:.1f}s",
                    'frame': frame_data.get('image')
                })
            
            return captioned_frames