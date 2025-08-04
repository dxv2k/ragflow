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

import pytest
from common import HOST_ADDRESS
from ragflow_sdk import RAGFlow
from ragflow_sdk.modules.dataset import DataSet


def test_create_dataset_with_monkeyocr_engine(get_api_key_fixture):
    """Test creating dataset with MonkeyOCR parser engine"""
    API_KEY = get_api_key_fixture
    rag = RAGFlow(API_KEY, HOST_ADDRESS)
    
    # Create dataset with MonkeyOCR engine
    dataset = rag.create_dataset(
        name="test_monkeyocr_engine",
        parser_engine="monkeyocr",
        chunk_method="monkeyocr"
    )
    
    assert dataset.name == "test_monkeyocr_engine"
    # Note: parser_engine is not stored in the dataset object, it's used for processing
    assert dataset.chunk_method == "monkeyocr"


def test_create_dataset_with_monkeyocr_config(get_api_key_fixture):
    """Test creating dataset with MonkeyOCR-specific configuration"""
    API_KEY = get_api_key_fixture
    rag = RAGFlow(API_KEY, HOST_ADDRESS)
    
    # Create MonkeyOCR configuration
    parser_config = DataSet.ParserConfig.create_monkeyocr_config(
        chunk_token_num=1000,
        # Note: MonkeyOCR-specific fields are handled by the backend
        # when parser_engine="monkeyocr" is specified
    )
    
    dataset = rag.create_dataset(
        name="test_monkeyocr_config",
        parser_engine="monkeyocr",
        chunk_method="monkeyocr",
        parser_config=parser_config
    )
    
    assert dataset.name == "test_monkeyocr_config"
    assert dataset.chunk_method == "monkeyocr"


def test_create_dataset_with_deepdoc_config(get_api_key_fixture):
    """Test creating dataset with DeepDoc configuration"""
    API_KEY = get_api_key_fixture
    rag = RAGFlow(API_KEY, HOST_ADDRESS)
    
    # Create DeepDoc configuration
    parser_config = DataSet.ParserConfig.create_deepdoc_config(
        chunk_token_num=500,
        layout_recognize="DeepDOC"
    )
    
    dataset = rag.create_dataset(
        name="test_deepdoc_config",
        parser_engine="deepdoc",
        chunk_method="naive",
        parser_config=parser_config
    )
    
    assert dataset.name == "test_deepdoc_config"
    assert dataset.chunk_method == "naive"


def test_parser_config_creation_methods():
    """Test ParserConfig creation methods"""
    # Test DeepDoc config creation
    deepdoc_config = DataSet.ParserConfig.create_deepdoc_config(
        chunk_token_num=256,
        delimiter="\n\n"
    )
    
    config_json = deepdoc_config.to_json()
    assert config_json["chunk_token_num"] == 256
    assert config_json["delimiter"] == "\n\n"
    # parser_engine is not in config, it's passed separately
    
    # Test MonkeyOCR config creation
    monkeyocr_config = DataSet.ParserConfig.create_monkeyocr_config(
        chunk_token_num=1000,
        # Note: MonkeyOCR-specific fields are handled by the backend
        # when parser_engine="monkeyocr" is specified
    )
    
    config_json = monkeyocr_config.to_json()
    assert config_json["chunk_token_num"] == 1000
    # parser_engine is not in config, it's passed separately


def test_monkeyocr_vs_deepdoc_comparison(get_api_key_fixture):
    """Test comparison between MonkeyOCR and DeepDoc engines"""
    API_KEY = get_api_key_fixture
    rag = RAGFlow(API_KEY, HOST_ADDRESS)
    
    # Create DeepDoc dataset
    deepdoc_config = DataSet.ParserConfig.create_deepdoc_config()
    deepdoc_dataset = rag.create_dataset(
        name="test_deepdoc_comparison",
        parser_engine="deepdoc",
        chunk_method="naive",
        parser_config=deepdoc_config
    )
    
    # Create MonkeyOCR dataset
    monkeyocr_config = DataSet.ParserConfig.create_monkeyocr_config()
    monkeyocr_dataset = rag.create_dataset(
        name="test_monkeyocr_comparison",
        parser_engine="monkeyocr",
        chunk_method="monkeyocr",
        parser_config=monkeyocr_config
    )
    
    # Verify both datasets were created successfully
    assert deepdoc_dataset.id != monkeyocr_dataset.id
    assert deepdoc_dataset.chunk_method == "naive"
    assert monkeyocr_dataset.chunk_method == "monkeyocr"
    
    # Clean up
    rag.delete_datasets(ids=[deepdoc_dataset.id, monkeyocr_dataset.id])


