#!/usr/bin/env python3
"""
MonkeyOCR FastAPI Application
"""

import os
import io
import tempfile
from typing import Optional, List
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
import json

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    # dotenv not available, will use system environment variables only

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from tempfile import gettempdir
import zipfile
from loguru import logger
import time
import cv2
import numpy as np
from pathlib import Path
from imutils import contours as imutils_contours

from magic_pdf.model.custom_model import MonkeyOCR
import uvicorn

# Response models
class TaskResponse(BaseModel):
    success: bool
    task_type: str
    content: str
    message: Optional[str] = None

class ParseResponse(BaseModel):
    success: bool
    message: str
    output_dir: Optional[str] = None
    files: Optional[List[str]] = None
    download_url: Optional[str] = None

class OMRResponse(BaseModel):
    """Response model for OMR processing"""
    success: bool
    message: str
    image_type: str
    ratings: Optional[List[int]] = None
    rating_codes: Optional[List[str]] = None
    processing_details: Optional[dict] = None

class EnhancedParseResponse(BaseModel):
    """Response model for enhanced parsing with OMR and OCR"""
    success: bool
    message: str
    original_markdown: str
    enhanced_markdown: str
    processing_details: dict
    omr_results: dict
    ocr_results: dict

# Global model instance and lock
monkey_ocr_model = None
supports_async = False
model_lock = asyncio.Lock()
executor = ThreadPoolExecutor(max_workers=4)

def initialize_model():
    """Initialize MonkeyOCR model"""
    global monkey_ocr_model
    global supports_async
    if monkey_ocr_model is None:
        config_path = os.getenv("MONKEYOCR_CONFIG", "model_configs.yaml")
        monkey_ocr_model = MonkeyOCR(config_path)
        supports_async = is_async_model(monkey_ocr_model)
    return monkey_ocr_model

def is_async_model(model: MonkeyOCR) -> bool:
    """Check if the model supports async concurrent calls"""
    if hasattr(model, 'chat_model'):
        chat_model = model.chat_model
        # More specific check for async models
        is_async = hasattr(chat_model, 'async_batch_inference')
        logger.info(f"Model {chat_model.__class__.__name__} supports async: {is_async}")
        return is_async
    return False

async def smart_model_call(func, *args, **kwargs):
    """
    Smart wrapper that automatically chooses between concurrent and blocking calls
    based on the model's capabilities
    """
    global monkey_ocr_model, model_lock
    
    if not monkey_ocr_model:
        raise HTTPException(status_code=500, detail="Model not initialized")
    
    if supports_async:
        # For async models, no need for model_lock, can run concurrently
        logger.info("Using concurrent execution (async model detected)")
        # Use asyncio's thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)
    else:
        # For sync models, use model_lock to prevent conflicts
        logger.info("Using blocking execution with lock (sync model detected)")
        async with model_lock:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, func, *args, **kwargs)

