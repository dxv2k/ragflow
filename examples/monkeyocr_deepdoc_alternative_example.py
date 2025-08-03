#!/usr/bin/env python3
"""
MonkeyOCR as DeepDoc Alternative - Usage Examples

This example demonstrates how to use the new parser_engine parameter
to choose between DeepDoc and MonkeyOCR as processing engines.

Requirements:
- RAGFlow SDK installed
- RAGFlow server running
- Valid API key configured
"""

import os
import sys
from pathlib import Path

# Add the SDK to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "sdk" / "python"))

from ragflow_sdk import RAGFlow


def setup_client():
    """Setup RAGFlow client with API key"""
    # Get API key from environment or use default
    api_key = os.getenv("RAGFLOW_API_KEY", "your-api-key-here")
    base_url = os.getenv("RAGFLOW_BASE_URL", "http://localhost:9380")
    
    return RAGFlow(api_key=api_key, base_url=base_url)


def example_deepdoc_processing():
    """Example: Using DeepDoc as the processing engine (default)"""
    print("=" * 60)
    print("EXAMPLE 1: DeepDoc Processing Engine")
    print("=" * 60)
    
    client = setup_client()
    
    try:
        # Create dataset with DeepDoc engine (default)
        dataset = client.create_dataset(
            name="DeepDoc Example Dataset",
            description="Testing DeepDoc processing engine",
            parser_engine="deepdoc",  # Explicitly specify DeepDoc
            chunk_method="naive",
            chunk_size=500,
            chunk_overlap=50
        )
        
        print(f"✅ Created dataset with DeepDoc engine:")
        print(f"   Dataset ID: {dataset.id}")
        print(f"   Name: {dataset.name}")
        print(f"   Parser Engine: {dataset.parser_config.get('parser_engine', 'deepdoc')}")
        print(f"   Parser ID: {dataset.parser_id}")
        
        # Upload a document
        document_path = "path/to/your/document.pdf"
        if os.path.exists(document_path):
            doc = client.upload_document(
                dataset_id=dataset.id,
                file_path=document_path
            )
            print(f"✅ Uploaded document: {doc.name}")
        else:
            print(f"⚠️  Document not found: {document_path}")
            
    except Exception as e:
        print(f"❌ Error with DeepDoc processing: {e}")


def example_monkeyocr_processing():
    """Example: Using MonkeyOCR as the processing engine"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: MonkeyOCR Processing Engine")
    print("=" * 60)
    
    client = setup_client()
    
    try:
        # Create dataset with MonkeyOCR engine
        dataset = client.create_dataset(
            name="MonkeyOCR Example Dataset",
            description="Testing MonkeyOCR processing engine",
            parser_engine="monkeyocr",  # Use MonkeyOCR engine
            chunk_method="monkeyocr",   # Use MonkeyOCR chunking method
            chunk_size=500,
            chunk_overlap=50
        )
        
        print(f"✅ Created dataset with MonkeyOCR engine:")
        print(f"   Dataset ID: {dataset.id}")
        print(f"   Name: {dataset.name}")
        print(f"   Parser Engine: {dataset.parser_config.get('parser_engine', 'monkeyocr')}")
        print(f"   Parser ID: {dataset.parser_id}")
        
        # Upload a document
        document_path = "path/to/your/document.pdf"
        if os.path.exists(document_path):
            doc = client.upload_document(
                dataset_id=dataset.id,
                file_path=document_path
            )
            print(f"✅ Uploaded document: {doc.name}")
        else:
            print(f"⚠️  Document not found: {document_path}")
            
    except Exception as e:
        print(f"❌ Error with MonkeyOCR processing: {e}")


def example_backward_compatibility():
    """Example: Backward compatibility - no parser_engine specified"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Backward Compatibility")
    print("=" * 60)
    
    client = setup_client()
    
    try:
        # Create dataset without specifying parser_engine (uses default)
        dataset = client.create_dataset(
            name="Backward Compatible Dataset",
            description="Testing backward compatibility",
            # parser_engine not specified - defaults to "deepdoc"
            chunk_method="naive",
            chunk_size=500,
            chunk_overlap=50
        )
        
        print(f"✅ Created dataset with default engine:")
        print(f"   Dataset ID: {dataset.id}")
        print(f"   Name: {dataset.name}")
        print(f"   Parser Engine: {dataset.parser_config.get('parser_engine', 'deepdoc')}")
        print(f"   Parser ID: {dataset.parser_id}")
        
    except Exception as e:
        print(f"❌ Error with backward compatibility test: {e}")


