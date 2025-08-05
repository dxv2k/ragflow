# MonkeyOCR Integration with RAGFlow

## Overview

This document describes the integration of MonkeyOCR parser with RAGFlow for enhanced document processing capabilities. MonkeyOCR provides advanced OCR and document analysis features for PDF and image files.

## Features

- **Supported Formats**: PDF, JPG, JPEG, PNG, TIFF, BMP
- **Standard RAGFlow Configuration**: Uses existing `parser_config` fields
- **Advanced OCR**: Text extraction with layout preservation
- **Form Recognition**: OMR (Optical Mark Recognition) for forms
- **Enhanced Output**: Markdown with structured content

## Architecture

### Integration Points

1. **File Type Detection**: `api/utils/file_utils.py`
2. **Parser Assignment**: `api/db/services/file_service.py`
3. **Document Processing**: `api/db/services/document_service.py`
4. **API Endpoints**: `api/apps/document_app.py`
5. **Parser Implementation**: `rag/app/monkey_ocr_parser.py`

### File Flow

```
File Upload → File Type Detection → Parser Assignment → MonkeyOCR Processing → Chunk Generation → Storage
```

## Configuration

### Standard RAGFlow Configuration

MonkeyOCR uses the same configuration fields as other RAGFlow parsers:

```python
parser_config = {
    "chunk_token_num": 4096,
    "delimiter": "\n!?;。；！？", 
    "layout_recognize": "MonkeyOCR"  # This field identifies MonkeyOCR processing
}
```

### Parser Switching

To switch between parsers, simply change the `parser_id` field:

- `"parser_id": "naive"` - Default text parser
- `"parser_id": "picture"` - Image parser  
- `"parser_id": "monkeyocr"` - MonkeyOCR parser
- `"parser_id": "presentation"` - Presentation parser

## API Endpoints

### Change Parser

```http
POST /document/change_parser
Content-Type: application/json

{
    "doc_id": "document_id",
    "parser_id": "monkeyocr",
    "parser_config": {
        "chunk_token_num": 4096,
        "delimiter": "\n!?;。；！？",
        "layout_recognize": "MonkeyOCR"
    }
}
```

### Upload Document with MonkeyOCR

```http
POST /document/upload
Content-Type: multipart/form-data

{
    "file": "document.pdf",
    "kb_id": "knowledgebase_id"
}
```

Files supported by MonkeyOCR will automatically be assigned the MonkeyOCR parser.

## Implementation Details

### File Type Detection

```python
def is_monkeyocr_supported(filename):
    """Check if file format is supported by MonkeyOCR parser"""
    filename = filename.lower()
    if re.match(r".*\.(pdf|jpg|jpeg|png|tiff|bmp)$", filename):
        return True
    return False
```

### Parser Assignment

```python
def get_parser(doc_type, filename, default):
    # Check if file is supported by MonkeyOCR
    if is_monkeyocr_supported(filename):
        return ParserType.MONKEYOCR.value
    return default
```

### Processing Pipeline

1. **File Upload**: Files are uploaded through standard RAGFlow endpoints
2. **Type Detection**: System automatically detects MonkeyOCR-supported formats
3. **Parser Assignment**: MonkeyOCR parser is assigned for supported files
4. **Processing**: Document is processed using MonkeyOCR with cedd_parse flow
5. **Chunking**: Content is converted to RAGFlow chunk format
6. **Storage**: Chunks are stored in the knowledge base

## Usage Examples

### Upload PDF with MonkeyOCR

```python
# File upload will automatically use MonkeyOCR for PDF files
files = [('file', open('document.pdf', 'rb'))]
response = requests.post('/document/upload', files=files, data={'kb_id': 'kb_id'})
```

### Change Parser to MonkeyOCR

```python
response = requests.post('/document/change_parser', json={
    'doc_id': 'doc_id',
    'parser_id': 'monkeyocr',
    'parser_config': {
        'chunk_token_num': 4096,
        'delimiter': '\n!?;。；！？',
        'layout_recognize': 'MonkeyOCR'
    }
})
```

### Change Parser Back to Default

```python
response = requests.post('/document/change_parser', json={
    'doc_id': 'doc_id',
    'parser_id': 'naive',
    'parser_config': {
        'chunk_token_num': 4096,
        'delimiter': '\n!?;。；！？',
        'layout_recognize': 'Plain Text'
    }
})
```

## Testing

### Integration Test

Run the integration test:

```bash
python test_monkeyocr_integration.py
```

This will test:
- File type detection
- Parser assignment
- Parser functionality
- Chunk generation

### Integration Verification

Run the verification script to check MonkeyOCR integration:

```bash
python migrate_monkeyocr.py
```

This will:
- Verify integration components
- Test file type detection
- Check existing knowledgebases
- Confirm no migration is needed (system handles defaults dynamically)

## Error Handling

### Common Issues

1. **Unsupported File Format**: Only PDF and image files are supported
2. **Parser Initialization**: MonkeyOCR model must be properly configured
3. **Processing Errors**: Check logs for detailed error messages

### Error Responses

```json
{
    "code": "DATA_ERROR",
    "message": "MonkeyOCR parser only supports PDF and image files!",
    "data": false
}
```

## Performance Considerations

- **Memory Usage**: MonkeyOCR processing can be memory-intensive
- **Processing Time**: Large documents may take longer to process
- **Concurrent Processing**: Limited by available system resources

## Dependencies

- MonkeyOCR library
- CEDD OCR service
- RAGFlow core components

## Future Enhancements

- Support for additional file formats
- Enhanced configuration options
- Performance optimizations
- Batch processing capabilities 