async def smart_batch_model_call(images_and_questions_list, batch_func):
    """
    Smart batch processing that can handle multiple requests efficiently
    """
    global monkey_ocr_model
    
    if not monkey_ocr_model:
        raise HTTPException(status_code=500, detail="Model not initialized")
    
    if supports_async and hasattr(monkey_ocr_model.chat_model, 'async_batch_inference'):
        # Use native async batch processing for maximum efficiency
        logger.info(f"Using native async batch processing for {len(images_and_questions_list)} requests")
        
        # Flatten all images and questions
        all_images = []
        all_questions = []
        request_indices = []
        
        for i, (images, questions) in enumerate(images_and_questions_list):
            for img, q in zip(images, questions):
                all_images.append(img)
                all_questions.append(q)
                request_indices.append(i)
        
        # Single batch call for all requests
        try:
            # Use the chat model's async batch inference method properly
            all_results = await monkey_ocr_model.chat_model.async_batch_inference(all_images, all_questions)
        except Exception as e:
            logger.error(f"Async batch inference failed: {e}, falling back to individual processing")
            # Fallback to individual processing using the corrected method
            results = []
            for images, questions in images_and_questions_list:
                try:
                    # Use the thread-safe smart_model_call wrapper
                    result = await smart_model_call(batch_func, images, questions)
                    results.append(result)
                except Exception as inner_e:
                    logger.error(f"Individual processing also failed: {inner_e}")
                    results.append([f"Error: {str(inner_e)}"] * len(images))
            return results
        
        # Reconstruct results for each original request
        results = []
        result_idx = 0
        for images, questions in images_and_questions_list:
            request_results = []
            for _ in range(len(images)):
                request_results.append(all_results[result_idx])
                result_idx += 1
            results.append(request_results)
        
        return results
    
    elif supports_async:
        # Concurrent processing for async models
        logger.info(f"Using concurrent batch processing for {len(images_and_questions_list)} requests")
        tasks = []
        for images, questions in images_and_questions_list:
            task = smart_model_call(batch_func, images, questions)
            tasks.append(task)
        
        return await asyncio.gather(*tasks, return_exceptions=True)
    else:
        # Sequential processing for sync models
        logger.info(f"Using sequential batch processing for {len(images_and_questions_list)} requests")
        results = []
        for images, questions in images_and_questions_list:
            result = await smart_model_call(batch_func, images, questions)
            results.append(result)
        return results

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler"""
    # Startup
    try:
        initialize_model()
        model_type = "async-capable" if supports_async else "sync-only"
        logger.info(f"✅ MonkeyOCR model initialized successfully ({model_type})")
    except Exception as e:
        logger.info(f"❌ Failed to initialize MonkeyOCR model: {e}")
        raise
    
    yield
    
    # Shutdown
    global executor
    executor.shutdown(wait=True)
    logger.info("🔄 Application shutdown complete")

app = FastAPI(
    title="MonkeyOCR API",
    description="OCR and Document Parsing API using MonkeyOCR",
    version="1.0.0",
    lifespan=lifespan
)

temp_dir = os.getenv("TMPDIR", gettempdir())
logger.info(f"Using temporary directory: {temp_dir}")
os.makedirs(temp_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=temp_dir), name="static")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "MonkeyOCR API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model_loaded": monkey_ocr_model is not None}

@app.post("/ocr/text", response_model=TaskResponse)
async def extract_text(file: UploadFile = File(...)):
    """Extract text from image or PDF"""
    return await perform_ocr_task(file, "text")

@app.post("/ocr/formula", response_model=TaskResponse)
async def extract_formula(file: UploadFile = File(...)):
    """Extract formulas from image or PDF"""
    return await perform_ocr_task(file, "formula")

@app.post("/ocr/table", response_model=TaskResponse)
async def extract_table(file: UploadFile = File(...)):
    """Extract tables from image or PDF"""
    return await perform_ocr_task(file, "table")

@app.post("/parse", response_model=ParseResponse)
async def parse_document(file: UploadFile = File(...)):
    """Parse complete document (PDF or image)"""
    return await parse_document_internal(file, split_pages=False)

@app.post("/parse/split", response_model=ParseResponse)
async def parse_document_split(file: UploadFile = File(...)):
    """Parse complete document and split result by pages (PDF or image)"""
    return await parse_document_internal(file, split_pages=True)

@app.post("/omr/classify", response_model=OMRResponse)
async def classify_omr_image(file: UploadFile = File(...)):
    """
    Classify image as multiple choice form or text/handwriting
    
    Args:
        file: Image file to classify
        
    Returns:
        OMRResponse with image classification
    """
    try:
        # Validate file type - only image files
        allowed_extensions = {'.jpg', '.jpeg', '.png'}
        file_ext_with_dot = os.path.splitext(file.filename)[1].lower() if file.filename else ''
        
        if file_ext_with_dot not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_ext_with_dot}. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save uploaded file temporarily
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext_with_dot, prefix=f"omr_classify_{unique_suffix}_") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Classify image
            image_type = classify_image(temp_file_path)
            
            return OMRResponse(
                success=True,
                message=f"Image classified successfully as {image_type}",
                image_type=image_type,
                processing_details={
                    "filename": file.filename,
                    "file_size": len(content),
                    "classification_result": image_type
                }
            )
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file {temp_file_path}: {cleanup_error}")
            
    except Exception as e:
        logger.error(f"OMR classification failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OMR classification failed: {str(e)}")

@app.post("/omr/extract", response_model=OMRResponse)
async def extract_omr_answers(file: UploadFile = File(...)):
    """
    Extract 5-point rating scale answers from multiple choice form image
    
    Args:
        file: Image file containing multiple choice form
        
    Returns:
        OMRResponse with extracted ratings and rating codes
    """
    try:
        # Validate file type - only image files
        allowed_extensions = {'.jpg', '.jpeg', '.png'}
        file_ext_with_dot = os.path.splitext(file.filename)[1].lower() if file.filename else ''
        
        if file_ext_with_dot not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext_with_dot}. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save uploaded file temporarily
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext_with_dot, prefix=f"omr_extract_{unique_suffix}_") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # First classify the image
            image_type = classify_image(temp_file_path)
            
            if image_type != 'multiple_choice':
                return OMRResponse(
                    success=False,
                    message=f"Image is classified as {image_type}, not a multiple choice form",
                    image_type=image_type,
                    processing_details={
                        "filename": file.filename,
                        "file_size": len(content),
                        "classification_result": image_type,
                        "extraction_skipped": True
                    }
                )
            
            # Extract ratings
            ratings = extract_rating_answers_from_cropped_image(temp_file_path)
            
            if ratings is None:
                return OMRResponse(
                    success=False,
                    message="Failed to extract ratings from image",
                    image_type=image_type,
                    processing_details={
                        "filename": file.filename,
                        "file_size": len(content),
                        "classification_result": image_type,
                        "extraction_failed": True
                    }
                )
            
            # Convert ratings to rating codes
            rating_codes = []
            for rating in ratings:
                if rating == 0:
                    rating_codes.append("00000")  # No rating marked
                else:
                    # Creates pattern like "00@00" for rating 3
                    code = "0" * (rating - 1) + "@" + "0" * (5 - rating)
                    rating_codes.append(code)
            
            return OMRResponse(
                success=True,
                message=f"Successfully extracted {len(ratings)} ratings from multiple choice form",
                image_type=image_type,
                ratings=ratings,
                rating_codes=rating_codes,
                processing_details={
                    "filename": file.filename,
                    "file_size": len(content),
                    "classification_result": image_type,
                    "total_rows": len(ratings),
                    "filled_ratings": len([r for r in ratings if r > 0]),
                    "empty_ratings": len([r for r in ratings if r == 0])
                }
            )
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file {temp_file_path}: {cleanup_error}")
            
    except Exception as e:
        logger.error(f"OMR extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OMR extraction failed: {str(e)}")

@app.post("/omr/process", response_model=OMRResponse)
async def process_omr_image(file: UploadFile = File(...)):
    """
    Complete OMR processing: classify and extract answers if it's a multiple choice form
    
    Args:
        file: Image file to process
        
    Returns:
        OMRResponse with classification and extraction results
    """
    try:
        # Validate file type - only image files
        allowed_extensions = {'.jpg', '.jpeg', '.png'}
        file_ext_with_dot = os.path.splitext(file.filename)[1].lower() if file.filename else ''
        
        if file_ext_with_dot not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_ext_with_dot}. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save uploaded file temporarily
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext_with_dot, prefix=f"omr_process_{unique_suffix}_") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Step 1: Classify image
            image_type = classify_image(temp_file_path)
            
            if image_type != 'multiple_choice':
                return OMRResponse(
                    success=False,
                    message=f"Image is classified as {image_type}, skipping extraction",
                    image_type=image_type,
                    processing_details={
                        "filename": file.filename,
                        "file_size": len(content),
                        "classification_result": image_type,
                        "extraction_skipped": True
                    }
                )
            
            # Step 2: Extract ratings
            ratings = extract_rating_answers_from_cropped_image(temp_file_path)
            
            if ratings is None:
                return OMRResponse(
                    success=False,
                    message="Failed to extract ratings from multiple choice form",
                    image_type=image_type,
                    processing_details={
                        "filename": file.filename,
                        "file_size": len(content),
                        "classification_result": image_type,
                        "extraction_failed": True
                    }
                )
            
            # Step 3: Convert to rating codes
            rating_codes = []
            for rating in ratings:
                if rating == 0:
                    rating_codes.append("00000")
                else:
                    code = "0" * (rating - 1) + "@" + "0" * (5 - rating)
                    rating_codes.append(code)
            
            return OMRResponse(
                success=True,
                message=f"Successfully processed multiple choice form with {len(ratings)} rows",
                image_type=image_type,
                ratings=ratings,
                rating_codes=rating_codes,
                processing_details={
                    "filename": file.filename,
                    "file_size": len(content),
                    "classification_result": image_type,
                    "total_rows": len(ratings),
                    "filled_ratings": len([r for r in ratings if r > 0]),
                    "empty_ratings": len([r for r in ratings if r == 0])
                }
            )
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file {temp_file_path}: {cleanup_error}")
            
    except Exception as e:
        logger.error(f"OMR processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OMR processing failed: {str(e)}")

@app.post("/parse/enhanced", response_model=EnhancedParseResponse)
async def parse_document_enhanced(file: UploadFile = File(...)):
    """
    Enhanced document parsing with OMR and OCR processing
    
    Workflow:
    1. Parse PDF to extract images and markdown
    2. Process images through OMR to extract rating data
    3. Process remaining text images through OCR
    4. Replace image references in markdown with extracted content
    
    Args:
        file: PDF file to process
        
    Returns:
        EnhancedParseResponse with original and enhanced markdown
    """
    try:
        # Validate file type - only PDF files
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400, 
                detail="Only PDF files are supported for enhanced parsing"
            )
        
        # Save uploaded file temporarily
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', prefix=f"enhanced_parse_{unique_suffix}_") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Step 1: Parse PDF to get images and markdown
            logger.info("Step 1: Parsing PDF document...")
            output_dir = tempfile.mkdtemp(prefix=f"enhanced_parse_{unique_suffix}_")
            result_dir = await async_parse_file(temp_file_path, output_dir, split_pages=False)
            
            # Find markdown file and images directory
            markdown_file = None
            images_dir = None
            
            if os.path.exists(result_dir):
                for filename in os.listdir(result_dir):
                    if filename.endswith('.md'):
                        markdown_file = os.path.join(result_dir, filename)
                    elif filename == 'images' and os.path.isdir(os.path.join(result_dir, filename)):
                        images_dir = os.path.join(result_dir, filename)
            
            if not markdown_file:
                raise HTTPException(status_code=500, detail="No markdown file generated")
            
            if not images_dir:
                raise HTTPException(status_code=500, detail="No images directory found")
            
            # Read original markdown
            with open(markdown_file, 'r', encoding='utf-8') as f:
                original_markdown = f.read()
            
            logger.info(f"Found {len(os.listdir(images_dir))} images to process")
            
            # Step 2: Process images through OMR and OCR
            enhanced_markdown = original_markdown
            omr_results = {"processed_images": [], "total_ratings": 0}
            ocr_results = {"processed_images": [], "total_text": 0}
            
            # Get all image files
            image_files = [f for f in os.listdir(images_dir) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            for image_filename in image_files:
                image_path = os.path.join(images_dir, image_filename)
                image_ref = f"![](images/{image_filename})"
                
                logger.info(f"Processing image: {image_filename}")
                
                # Step 2a: Try OMR processing first
                try:
                    # Classify image
                    image_type = classify_image(image_path)
                    
                    if image_type == 'multiple_choice':
                        # Extract ratings
                        ratings = extract_rating_answers_from_cropped_image(image_path)
                        
                        if ratings and any(r > 0 for r in ratings):
                            # Convert ratings to formatted text (one line per row)
                            rating_lines = []
                            for i, rating in enumerate(ratings, 1):
                                if rating > 0:
                                    rating_lines.append(f"Item {i}: Score {rating}")
                                else:
                                    rating_lines.append(f"Item {i}: No score")
                            
                            replacement_text = "\n\n".join(rating_lines)
                            enhanced_markdown = enhanced_markdown.replace(image_ref, replacement_text)
                            
                            omr_results["processed_images"].append({
                                "filename": image_filename,
                                "image_type": image_type,
                                "ratings": ratings,
                                "replacement_text": replacement_text
                            })
                            omr_results["total_ratings"] += len([r for r in ratings if r > 0])
                            
                            logger.info(f"OMR processed: {image_filename} - {len([r for r in ratings if r > 0])} ratings")
                            continue
                    
                    # Step 2b: If not OMR or no ratings found, try OCR
                    logger.info(f"Trying OCR for: {image_filename}")
                    
                    # Create temporary file for OCR processing
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image_filename)[1], 
                                                   prefix=f"ocr_temp_{unique_suffix}_") as ocr_temp:
                        # Copy image to temp file
                        with open(image_path, 'rb') as src:
                            ocr_temp.write(src.read())
                        ocr_temp_path = ocr_temp.name
                    
                    try:
                        # Process with OCR
                        result_dir_ocr = await async_single_task_recognition(ocr_temp_path, output_dir, "text")
                        
                        # Read OCR result
                        ocr_result_files = [f for f in os.listdir(result_dir_ocr) if f.endswith('_text_result.md')]
                        if ocr_result_files:
                            ocr_result_file = os.path.join(result_dir_ocr, ocr_result_files[0])
                            with open(ocr_result_file, 'r', encoding='utf-8') as f:
                                ocr_text = f.read().strip()
                            
                            if ocr_text:
                                enhanced_markdown = enhanced_markdown.replace(image_ref, ocr_text)
                                
                                ocr_results["processed_images"].append({
                                    "filename": image_filename,
                                    "image_type": image_type,
                                    "extracted_text": ocr_text
                                })
                                ocr_results["total_text"] += 1
                                
                                logger.info(f"OCR processed: {image_filename} - {len(ocr_text)} characters")
                            else:
                                logger.warning(f"No text extracted from {image_filename}")
                        else:
                            logger.warning(f"No OCR result file found for {image_filename}")
                    
                    finally:
                        # Clean up OCR temp file
                        try:
                            os.unlink(ocr_temp_path)
                        except:
                            pass
                
                except Exception as e:
                    logger.error(f"Error processing {image_filename}: {e}")
                    # Keep original image reference if processing fails
                    continue
            
            # Save enhanced markdown file in the same folder as original
            enhanced_markdown_file = os.path.join(result_dir, f"{Path(markdown_file).stem}_enhanced.md")
            with open(enhanced_markdown_file, 'w', encoding='utf-8') as f:
                f.write(enhanced_markdown)
            
            logger.info(f"💾 Saved enhanced markdown: {enhanced_markdown_file}")
            
            # Prepare processing details
            processing_details = {
                "filename": file.filename,
                "file_size": len(content),
                "total_images": len(image_files),
                "omr_processed": len(omr_results["processed_images"]),
                "ocr_processed": len(ocr_results["processed_images"]),
                "unprocessed_images": len(image_files) - len(omr_results["processed_images"]) - len(ocr_results["processed_images"]),
                "original_markdown_file": markdown_file,
                "enhanced_markdown_file": enhanced_markdown_file
            }
            
            return EnhancedParseResponse(
                success=True,
                message=f"Enhanced parsing completed successfully. Processed {len(image_files)} images.",
                original_markdown=original_markdown,
                enhanced_markdown=enhanced_markdown,
                processing_details=processing_details,
                omr_results=omr_results,
                ocr_results=ocr_results
            )
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file {temp_file_path}: {cleanup_error}")
            
    except Exception as e:
        logger.error(f"Enhanced parsing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Enhanced parsing failed: {str(e)}")

async def async_parse_file(input_file_path: str, output_dir: str, split_pages: bool = False):
    """
    Optimized async version of parse_file that breaks down processing into async chunks
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    import uuid
    
    if not monkey_ocr_model:
        raise HTTPException(status_code=500, detail="Model not initialized")
    
    # Get filename with unique identifier to avoid conflicts
    name_without_suff = '.'.join(os.path.basename(input_file_path).split(".")[:-1])
    unique_id = str(uuid.uuid4())[:8]  # Short unique identifier
    safe_name = f"{name_without_suff}_{unique_id}"
    
    # Prepare output directory with unique name
    local_image_dir = os.path.join(output_dir, safe_name, "images")
    local_md_dir = os.path.join(output_dir, safe_name)
    image_dir = os.path.basename(local_image_dir)
    
    # Create directories asynchronously with better error handling
    def create_dir_safe(path):
        try:
            os.makedirs(path, exist_ok=True)
        except FileExistsError:
            # Directory already exists, that's fine
            pass
        except Exception as e:
            logger.error(f"Failed to create directory {path}: {e}")
            raise
    
    await asyncio.get_event_loop().run_in_executor(None, create_dir_safe, local_image_dir)
    await asyncio.get_event_loop().run_in_executor(None, create_dir_safe, local_md_dir)
    
    logger.info(f"Output dir: {local_md_dir}")
    
    # Read file content in thread pool
    def read_file_sync():
        from magic_pdf.data.data_reader_writer import FileBasedDataReader
        reader = FileBasedDataReader()
        return reader.read(input_file_path)
    
    file_bytes = await asyncio.get_event_loop().run_in_executor(None, read_file_sync)
    
    # Create dataset instance in thread pool
    def create_dataset_sync():
        from magic_pdf.data.dataset import PymuDocDataset, ImageDataset
        file_extension = input_file_path.split(".")[-1].lower()
        if file_extension == "pdf":
            return PymuDocDataset(file_bytes)
        else:
            return ImageDataset(file_bytes)
    
    ds = await asyncio.get_event_loop().run_in_executor(None, create_dataset_sync)
    
    # Run inference in thread pool
    def run_inference_sync():
        from magic_pdf.model.doc_analyze_by_custom_model_llm import doc_analyze_llm
        return ds.apply(doc_analyze_llm, MonkeyOCR_model=monkey_ocr_model, split_pages=split_pages)
    
    logger.info("Starting document parsing...")
    start_time = time.time()
    
    # Use smart model call for inference
    if supports_async:
        # For async models, run without lock
        infer_result = await asyncio.get_event_loop().run_in_executor(None, run_inference_sync)
    else:
        # For sync models, use lock
        async with model_lock:
            infer_result = await asyncio.get_event_loop().run_in_executor(None, run_inference_sync)
    
    parsing_time = time.time() - start_time
    logger.info(f"Parsing time: {parsing_time:.2f}s")
    
    # Process results asynchronously
    await process_inference_results_async(
        infer_result, output_dir, safe_name, 
        local_image_dir, local_md_dir, image_dir, split_pages
    )
    
    return local_md_dir

