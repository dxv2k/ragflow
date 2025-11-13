"""High-level API for the transcription backend."""

import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List

from .models import ProcessingConfig, TranscriptionResult
from .core import ProcessingOrchestrator
from .utils import FileManager, CacheManager
from .logger import get_whisperx_logger

logger = get_whisperx_logger(__name__)


class TranscriptionAPI:
    """High-level API for audio transcription."""
    
    def __init__(self, output_dir: str = "./outputs", openai_api_key: Optional[str] = None, openai_api_base: Optional[str] = "https://llm-proxy.viact.net", hf_token: Optional[str] = None):
        # Debug logging for HF token tracing
        logger.info(f"🔍 TranscriptionAPI.__init__: hf_token = '{hf_token[:20] + '...' if hf_token and len(hf_token) > 20 else hf_token}' (length: {len(hf_token) if hf_token else 0})")
        
        self.cache_manager = CacheManager()
        self.file_manager = FileManager(output_dir)
        self.orchestrator = ProcessingOrchestrator(self.cache_manager, openai_api_key, openai_api_base, hf_token)
        
        logger.info("TranscriptionAPI initialized")
        logger.info(f"🔍 TranscriptionAPI.__init__: ProcessingOrchestrator initialized with hf_token")
    
    def transcribe_file(self, file_path: str, **kwargs) -> TranscriptionResult:
        """
        Transcribe a single audio file.
        
        Args:
            file_path: Path to the audio file
            **kwargs: Configuration options (language, model_name, hf_token, etc.)
        
        Returns:
            TranscriptionResult with transcription data
        """
        # Extract hf_token from kwargs if provided, otherwise use instance token
        hf_token = kwargs.pop('hf_token', None) or getattr(self.orchestrator, 'hf_token', None)
        logger.info(f"🔍 TranscriptionAPI.transcribe_file: extracted hf_token = '{hf_token[:20] + '...' if hf_token and len(hf_token) > 20 else hf_token}' (length: {len(hf_token) if hf_token else 0})")
        logger.info(f"🔍 TranscriptionAPI.transcribe_file: orchestrator.hf_token = '{getattr(self.orchestrator, 'hf_token', None)[:20] + '...' if getattr(self.orchestrator, 'hf_token', None) and len(getattr(self.orchestrator, 'hf_token', None)) > 20 else getattr(self.orchestrator, 'hf_token', None)}'")
        
        config = ProcessingConfig(**kwargs)
        return asyncio.run(self.orchestrator.process_audio(file_path, config, hf_token=hf_token))
    
    def transcribe_and_save(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Transcribe file and save results to disk.
        
        Args:
            file_path: Path to the audio file
            **kwargs: Configuration options (hf_token, etc.)
        
        Returns:
            Dictionary with result and file paths
        """
        # Extract hf_token from kwargs if provided, otherwise use instance token
        hf_token = kwargs.pop('hf_token', None) or getattr(self.orchestrator, 'hf_token', None)
        openai_api_base = kwargs.pop('openai_api_base', None)
        api = TranscriptionAPI(hf_token=hf_token, openai_api_base=openai_api_base)
        return api.transcribe_and_save(file_path, **kwargs)


def transcribe_audio(file_path: str, **kwargs) -> TranscriptionResult:
    """
    Quick transcription function.
    
    Example:
        result = transcribe_audio("audio.mp3", language="en", enable_llm_correction=True, hf_token="hf_xxx", openai_api_base="https://api.openai.com/v1")
    """
    hf_token = kwargs.pop('hf_token', None)
    openai_api_base = kwargs.pop('openai_api_base', None)
    api = TranscriptionAPI(hf_token=hf_token, openai_api_base=openai_api_base)
    return api.transcribe_file(file_path, **kwargs)


def transcribe_and_save(file_path: str, **kwargs) -> Dict[str, Any]:
    """
    Quick transcription and save function.
    
    Example:
        result = transcribe_and_save("audio.mp3", output_formats=["txt", "srt"], hf_token="hf_xxx", openai_api_base="https://api.openai.com/v1")
    """
    hf_token = kwargs.pop('hf_token', None)
    openai_api_base = kwargs.pop('openai_api_base', None)
    api = TranscriptionAPI(hf_token=hf_token, openai_api_base=openai_api_base)
    return api.transcribe_and_save(file_path, **kwargs)