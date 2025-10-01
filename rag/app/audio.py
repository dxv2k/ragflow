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
import json
import tempfile
import os

from api.db import LLMType
from rag.nlp import rag_tokenizer
from api.db.services.llm_service import LLMBundle, TenantLLMService
from rag.nlp import tokenize


def chunk(filename, binary, tenant_id, lang, callback=None, **kwargs):
    doc = {
        "docnm_kwd": filename,
        "title_tks": rag_tokenizer.tokenize(re.sub(r"\.[a-zA-Z]+$", "", filename))
    }
    doc["title_sm_tks"] = rag_tokenizer.fine_grained_tokenize(doc["title_tks"])

    # is it English
    eng = lang.lower() == "english"  # is_english(sections)
    try:
        callback(0.1, "USE Sequence2Txt LLM to transcription the audio")
        
        # Check if WhisperX is being used
        model_config = TenantLLMService.get_model_config(tenant_id, LLMType.SPEECH2TEXT)
        is_whisperx = model_config.get("llm_factory") == "WhisperX"
        
        if is_whisperx:
            callback(0.2, "Using WhisperX for transcription with speaker diarization")
            # Use WhisperX and get JSON structure
            seq2txt_mdl = LLMBundle(tenant_id, LLMType.SPEECH2TEXT, lang=lang)
            
            # Get the actual WhisperX model instance
            whisperx_model = seq2txt_mdl.mdl
            
            # Create temporary file for WhisperX (it expects file paths)
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(binary)
                temp_file_path = temp_file.name
            
            try:
                # Get WhisperX API instance
                whisperx_api = whisperx_model._get_whisperx_api()
                
                # Configure for JSON output
                transcription_config = {
                    'model_name': whisperx_model.whisperx_model,
                    'language': 'auto' if lang.lower() == 'chinese' else lang.lower(),
                    'enable_diarization': whisperx_model.enable_diarization,
                    'min_speakers': whisperx_model.min_speakers,
                    'max_speakers': whisperx_model.max_speakers,
                    'initial_prompt': whisperx_model.initial_prompt,
                    'condition_on_previous_text': whisperx_model.condition_on_previous_text,
                    'output_formats': ['json'],
                }
                
                callback(0.5, "WhisperX processing audio with speaker diarization...")
                
                # Get raw WhisperX result
                result = whisperx_api.transcribe_file(temp_file_path, **transcription_config)
                
                if result and result.segments:
                    # Convert to JSON structure matching our test.json format
                    json_data = {
                        "segments": [
                            {
                                "start": seg.start,
                                "end": seg.end,
                                "text": seg.text,
                                "speaker": seg.speaker,
                                "words": seg.words or []
                            }
                            for seg in result.segments
                        ],
                        "word_segments": []
                    }
                    
                    # Also create word_segments array
                    for seg in result.segments:
                        if seg.words:
                            json_data["word_segments"].extend(seg.words)
                    
                    # Save as JSON string to content_with_weight
                    json_content = json.dumps(json_data, ensure_ascii=False)
                    
                    callback(0.8, f"WhisperX completed: {len(result.segments)} segments with speakers")
                    
                    # Set the JSON content directly instead of using tokenize
                    doc["content_with_weight"] = json_content
                    doc["content_ltks"] = rag_tokenizer.tokenize(result.get_full_text(include_speakers=False))
                    doc["content_sm_ltks"] = rag_tokenizer.fine_grained_tokenize(doc["content_ltks"])
                    
                    return [doc]
                else:
                    callback(prog=-1, msg="WhisperX: No transcription generated")
                    return []
                    
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass
        else:
            # Use traditional approach for non-WhisperX models
            seq2txt_mdl = LLMBundle(tenant_id, LLMType.SPEECH2TEXT, lang=lang)
            ans = seq2txt_mdl.transcription(binary)
            callback(0.8, "Sequence2Txt LLM respond: %s ..." % ans[:32])
            tokenize(doc, ans, eng)
            return [doc]
            
    except Exception as e:
        callback(prog=-1, msg=str(e))

    return []