async def process_inference_results_async(infer_result, output_dir, name_without_suff, 
                                        local_image_dir, local_md_dir, image_dir, split_pages):
    """
    Process inference results asynchronously
    """
    from magic_pdf.data.data_reader_writer import FileBasedDataWriter
    
    def create_writers():
        image_writer = FileBasedDataWriter(local_image_dir)
        md_writer = FileBasedDataWriter(local_md_dir)
        return image_writer, md_writer
    
    # Check if infer_result is a list (split pages)
    if isinstance(infer_result, list):
        logger.info(f"Processing {len(infer_result)} pages separately...")
        
        # Process pages concurrently
        tasks = []
        for page_idx, page_infer_result in enumerate(infer_result):
            task = process_single_page_async(
                page_infer_result, page_idx, output_dir, name_without_suff
            )
            tasks.append(task)
        
        # Wait for all page processing to complete
        await asyncio.gather(*tasks)
        
        logger.info(f"All {len(infer_result)} pages processed and saved in separate subdirectories")
    else:
        # Process single result
        logger.info("Processing as single result...")
        await process_single_result_async(
            infer_result, name_without_suff, local_image_dir, local_md_dir, image_dir
        )

async def process_single_page_async(page_infer_result, page_idx, output_dir, name_without_suff):
    """
    Process a single page result asynchronously
    """
    import uuid
    
    page_dir_name = f"page_{page_idx}"
    page_local_image_dir = os.path.join(output_dir, name_without_suff, page_dir_name, "images")
    page_local_md_dir = os.path.join(output_dir, name_without_suff, page_dir_name)
    page_image_dir = os.path.basename(page_local_image_dir)
    
    # Create page-specific directories with better error handling
    def create_dir_safe(path):
        try:
            os.makedirs(path, exist_ok=True)
        except FileExistsError:
            # Directory already exists, that's fine
            pass
        except Exception as e:
            logger.error(f"Failed to create page directory {path}: {e}")
            raise
    
    await asyncio.get_event_loop().run_in_executor(None, create_dir_safe, page_local_image_dir)
    await asyncio.get_event_loop().run_in_executor(None, create_dir_safe, page_local_md_dir)
    
    def process_page_sync():
        from magic_pdf.data.data_reader_writer import FileBasedDataWriter
        
        # Create page-specific writers
        page_image_writer = FileBasedDataWriter(page_local_image_dir)
        page_md_writer = FileBasedDataWriter(page_local_md_dir)
        
        logger.info(f"Processing page {page_idx} - Output dir: {page_local_md_dir}")
        
        # Pipeline processing for this page
        page_pipe_result = page_infer_result.pipe_ocr_mode(page_image_writer, MonkeyOCR_model=monkey_ocr_model)
        
        # Save page-specific results
        page_infer_result.draw_model(os.path.join(page_local_md_dir, f"{name_without_suff}_page_{page_idx}_model.pdf"))
        page_pipe_result.draw_layout(os.path.join(page_local_md_dir, f"{name_without_suff}_page_{page_idx}_layout.pdf"))
        page_pipe_result.draw_span(os.path.join(page_local_md_dir, f"{name_without_suff}_page_{page_idx}_spans.pdf"))
        page_pipe_result.dump_md(page_md_writer, f"{name_without_suff}_page_{page_idx}.md", page_image_dir)
        page_pipe_result.dump_content_list(page_md_writer, f"{name_without_suff}_page_{page_idx}_content_list.json", page_image_dir)
        page_pipe_result.dump_middle_json(page_md_writer, f'{name_without_suff}_page_{page_idx}_middle.json')
    
    # Run page processing in thread pool
    await asyncio.get_event_loop().run_in_executor(None, process_page_sync)