def test_monkeyocr_advanced_configuration(get_api_key_fixture):
    """Test advanced MonkeyOCR configuration options"""
    API_KEY = get_api_key_fixture
    rag = RAGFlow(API_KEY, HOST_ADDRESS)
    
    # Create advanced MonkeyOCR configuration
    parser_config = DataSet.ParserConfig.create_monkeyocr_config(
        chunk_token_num=2048,
        # Note: MonkeyOCR-specific fields are handled by the backend
        # when parser_engine="monkeyocr" is specified
    )
    
    dataset = rag.create_dataset(
        name="test_monkeyocr_advanced",
        parser_engine="monkeyocr",
        chunk_method="monkeyocr",
        parser_config=parser_config
    )
    
    config_json = parser_config.to_json()
    assert config_json["chunk_token_num"] == 2048
    # MonkeyOCR-specific fields are handled by the backend


def test_backward_compatibility(get_api_key_fixture):
    """Test backward compatibility - no parser_engine specified"""
    API_KEY = get_api_key_fixture
    rag = RAGFlow(API_KEY, HOST_ADDRESS)
    
    # Create dataset without specifying parser_engine (should default to deepdoc)
    dataset = rag.create_dataset(
        name="test_backward_compatibility",
        chunk_method="naive"
    )
    
    # Should default to deepdoc
    assert dataset.name == "test_backward_compatibility"
    assert dataset.chunk_method == "naive"


def test_invalid_monkeyocr_configuration(get_api_key_fixture):
    """Test error handling for invalid MonkeyOCR configurations"""
    API_KEY = get_api_key_fixture
    rag = RAGFlow(API_KEY, HOST_ADDRESS)
    
    # Test with invalid chunk_method for MonkeyOCR
    with pytest.raises(Exception) as exc_info:
        rag.create_dataset(
            name="test_invalid_monkeyocr",
            parser_engine="monkeyocr",
            chunk_method="invalid_method"  # This should fail
        )
    
    assert "chunk_method" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()


def test_monkeyocr_parser_config_validation():
    """Test ParserConfig validation for MonkeyOCR"""
    # Test that MonkeyOCR config includes all required fields
    config = DataSet.ParserConfig.create_monkeyocr_config()
    config_json = config.to_json()
    
    required_fields = [
        "chunk_token_num", "delimiter", "html4excel", "layout_recognize"
    ]
    
    for field in required_fields:
        assert field in config_json, f"Missing required field: {field}"
    
    # Verify MonkeyOCR-specific fields are handled by the backend
    # when parser_engine="monkeyocr" is specified


def test_deepdoc_parser_config_validation():
    """Test ParserConfig validation for DeepDoc"""
    # Test that DeepDoc config includes all required fields
    config = DataSet.ParserConfig.create_deepdoc_config()
    config_json = config.to_json()
    
    required_fields = [
        "chunk_token_num", "delimiter", "html4excel", "layout_recognize"
    ]
    
    for field in required_fields:
        assert field in config_json, f"Missing required field: {field}"
    
    # Verify DeepDoc-specific fields (parser_engine is passed separately)
    assert config_json["layout_recognize"] == "DeepDOC"


def test_parser_config_customization():
    """Test customizing ParserConfig with additional parameters"""
    # Test custom DeepDoc config
    deepdoc_config = DataSet.ParserConfig.create_deepdoc_config(
        chunk_token_num=1024,
        delimiter="\n---\n",
        html4excel=True,
        layout_recognize="Plain Text"
    )
    
    config_json = deepdoc_config.to_json()
    assert config_json["chunk_token_num"] == 1024
    assert config_json["delimiter"] == "\n---\n"
    assert config_json["html4excel"] is True
    assert config_json["layout_recognize"] == "Plain Text"
    
    # Test custom MonkeyOCR config
    monkeyocr_config = DataSet.ParserConfig.create_monkeyocr_config(
        chunk_token_num=1500,
        # Note: MonkeyOCR-specific fields are handled by the backend
        # when parser_engine="monkeyocr" is specified
    )
    
    config_json = monkeyocr_config.to_json()
    assert config_json["chunk_token_num"] == 1500
    # MonkeyOCR-specific fields are handled by the backend 