def example_advanced_configuration():
    """Example: Advanced configuration with custom parser settings"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Advanced Configuration")
    print("=" * 60)
    
    client = setup_client()
    
    try:
        # Create dataset with advanced configuration
        dataset = client.create_dataset(
            name="Advanced MonkeyOCR Dataset",
            description="Testing advanced MonkeyOCR configuration",
            parser_engine="monkeyocr",
            chunk_method="monkeyocr",
            chunk_size=1000,
            chunk_overlap=100,
            parser_config={
                "parser_engine": "monkeyocr",
                "mode": "full",  # full, parse_only, ocr_only
                "split_pages": False,
                "extract_images": True,
                "generate_layout_pdf": True,
                "auto_keywords": 3,  # Generate 3 keywords per chunk
                "auto_questions": 2  # Generate 2 questions per chunk
            }
        )
        
        print(f"✅ Created dataset with advanced configuration:")
        print(f"   Dataset ID: {dataset.id}")
        print(f"   Name: {dataset.name}")
        print(f"   Parser Engine: {dataset.parser_config.get('parser_engine')}")
        print(f"   Mode: {dataset.parser_config.get('mode')}")
        print(f"   Auto Keywords: {dataset.parser_config.get('auto_keywords')}")
        print(f"   Auto Questions: {dataset.parser_config.get('auto_questions')}")
        
    except Exception as e:
        print(f"❌ Error with advanced configuration: {e}")


def example_api_comparison():
    """Example: Comparing API responses between engines"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: API Response Comparison")
    print("=" * 60)
    
    client = setup_client()
    
    try:
        # Create datasets with different engines
        deepdoc_dataset = client.create_dataset(
            name="DeepDoc Comparison",
            parser_engine="deepdoc",
            chunk_method="naive"
        )
        
        monkeyocr_dataset = client.create_dataset(
            name="MonkeyOCR Comparison",
            parser_engine="monkeyocr",
            chunk_method="monkeyocr"
        )
        
        print("📊 Dataset Configuration Comparison:")
        print(f"{'Field':<20} {'DeepDoc':<15} {'MonkeyOCR':<15}")
        print("-" * 50)
        print(f"{'Parser Engine':<20} {deepdoc_dataset.parser_config.get('parser_engine', 'deepdoc'):<15} {monkeyocr_dataset.parser_config.get('parser_engine', 'monkeyocr'):<15}")
        print(f"{'Parser ID':<20} {deepdoc_dataset.parser_id:<15} {monkeyocr_dataset.parser_id:<15}")
        print(f"{'Chunk Method':<20} {deepdoc_dataset.chunk_method:<15} {monkeyocr_dataset.chunk_method:<15}")
        
        # Clean up
        client.delete_dataset(deepdoc_dataset.id)
        client.delete_dataset(monkeyocr_dataset.id)
        print("\n✅ Comparison datasets cleaned up")
        
    except Exception as e:
        print(f"❌ Error with API comparison: {e}")


def main():
    """Run all examples"""
    print("🚀 MonkeyOCR as DeepDoc Alternative - Usage Examples")
    print("=" * 60)
    
    # Check if client can be set up
    try:
        client = setup_client()
        print("✅ RAGFlow client setup successful")
    except Exception as e:
        print(f"❌ Failed to setup RAGFlow client: {e}")
        print("Please check your API key and server connection")
        return
    
    # Run examples
    example_deepdoc_processing()
    example_monkeyocr_processing()
    example_backward_compatibility()
    example_advanced_configuration()
    example_api_comparison()
    
    print("\n" + "=" * 60)
    print("🎉 All examples completed!")
    print("=" * 60)
    print("\nKey Points:")
    print("• Use parser_engine='deepdoc' for DeepDoc processing (default)")
    print("• Use parser_engine='monkeyocr' for MonkeyOCR processing")
    print("• Both engines support the same API interface")
    print("• Backward compatibility is maintained")
    print("• Advanced configuration available via parser_config")


if __name__ == "__main__":
    main()