async def process_single_result_async(infer_result, name_without_suff, local_image_dir, local_md_dir, image_dir):
    """
    Process single result asynchronously
    """
    def process_single_sync():
        from magic_pdf.data.data_reader_writer import FileBasedDataWriter
        
        image_writer = FileBasedDataWriter(local_image_dir)
        md_writer = FileBasedDataWriter(local_md_dir)
        
        # Pipeline processing for single result
        pipe_result = infer_result.pipe_ocr_mode(image_writer, MonkeyOCR_model=monkey_ocr_model)
        
        # Save single result
        infer_result.draw_model(os.path.join(local_md_dir, f"{name_without_suff}_model.pdf"))
        pipe_result.draw_layout(os.path.join(local_md_dir, f"{name_without_suff}_layout.pdf"))
        pipe_result.draw_span(os.path.join(local_md_dir, f"{name_without_suff}_spans.pdf"))
        pipe_result.dump_md(md_writer, f"{name_without_suff}.md", image_dir)
        pipe_result.dump_content_list(md_writer, f"{name_without_suff}_content_list.json", image_dir)
        pipe_result.dump_middle_json(md_writer, f'{name_without_suff}_middle.json')
    
    # Run processing in thread pool
    await asyncio.get_event_loop().run_in_executor(None, process_single_sync)

async def async_single_task_recognition(input_file_path: str, output_dir: str, task: str):
    """
    Optimized async version of single_task_recognition
    """
    import uuid
    
    logger.info(f"Starting async single task recognition: {task}")
    
    # Get filename with unique identifier to avoid conflicts
    name_without_suff = '.'.join(os.path.basename(input_file_path).split(".")[:-1])
    unique_id = str(uuid.uuid4())[:8]  # Short unique identifier
    safe_name = f"{name_without_suff}_{unique_id}"
    
    # Prepare output directory with unique name
    local_md_dir = os.path.join(output_dir, safe_name)
    
    def create_dir_safe(path):
        try:
            os.makedirs(path, exist_ok=True)
        except FileExistsError:
            # Directory already exists, that's fine
            pass
        except Exception as e:
            logger.error(f"Failed to create directory {path}: {e}")
            raise
    
    await asyncio.get_event_loop().run_in_executor(None, create_dir_safe, local_md_dir)
    
    # Get task instruction
    from parse import TASK_INSTRUCTIONS
    instruction = TASK_INSTRUCTIONS.get(task, TASK_INSTRUCTIONS['text'])
    
    # Load images asynchronously
    def load_images_sync():
        file_extension = input_file_path.split(".")[-1].lower()
        images = []
        
        if file_extension == 'pdf':
            from pdf2image import convert_from_path
            images = convert_from_path(input_file_path, dpi=150)
        elif file_extension in ['jpg', 'jpeg', 'png']:
            from PIL import Image
            images = [Image.open(input_file_path)]
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")
        
        return images, file_extension
    
    images, file_extension = await asyncio.get_event_loop().run_in_executor(None, load_images_sync)
    
    # Perform recognition
    logger.info(f"Performing {task} recognition on {len(images)} image(s)...")
    start_time = time.time()
    
    # Prepare instructions for all images
    instructions = [instruction] * len(images)
    
    # Use chat model for recognition
    if supports_async and hasattr(monkey_ocr_model.chat_model, 'async_batch_inference'):
        # Use async batch inference if available
        try:
            responses = await monkey_ocr_model.chat_model.async_batch_inference(images, instructions)
        except Exception as e:
            logger.warning(f"Async batch inference failed: {e}, falling back to sync")
            responses = await asyncio.get_event_loop().run_in_executor(
                None, monkey_ocr_model.chat_model.batch_inference, images, instructions
            )
    else:
        # Use sync batch inference in thread pool
        responses = await asyncio.get_event_loop().run_in_executor(
            None, monkey_ocr_model.chat_model.batch_inference, images, instructions
        )
    
    recognition_time = time.time() - start_time
    logger.info(f"Recognition time: {recognition_time:.2f}s")
    
    # Combine and save results
    def save_results_sync():
        from magic_pdf.data.data_reader_writer import FileBasedDataWriter
        
        md_writer = FileBasedDataWriter(local_md_dir)
        
        # Combine results
        combined_result = responses[0]
        for i, response in enumerate(responses):
            if i > 0:
                combined_result = combined_result + "\n\n" + response
        
        # Save result with original name (without unique suffix)
        result_filename = f"{name_without_suff}_{task}_result.md"
        md_writer.write(result_filename, combined_result.encode('utf-8'))
        
        return result_filename
    
    result_filename = await asyncio.get_event_loop().run_in_executor(None, save_results_sync)
    
    logger.info(f"Single task recognition completed!")
    logger.info(f"Result saved to: {os.path.join(local_md_dir, result_filename)}")
    
    # Clean up images
    def cleanup_images():
        try:
            for img in images:
                if hasattr(img, 'close'):
                    img.close()
        except Exception as cleanup_error:
            logger.warning(f"Warning: Error during cleanup: {cleanup_error}")
    
    await asyncio.get_event_loop().run_in_executor(None, cleanup_images)
    
    return local_md_dir

async def parse_document_internal(file: UploadFile, split_pages: bool = False):
    """Internal function to parse document with optional page splitting"""
    try:
        if not monkey_ocr_model:
            raise HTTPException(status_code=500, detail="Model not initialized")
        
        # Validate file type - support both PDF and image files
        allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png'}
        file_ext_with_dot = os.path.splitext(file.filename)[1].lower() if file.filename else ''
        
        if file_ext_with_dot not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_ext_with_dot}. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Get original filename without extension
        original_name = '.'.join(file.filename.split('.')[:-1])
        
        # Save uploaded file temporarily with unique name to avoid conflicts
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext_with_dot, prefix=f"upload_{unique_suffix}_") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Create output directory with unique name
            output_dir = tempfile.mkdtemp(prefix=f"monkeyocr_parse_{unique_suffix}_")
            
            # Use optimized async parse function
            result_dir = await async_parse_file(temp_file_path, output_dir, split_pages)
            
            # List generated files
            files = []
            if os.path.exists(result_dir):
                for root, dirs, filenames in os.walk(result_dir):
                    for filename in filenames:
                        rel_path = os.path.relpath(os.path.join(root, filename), result_dir)
                        files.append(rel_path)
            
            # Create download URL with original filename and timestamp
            suffix = "_split" if split_pages else "_parsed"
            timestamp = int(time.time() * 1000)  # Use milliseconds for better uniqueness
            zip_filename = f"{original_name}{suffix}_{timestamp}_{unique_suffix}.zip"
            zip_path = os.path.join(temp_dir, zip_filename)
            
            # Create ZIP file asynchronously
            await create_zip_file_async(result_dir, zip_path, original_name, split_pages)
            
            download_url = f"/static/{zip_filename}"
            
            # Determine file type for response message
            file_type = "PDF" if file_ext_with_dot == '.pdf' else "image"
            parse_type = "with page splitting" if split_pages else "standard"
            
            return ParseResponse(
                success=True,
                message=f"{file_type} parsing ({parse_type}) completed successfully",
                output_dir=result_dir,
                files=files,
                download_url=download_url
            )
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file {temp_file_path}: {cleanup_error}")
            
    except Exception as e:
        logger.error(f"Parsing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")

async def create_zip_file_async(result_dir, zip_path, original_name, split_pages):
    """Create ZIP file asynchronously"""
    def create_zip_sync():
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, filenames in os.walk(result_dir):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(file_path, result_dir)
                    
                    if split_pages:
                        # For split pages, maintain the page directory structure
                        # but add original name prefix
                        if rel_path.startswith('page_'):
                            # Keep the page structure: page_0/filename -> page_0/original_name_filename
                            parts = rel_path.split('/', 1)
                            if len(parts) == 2:
                                page_dir, filename_part = parts
                                if filename_part.startswith('images/'):
                                    # Handle images: page_0/images/img.jpg -> page_0/images/original_name_img.jpg
                                    img_name = filename_part.replace('images/', '')
                                    new_filename = f"{page_dir}/images/{original_name}_{img_name}"
                                else:
                                    # Handle other files in page directories
                                    new_filename = f"{page_dir}/{original_name}_{filename_part}"
                            else:
                                new_filename = f"{original_name}_{rel_path}"
                        else:
                            new_filename = f"{original_name}_{rel_path}"
                    else:
                        # Handle different file types
                        if filename.endswith('.md'):
                            new_filename = f"{original_name}.md"
                        elif filename.endswith('_content_list.json'):
                            new_filename = f"{original_name}_content_list.json"
                        elif filename.endswith('_middle.json'):
                            new_filename = f"{original_name}_middle.json"
                        elif filename.endswith('_model.pdf'):
                            new_filename = f"{original_name}_model.pdf"
                        elif filename.endswith('_layout.pdf'):
                            new_filename = f"{original_name}_layout.pdf"
                        elif filename.endswith('_spans.pdf'):
                            new_filename = f"{original_name}_spans.pdf"
                        else:
                            # For images and other files, keep relative path structure but rename
                            if 'images/' in rel_path:
                                # Keep images in images subfolder with original name prefix
                                image_name = os.path.basename(rel_path)
                                new_filename = f"images/{original_name}_{image_name}"
                            else:
                                new_filename = f"{original_name}_{filename}"
                    
                    zipf.write(file_path, new_filename)
    
    # Run ZIP creation in thread pool to avoid blocking
    await asyncio.get_event_loop().run_in_executor(None, create_zip_sync)

def classify_image(image_path):
    """
    Classify image as multiple choice form or text/handwriting using robust circle detection.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: 'multiple_choice' or 'text_handwriting'
    """
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        logger.error(f"Could not read image {image_path}")
        return 'unknown'
    
    # Convert to grayscale for processing
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise and improve circle detection
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    
    # Hough Circle Transform
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=20,
        param1=50,
        param2=30,
        minRadius=5,
        maxRadius=50
    )
    
    # Count valid circles detected by Hough transform
    valid_circles = 0
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        valid_circles = len(circles)
    
    # Pattern Analysis
    has_regular_pattern = False
    if valid_circles >= 3:
        if circles is not None:
            x_coords = circles[:, 0]
            y_coords = circles[:, 1]
            
            # Horizontal alignment detection
            y_tolerance = 10
            unique_y = np.unique(np.round(y_coords / y_tolerance) * y_tolerance)
            
            # Vertical alignment detection
            x_tolerance = 10
            unique_x = np.unique(np.round(x_coords / x_tolerance) * x_tolerance)
            
            # Grid pattern validation
            if len(unique_y) >= 2 and len(unique_x) >= 2:
                has_regular_pattern = True
    
    # Contour Analysis
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Analyze contour properties
    circular_contours = 0
    text_contours = 0
    
    for contour in contours:
        if cv2.contourArea(contour) < 50:
            continue
            
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        if perimeter > 0:
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            epsilon = 0.02 * perimeter
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            if circularity > 0.7 and len(approx) >= 8:
                circular_contours += 1
            elif len(approx) <= 6 or circularity < 0.3:
                text_contours += 1
    
    # Classification decision logic
    is_multiple_choice = (
        valid_circles >= 3 and
        valid_circles <= 50 and
        has_regular_pattern and
        circular_contours > text_contours and
        circular_contours >= 3
    )
    
    return 'multiple_choice' if is_multiple_choice else 'text_handwriting'


def extract_rating_answers_from_cropped_image(image_path):
    """
    Extract 5-point rating scale answers from a cropped image section.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        list: List of ratings (1-5) for each row, or None if extraction fails
    """
    # Load image
    image = cv2.imread(str(image_path))
    if image is None:
        logger.error(f"Could not load image: {image_path}")
        return None
    
    # Image preprocessing
    image = cv2.resize(image, (700, 700))

    # Conditional header crop (top 15%)
    crop_top = int(0.15 * image.shape[0])
    header_region = image[:crop_top, :]
    header_gray = cv2.cvtColor(header_region, cv2.COLOR_BGR2GRAY)
    _, header_thresh = cv2.threshold(header_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    header_contours, _ = cv2.findContours(header_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    non_circle_count = 0
    for c in header_contours:
        area = cv2.contourArea(c)
        if area < 50:
            continue
        x, y, w, h = cv2.boundingRect(c)
        aspect = w / float(h) if h > 0 else 0
        if not (0.7 < aspect < 1.7 and 10 < w < 100 and 10 < h < 100):
            non_circle_count += 1
    
    if non_circle_count > 0:
        logger.info("Header detected, cropping top 15%")
        image = image[crop_top:, :]

    # Convert to grayscale for contour detection
    imgGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply CLAHE to enhance contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    imgGray = clahe.apply(imgGray)

    # Apply Gaussian blur
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)

    # Adaptive thresholding
    imgThresh = cv2.adaptiveThreshold(
        imgBlur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11, 2
    )

    # Morphological operations
    kernel = np.ones((3, 3), np.uint8)
    imgThresh = cv2.morphologyEx(imgThresh, cv2.MORPH_OPEN, kernel)
    imgThresh = cv2.morphologyEx(imgThresh, cv2.MORPH_CLOSE, kernel)

    # Final crop to OMR grid
    contours, _ = cv2.findContours(imgThresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    circle_like = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < 50:
                continue
        x, y, w, h = cv2.boundingRect(c)
        aspect = w / float(h) if h > 0 else 0
        if 0.7 < aspect < 1.7 and 10 < w < 100 and 10 < h < 100:
            circle_like.append((x, y, w, h))
    
    if circle_like:
        xs = [x for x, y, w, h in circle_like]
        ys = [y for x, y, w, h in circle_like]
        ws = [w for x, y, w, h in circle_like]
        hs = [h for x, y, w, h in circle_like]
        x_min, y_min = min(xs), min(ys)
        x_max, y_max = max([x + w for x, w in zip(xs, ws)]), max([y + h for y, h in zip(ys, hs)])
        margin = 5
        x_min = max(x_min - margin, 0)
        y_min = max(y_min - margin, 0)
        x_max = min(x_max + margin, image.shape[1])
        y_max = min(y_max + margin, image.shape[0])
        
        # Crop all images to bounding box
        image = image[y_min:y_max, x_min:x_max]
        imgGray = imgGray[y_min:y_max, x_min:x_max]
        imgBlur = imgBlur[y_min:y_max, x_min:x_max]
        imgThresh = imgThresh[y_min:y_max, x_min:x_max]
    
    # Contour detection
    contours, hierarchy = cv2.findContours(imgThresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
    # Circle filtering
    circleContours = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 50:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            if len(approx) >= 6:
                circleContours.append(cnt)
    
    if len(circleContours) == 0:
        logger.warning(f"No circles found in {Path(image_path).name}")
        return None
    
    # Pattern organization
    circleContours = imutils_contours.sort_contours(circleContours, method="top-to-bottom")[0]
    
    # Row grouping
    ratingRows = []
    for c in range(0, len(circleContours), 5):
        if c + 5 <= len(circleContours):
            row = imutils_contours.sort_contours(circleContours[c:c + 5])[0]
            ratingRows.append(row)
    
    if len(ratingRows) == 0:
        logger.warning("No complete rows found (need 5 circles per row)")
        return None
    
    # Answer extraction
    all_pixel_values = []
    row_pixel_values = []
    for row in ratingRows:
        pixelValues = []
        for circle in row:
            mask = np.zeros(imgThresh.shape, np.uint8)
            cv2.drawContours(mask, [circle], 0, 255, -1)
            mask = cv2.bitwise_and(imgThresh, imgThresh, mask=mask)
            pixelValues.append(cv2.countNonZero(mask))
        row_pixel_values.append(pixelValues)
        all_pixel_values.extend(pixelValues)
    
    MEAN_PERCENT_THRESHOLD = 7.0
    ratings = []
    for i, pixelValues in enumerate(row_pixel_values):
        mean_pixel = np.mean(pixelValues)
        max_pixel = max(pixelValues)
        max_indices = [i for i, v in enumerate(pixelValues) if v == max_pixel]
        
        if len(max_indices) == 1 and mean_pixel != 0 and ((max_pixel - mean_pixel) / mean_pixel * 100) >= MEAN_PERCENT_THRESHOLD:
            ratings.append(max_indices[0] + 1)
        else:
            ratings.append(0)
    
    return ratings


async def perform_ocr_task(file: UploadFile, task_type: str) -> TaskResponse:
    """Perform OCR task on uploaded file"""
    try:
        if not monkey_ocr_model:
            raise HTTPException(status_code=500, detail="Model not initialized")
        
        # Validate file type
        allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png'}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_ext}. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save uploaded file temporarily with unique name
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext, prefix=f"ocr_{unique_suffix}_") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Create output directory with unique name
            output_dir = tempfile.mkdtemp(prefix=f"monkeyocr_{task_type}_{unique_suffix}_")
            
            # Use optimized async single task recognition
            result_dir = await async_single_task_recognition(temp_file_path, output_dir, task_type)
            
            # Read result file
            def read_result_sync():
                result_files = [f for f in os.listdir(result_dir) if f.endswith(f'_{task_type}_result.md')]
                if not result_files:
                    raise Exception("No result file generated")
                
                result_file_path = os.path.join(result_dir, result_files[0])
                with open(result_file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            content = await asyncio.get_event_loop().run_in_executor(None, read_result_sync)
            
            return TaskResponse(
                success=True,
                task_type=task_type,
                content=content,
                message=f"{task_type.capitalize()} extraction completed successfully"
            )
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file {temp_file_path}: {cleanup_error}")
            
    except Exception as e:
        logger.error(f"OCR task failed: {str(e)}")
        return TaskResponse(
            success=False,
            task_type=task_type,
            content="",
            message=f"OCR task failed: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7861)
