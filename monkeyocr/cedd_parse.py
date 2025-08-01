#!/usr/bin/env python3.10
import os
import sys
import time
import argparse
from pathlib import Path
import logging

# Removed subprocess import as it's no longer used for internal calls in 'full' mode
from magic_pdf.model.custom_model import MonkeyOCR
from pdf2image import convert_from_path
from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset, ImageDataset
from magic_pdf.model.doc_analyze_by_custom_model_llm import doc_analyze_llm

# --- Constants for configurability and readability ---
DEFAULT_DPI = 150
DEFAULT_OUTPUT_DIR = "./output_cedd"
DEFAULT_CONFIG_PATH = "model_configs.yaml"
DEFAULT_MAX_IMAGE_DIM = 1280

# OMR Constants
OMR_MEAN_PERCENT_THRESHOLD = 7.0
OMR_MIN_PIXEL_COUNT = 50
OMR_Y_TOLERANCE = 10
OMR_X_TOLERANCE = 10
OMR_MIN_CIRCLE_AREA = 50
OMR_CIRCLE_ASPECT_RATIO_MIN = 0.7
OMR_CIRCLE_ASPECT_RATIO_MAX = 1.7
OMR_CIRCLE_SIZE_MIN = 10
OMR_CIRCLE_SIZE_MAX = 100
OMR_HEADER_REGION_RATIO = 0.15
OMR_CROP_TOP_RATIO = 0.13
OMR_MIN_CIRCLES_FOR_PATTERN = 3
OMR_MAX_CIRCLES_TOTAL = 50

# Task instructions for single-task recognition
TASK_INSTRUCTIONS = {
    "text": "Please output the text content from the image.",
    "formula": "Please write out the expression of the formula in the image using LaTeX format.",
    "table": "This is the image of a table. Please output the table in html format.",
}

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)  # Use module-specific logger


# --- Helper Functions for Image Loading ---
def _load_images_from_file(file_path, dpi=DEFAULT_DPI, max_dim=DEFAULT_MAX_IMAGE_DIM):
    """
    Helper to load images from a PDF or image file.
    Returns a list of PIL Images and a flag indicating if they are from PDF.
    """
    file_path = Path(file_path)
    file_extension = file_path.suffix.lower().lstrip(".")
    images = []
    from_pil = False

    if file_extension == "pdf":
        logger.warning("PDF input detected.")
        logger.warning("Converting all PDF pages to images for processing.")
        logger.warning("Consider using individual images for better performance.")
        try:
            logger.info("Converting PDF pages to images...")
            images = convert_from_path(str(file_path), dpi=dpi)
            logger.info(f"Converted {len(images)} pages to images")
        except Exception as e:
            logger.error(f"Failed to convert PDF to images: {e}")
            raise RuntimeError(f"Failed to convert PDF to images: {str(e)}")
    elif file_extension in ["jpg", "jpeg", "png"]:
        try:
            from PIL import Image

            pil_image = Image.open(str(file_path))
            # Resize if needed
            w, h = pil_image.size
            if w > max_dim or h > max_dim:
                scale = min(max_dim / w, max_dim / h)
                new_size = (int(w * scale), int(h * scale))
                logger.info(f"🔄 Resizing image {file_path.name} from {w}x{h} to {new_size[0]}x{new_size[1]}")
                pil_image = pil_image.resize(new_size)
            images = [pil_image]
            from_pil = True  # Flag to indicate source for cleanup
        except Exception as e:
            logger.error(f"Failed to open image {file_path}: {e}")
            raise RuntimeError(f"Failed to open image: {str(e)}")
    else:
        raise ValueError(f"Unsupported file type: {file_extension}. Supports PDF and image files.")
    return images, from_pil


def single_task_recognition(input_file, output_dir, MonkeyOCR_model, task):
    """
    Single task recognition for specific content type.
    Args:
        input_file: Input file path
        output_dir: Output directory
        MonkeyOCR_model: Pre-initialized model instance
        task: Task type ('text', 'formula', 'table')
    Returns:
        Output directory containing results
    """
    logger.info(f"Starting single task recognition: {task}")
    logger.info(f"Processing file: {input_file}")

    if not Path(input_file).exists():
        raise FileNotFoundError(f"Input file does not exist: {input_file}")

    name_without_suff = Path(input_file).stem
    local_md_dir = Path(output_dir) / name_without_suff
    local_md_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output dir: {local_md_dir}")

    md_writer = FileBasedDataWriter(str(local_md_dir))
    instruction = TASK_INSTRUCTIONS.get(task, TASK_INSTRUCTIONS["text"])

    images, from_pil_source = _load_images_from_file(input_file, dpi=DEFAULT_DPI, max_dim=DEFAULT_MAX_IMAGE_DIM)

    logger.info(f"Performing {task} recognition on {len(images)} image(s)...")
    start_time = time.time()
    try:
        instructions = [instruction] * len(images)
        responses = MonkeyOCR_model.chat_model.batch_inference(images, instructions)
        recognition_time = time.time() - start_time
        logger.info(f"Recognition time: {recognition_time:.2f}s")

        # --- OPTIMIZATION: Use str.join for efficient concatenation ---
        combined_result = "\n".join(responses)

        result_filename = f"{name_without_suff}_{task}_result.md"
        md_writer.write(result_filename, combined_result.encode("utf-8"))
        logger.info("Single task recognition completed!")
        logger.info(f"Task: {task}")
        logger.info(f"Processed {len(images)} image(s)")
        logger.info(f"Result saved to: {local_md_dir / result_filename}")

        # --- OPTIMIZATION: Improved cleanup ---
        if from_pil_source and images:
            try:
                # Assuming the first image is the one opened by PIL if from_pil_source is True
                images[0].close()
                logger.debug("Closed PIL image source.")
            except Exception as cleanup_error:
                logger.warning(f"Warning: Error during cleanup of PIL image: {cleanup_error}")

    except Exception as e:
        logger.error(f"Single task recognition failed: {e}")
        raise RuntimeError(f"Single task recognition failed: {str(e)}")

    return str(local_md_dir)


def parse_file(input_file, output_dir, MonkeyOCR_model, split_pages=False, pred_abandon=False):
    """
    Parse PDF or image and save results.
    Args:
        input_file: Input PDF or image file path
        output_dir: Output directory
        MonkeyOCR_model: Pre-initialized model instance
        split_pages: Whether to split result by pages
        pred_abandon: Whether to predict abandon elements
    Returns:
        Output directory containing results
    """
    logger.info(f"Starting to parse file: {input_file}")

    if not Path(input_file).exists():
        raise FileNotFoundError(f"Input file does not exist: {input_file}")

    name_without_suff = Path(input_file).stem
    local_image_dir = Path(output_dir) / name_without_suff / "images"
    local_md_dir = Path(output_dir) / name_without_suff
    image_dir = local_image_dir.name

    local_image_dir.mkdir(parents=True, exist_ok=True)
    local_md_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Output dir: {local_md_dir}")

    image_writer = FileBasedDataWriter(str(local_image_dir))
    md_writer = FileBasedDataWriter(str(local_md_dir))
    reader = FileBasedDataReader()
    file_bytes = reader.read(input_file)
    file_extension = Path(input_file).suffix.lower().lstrip(".")

    if file_extension == "pdf":
        ds = PymuDocDataset(file_bytes)
    else:
        ds = ImageDataset(file_bytes)

    logger.info("Performing document parsing...")
    start_time = time.time()
    infer_result = ds.apply(doc_analyze_llm, MonkeyOCR_model=MonkeyOCR_model, split_pages=split_pages, pred_abandon=pred_abandon)

    if isinstance(infer_result, list):
        logger.info(f"Processing {len(infer_result)} pages separately...")
        for page_idx, page_infer_result in enumerate(infer_result):
            page_dir_name = f"page_{page_idx}"
            page_local_image_dir = Path(output_dir) / name_without_suff / page_dir_name / "images"
            page_local_md_dir = Path(output_dir) / name_without_suff / page_dir_name
            page_image_dir = page_local_image_dir.name

            page_local_image_dir.mkdir(parents=True, exist_ok=True)
            page_local_md_dir.mkdir(parents=True, exist_ok=True)

            page_image_writer = FileBasedDataWriter(str(page_local_image_dir))
            page_md_writer = FileBasedDataWriter(str(page_local_md_dir))

            logger.info(f"Processing page {page_idx} - Output dir: {page_local_md_dir}")

            page_pipe_result = page_infer_result.pipe_ocr_mode(page_image_writer, MonkeyOCR_model=MonkeyOCR_model)
            page_infer_result.draw_model(str(page_local_md_dir / f"{name_without_suff}_page_{page_idx}_model.pdf"))
            page_pipe_result.draw_layout(str(page_local_md_dir / f"{name_without_suff}_page_{page_idx}_layout.pdf"))
            page_pipe_result.draw_span(str(page_local_md_dir / f"{name_without_suff}_page_{page_idx}_spans.pdf"))
            page_pipe_result.dump_md(page_md_writer, f"{name_without_suff}_page_{page_idx}.md", page_image_dir)
            page_pipe_result.dump_content_list(page_md_writer, f"{name_without_suff}_page_{page_idx}_content_list.json", page_image_dir)
            page_pipe_result.dump_middle_json(page_md_writer, f"{name_without_suff}_page_{page_idx}_middle.json")

        logger.info(f"All {len(infer_result)} pages processed and saved in separate subdirectories")
    else:
        logger.info("Processing as single result...")
        pipe_result = infer_result.pipe_ocr_mode(image_writer, MonkeyOCR_model=MonkeyOCR_model)
        infer_result.draw_model(str(local_md_dir / f"{name_without_suff}_model.pdf"))
        pipe_result.draw_layout(str(local_md_dir / f"{name_without_suff}_layout.pdf"))
        pipe_result.draw_span(str(local_md_dir / f"{name_without_suff}_spans.pdf"))
        pipe_result.dump_md(md_writer, f"{name_without_suff}.md", image_dir)
        pipe_result.dump_content_list(md_writer, f"{name_without_suff}_content_list.json", image_dir)
        pipe_result.dump_middle_json(md_writer, f"{name_without_suff}_middle.json")

    parsing_time = time.time() - start_time
    logger.info(f"Parsing and saving time: {parsing_time:.2f}s")
    logger.info(f"Results saved to {local_md_dir}")
    return str(local_md_dir)


import cv2
import numpy as np
from imutils import contours as imutils_contours


def classify_image(image_path):
    """
    Classify image as multiple choice form or text/handwriting using robust circle detection.
    Args:
        image_path (str): Path to the image file
    Returns:
        str: 'multiple_choice' or 'text_handwriting'
    """
    logger.info(f"Classifying image: {image_path}")
    image = cv2.imread(str(image_path))
    if image is None:
        logger.error(f"Could not read image {image_path}")
        return "text_handwriting"
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)

    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=20, param1=50, param2=30, minRadius=5, maxRadius=50)

    valid_circles = 0
    circles_array = None
    if circles is not None:
        circles_array = np.round(circles[0, :]).astype("int")
        valid_circles = len(circles_array)

    has_regular_pattern = False
    if valid_circles >= OMR_MIN_CIRCLES_FOR_PATTERN and circles_array is not None:
        x_coords = circles_array[:, 0]
        y_coords = circles_array[:, 1]
        unique_y = np.unique(np.round(y_coords / OMR_Y_TOLERANCE) * OMR_Y_TOLERANCE)
        unique_x = np.unique(np.round(x_coords / OMR_X_TOLERANCE) * OMR_X_TOLERANCE)
        if len(unique_y) >= 2 and len(unique_x) >= 2:
            has_regular_pattern = True

    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    circular_contours = 0
    text_contours = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < OMR_MIN_CIRCLE_AREA:
            continue
        perimeter = cv2.arcLength(contour, True)
        if perimeter > 0:
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            epsilon = 0.02 * perimeter
            approx = cv2.approxPolyDP(contour, epsilon, True)
            if circularity > 0.7 and len(approx) >= 8:
                circular_contours += 1
            elif len(approx) <= 6 or circularity < 0.3:
                text_contours += 1

    is_multiple_choice = (
        OMR_MIN_CIRCLES_FOR_PATTERN <= valid_circles <= OMR_MAX_CIRCLES_TOTAL and has_regular_pattern and circular_contours > text_contours and circular_contours >= OMR_MIN_CIRCLES_FOR_PATTERN
    )

    result = "multiple_choice" if is_multiple_choice else "text_handwriting"
    logger.info(f"Classification result for {image_path}: {result}")
    return result


def extract_rating_answers_from_cropped_image(image_path):
    """
    Extract 5-point rating scale answers from a cropped image section.
    Works with images that only contain rating circles without document boundaries.
    Args:
        image_path (str): Path to the image file
    Returns:
        list: List of ratings (1-5) for each row, or [] if extraction fails
    """
    image_path = Path(image_path)
    image = cv2.imread(str(image_path))
    if image is None:
        logger.error(f"❌ Could not load image: {image_path}")
        return []

    image = cv2.resize(image, (700, 700))
    crop_top = int(OMR_CROP_TOP_RATIO * image.shape[0])
    region_15 = int(OMR_HEADER_REGION_RATIO * image.shape[0])
    header_region = image[:region_15, :]
    header_gray = cv2.cvtColor(header_region, cv2.COLOR_BGR2GRAY)
    _, header_thresh = cv2.threshold(header_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    header_contours, _ = cv2.findContours(header_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    non_circle_count = 0
    for c in header_contours:
        area = cv2.contourArea(c)
        if area < OMR_MIN_CIRCLE_AREA:
            continue
        x, y, w, h = cv2.boundingRect(c)
        aspect = w / float(h) if h > 0 else 0
        # Use constants for bounds
        if not (OMR_CIRCLE_ASPECT_RATIO_MIN < aspect < OMR_CIRCLE_ASPECT_RATIO_MAX and OMR_CIRCLE_SIZE_MIN < w < OMR_CIRCLE_SIZE_MAX and OMR_CIRCLE_SIZE_MIN < h < OMR_CIRCLE_SIZE_MAX):
            non_circle_count += 1

    logger.debug(f"Header region: found {len(header_contours)} contours, non-circle-like: {non_circle_count}")
    if non_circle_count > 3:
        logger.info("Header detected, cropping top 13%")
        image = image[crop_top:, :]
    else:
        logger.info("No header detected, no crop")

    imgGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    imgGray = clahe.apply(imgGray)
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
    imgThresh = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    kernel = np.ones((3, 3), np.uint8)
    imgThresh = cv2.morphologyEx(imgThresh, cv2.MORPH_OPEN, kernel)
    imgThresh = cv2.morphologyEx(imgThresh, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(imgThresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    circle_like = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < OMR_MIN_CIRCLE_AREA:
            continue
        x, y, w, h = cv2.boundingRect(c)
        aspect = w / float(h) if h > 0 else 0
        if OMR_CIRCLE_ASPECT_RATIO_MIN < aspect < OMR_CIRCLE_ASPECT_RATIO_MAX and OMR_CIRCLE_SIZE_MIN < w < OMR_CIRCLE_SIZE_MAX and OMR_CIRCLE_SIZE_MIN < h < OMR_CIRCLE_SIZE_MAX:
            circle_like.append((x, y, w, h))

    if circle_like:
        xs = [x for x, y, w, h in circle_like]
        ys = [y for x, y, w, h in circle_like]
        ws = [w for x, y, w, h in circle_like]
        hs = [h for x, y, w, h in circle_like]
        x_min, y_min = min(xs), min(ys)
        x_max = max([x + w for x, w in zip(xs, ws)])
        y_max = max([y + h for y, h in zip(ys, hs)])
        margin = 5
        x_min = max(x_min - margin, 0)
        y_min = max(y_min - margin, 0)
        x_max = min(x_max + margin, image.shape[1])
        y_max = min(y_max + margin, image.shape[0])
        logger.debug(f"OMR grid crop: bounding box x={x_min}:{x_max}, y={y_min}:{y_max}, {len(circle_like)} circles detected")
        image = image[y_min:y_max, x_min:x_max]
        imgGray = imgGray[y_min:y_max, x_min:x_max]
        imgBlur = imgBlur[y_min:y_max, x_min:x_max]
        imgThresh = imgThresh[y_min:y_max, x_min:x_max]

    contours, hierarchy = cv2.findContours(imgThresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    circleContours = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > OMR_MIN_CIRCLE_AREA:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            if len(approx) >= 6:
                circleContours.append(cnt)

    if len(circleContours) == 0:
        logger.warning(f"⚠️  No circles found in {image_path.name}")
        return []
    logger.info(f"🔍 Found {len(circleContours)} circles")

    circleContours = imutils_contours.sort_contours(circleContours, method="top-to-bottom")[0]
    ratingRows = []
    for c in range(0, len(circleContours), 5):
        if c + 5 <= len(circleContours):
            row = imutils_contours.sort_contours(circleContours[c : c + 5])[0]
            ratingRows.append(row)

    if len(ratingRows) == 0:
        logger.warning(f"⚠️  No complete rows found (need 5 circles per row) in {image_path.name}")
        return []
    logger.info(f"📊 Found {len(ratingRows)} rating rows")

    all_pixel_values = []
    row_pixel_values = []
    for row_idx, row in enumerate(ratingRows):
        pixelValues = []
        for col_idx, circle in enumerate(row):
            mask = np.zeros(imgThresh.shape, np.uint8)
            cv2.drawContours(mask, [circle], 0, 255, -1)
            masked = cv2.bitwise_and(imgThresh, imgThresh, mask=mask)
            pixelValues.append(cv2.countNonZero(masked))
        row_pixel_values.append(pixelValues)
        all_pixel_values.extend(pixelValues)

    ratings = []
    for i, pixelValues in enumerate(row_pixel_values):
        logger.debug(f"Row {i + 1} pixel counts: {pixelValues}")
        mean_pixel = np.mean(pixelValues)
        if mean_pixel != 0:
            norm_percent = [round((v - mean_pixel) / mean_pixel * 100, 1) for v in pixelValues]
        else:
            norm_percent = [0 for v in pixelValues]
        max_pixel = max(pixelValues)
        max_indices = [i for i, v in enumerate(pixelValues) if v == max_pixel]
        median_pixel = np.median(pixelValues)
        # Use constants
        if len(max_indices) == 1 and median_pixel != 0 and ((max_pixel - median_pixel) / median_pixel * 100) >= OMR_MEAN_PERCENT_THRESHOLD and max_pixel > OMR_MIN_PIXEL_COUNT:
            ratings.append(max_indices[0] + 1)
        else:
            ratings.append(0)

    logger.info(f"OMR ratings for {image_path}: {ratings}")
    return ratings


def single_task_recognition_multi_file_group(file_paths, output_dir, MonkeyOCR_model, task):
    """
    Batch single task recognition for a group of images (text OCR for multiple images).
    Args:
        file_paths: List of image file paths
        output_dir: Output directory
        MonkeyOCR_model: Pre-initialized model instance
        task: Task type ('text', 'formula', 'table')
    Returns:
        Dict mapping file name to OCR result string
    """
    from PIL import Image

    instruction = TASK_INSTRUCTIONS.get(task, TASK_INSTRUCTIONS["text"])
    images = []
    file_names = []
    for file_path in file_paths:
        try:
            img = Image.open(str(file_path))
            # Resize image if too large (max 1280px width/height)
            max_dim = DEFAULT_MAX_IMAGE_DIM
            if hasattr(img, "size"):
                w, h = img.size
                if w > max_dim or h > max_dim:
                    scale = min(max_dim / w, max_dim / h)
                    new_size = (int(w * scale), int(h * scale))
                    logger.info(f"🔄 Resizing image {Path(file_path).name} from {w}x{h} to {new_size[0]}x{new_size[1]}")
                    img = img.resize(new_size)
            images.append(img)
            file_names.append(Path(file_path).name)  # Store name only
        except Exception as e:
            logger.error(f"Failed to load image {file_path}: {e}")
            # Could add error placeholder to results if desired
            continue  # Skip problematic images

    instructions = [instruction] * len(images)
    responses = []

    if images:
        try:
            responses = MonkeyOCR_model.chat_model.batch_inference(images, instructions)
        except Exception as e:
            logger.error(f"[ERROR] Batch inference failed: {e}. Falling back to single-image processing.")
            responses = []
            for img, instr, fname in zip(images, instructions, file_names):
                try:
                    resp = MonkeyOCR_model.chat_model.batch_inference([img], [instr])[0]
                except Exception as e2:
                    resp = f"[ERROR] {str(e2)}"
                    logger.warning(f"[WARNING] Failed processing {fname} with fallback single-image inference: {e2}")
                responses.append(resp)

    # Clean up images
    for img in images:
        if hasattr(img, "close"):
            try:
                img.close()
            except Exception as cleanup_error:
                logger.warning(f"Warning: Error during cleanup of PIL image: {cleanup_error}")

    # Map file name to OCR result
    return dict(zip(file_names, responses))


# --- Helper for OCR_ONLY logic ---
def _run_ocr_only_logic(parsed_folder, model):
    """Refactored core logic for the 'ocr_only' mode."""
    parsed_folder = Path(parsed_folder)
    # Find markdown and images dir
    markdown_file = None
    images_dir = None
    for item in parsed_folder.iterdir():
        if item.is_file() and item.suffix == ".md":
            markdown_file = item
        elif item.is_dir() and item.name == "images":
            images_dir = item

    if not markdown_file:
        logger.error("[ERROR] No markdown file found in parsed folder")
        raise FileNotFoundError("No markdown file found in parsed folder")
    if not images_dir:
        logger.error("[ERROR] No images directory found in parsed folder")
        raise FileNotFoundError("No images directory found in parsed folder")

    with open(markdown_file, "r", encoding="utf-8") as f:
        original_markdown = f.read()
    logger.info(f"[OCR_ONLY] Found {len(list(images_dir.iterdir()))} items in images directory")

    image_files = [f for f in images_dir.iterdir() if f.is_file() and f.suffix.lower() in [".jpg", ".jpeg", ".png"]]
    image_paths = [str(f) for f in image_files]  # Convert to strings for processing functions

    # Classify images
    text_image_paths = []
    omr_image_info = []
    for image_path in image_paths:
        try:
            image_type = classify_image(image_path)
        except Exception as e:
            logger.error(f"[ERROR] Failed to classify image {image_path}: {e}")
            continue  # Or handle error differently
        if image_type == "multiple_choice":
            omr_image_info.append((image_path, image_type))
        else:
            text_image_paths.append(image_path)

    # Batch OCR for text images
    ocr_results = {}
    if text_image_paths:
        logger.info(f"[OCR_ONLY] Batch OCR for {len(text_image_paths)} text images...")
        try:
            ocr_results = single_task_recognition_multi_file_group(text_image_paths, str(parsed_folder), model, task="text")
        except Exception as e:
            logger.error(f"[ERROR] OCR batch processing failed: {e}")

    # OMR for circle images
    omr_results = {}
    for image_path, image_type in omr_image_info:
        try:
            ratings = extract_rating_answers_from_cropped_image(image_path)
            omr_results[Path(image_path).name] = ratings  # Store filename key
        except Exception as e:
            logger.error(f"[ERROR] OMR processing failed for {image_path}: {e}")

    # Map results into new markdown
    enhanced_markdown = original_markdown
    for image_path in text_image_paths:
        image_filename = Path(image_path).name
        image_ref = f"![](images/{image_filename})"
        ocr_text = ocr_results.get(image_filename, "")
        if ocr_text:
            enhanced_markdown = enhanced_markdown.replace(image_ref, ocr_text)
        else:
            enhanced_markdown = enhanced_markdown.replace(image_ref, "[No text found or OCR failed]")

    omr_8_row_info = []
    omr_4_row_info = []
    for image_path, image_type in omr_image_info:
        image_filename = os.path.basename(image_path)
        ratings = omr_results.get(image_filename, [])
        if len(ratings) == 8:
            omr_8_row_info.append((image_path, image_type))
        elif len(ratings) == 4:
            omr_4_row_info.append((image_path, image_type))
        else:
            # Handle unexpected number of rows if necessary, or just process normally
            # For now, let's assume 4 if not 8 (could also warn or skip)
            # Placing unknown size images in 4-row group for now.
            # You might want to log this.
            print(f"[WARNING] Unexpected number of OMR rows ({len(ratings)}) for {image_filename}. Treating as 4-row.")
            omr_4_row_info.append((image_path, image_type))

    # --- PROCESS 8-ROW IMAGES FIRST (Items 1-8) ---
    for image_path, image_type in omr_8_row_info:
        image_filename = os.path.basename(image_path)
        image_ref = f"![](images/{image_filename})"
        ratings = omr_results.get(image_filename)
        if ratings:
            rating_lines = []
            # Start numbering from 1 for the first 8-row image
            start_number = 1
            for i, rating in enumerate(ratings):
                item_number = start_number + i
                if rating > 0:
                    rating_lines.append(f"Item {item_number}: Score {rating}")
                else:
                    rating_lines.append(f"Item {item_number}: No score")
            replacement_text = "\n\n".join(rating_lines)
            enhanced_markdown = enhanced_markdown.replace(image_ref, replacement_text)
        else:
            enhanced_markdown = enhanced_markdown.replace(image_ref, "[No OMR score detected]")

    # --- PROCESS 4-ROW IMAGES SECOND (Items 9-12) ---
    for image_path, image_type in omr_4_row_info:
        image_filename = os.path.basename(image_path)
        image_ref = f"![](images/{image_filename})"
        ratings = omr_results.get(image_filename)
        if ratings:
            rating_lines = []
            # Start numbering from 9 for the first 4-row image
            start_number = 9
            for i, rating in enumerate(ratings):
                item_number = start_number + i
                if rating > 0:
                    rating_lines.append(f"Item {item_number}: Score {rating}")
                else:
                    rating_lines.append(f"Item {item_number}: No score")
            replacement_text = "\n\n".join(rating_lines)
            enhanced_markdown = enhanced_markdown.replace(image_ref, replacement_text)
        else:
            enhanced_markdown = enhanced_markdown.replace(image_ref, "[No OMR score detected]")

    enhanced_md_name = f"{markdown_file.stem}_cedd.md"
    enhanced_md_path = parsed_folder / enhanced_md_name
    try:
        with open(enhanced_md_path, "w", encoding="utf-8") as f:
            f.write(enhanced_markdown)
        logger.info(f"💾 [OCR_ONLY] CEDD markdown saved to: {enhanced_md_path}")
        logger.info("✅ [OCR_ONLY] CEDD parsing completed successfully.")
    except Exception as e:
        logger.error(f"[ERROR] Failed to save enhanced markdown: {e}")
        raise

    return str(enhanced_md_path)


def cedd_parse(input_pdf: str = None, output_dir: str = DEFAULT_OUTPUT_DIR, config_path: str = DEFAULT_CONFIG_PATH, MonkeyOCR_model=None, parsed_folder: str = None, mode: str = "full"):
    """
    CEDD parsing pipeline: PDF → MonkeyOCR → classify images → OMR/OCR → enhanced .md
    Supports three modes: 'parse_only', 'ocr_only', 'full'.
    Args:
        input_pdf: Path to input PDF file
        output_dir: Directory to save results
        config_path: Path to MonkeyOCR config
        MonkeyOCR_model: Optional pre-initialized MonkeyOCR model instance
        parsed_folder: Folder with parsed results (for ocr_only)
        mode: 'parse_only', 'ocr_only', or 'full'
    Returns:
        Path to enhanced markdown file (in full/ocr_only mode)
    """
    try:
        # Load model once at the beginning if needed
        model = MonkeyOCR_model
        if model is None and mode in ["parse_only", "full"]:
            logger.info("Loading MonkeyOCR model...")
            model = MonkeyOCR(config_path)

        if mode == "parse_only":
            if not input_pdf:
                logger.error("[ERROR] --input is required for parse_only mode")
                sys.exit(1)
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            logger.info(f"[PARSE_ONLY] Working dir: {output_dir}")
            result_dir = parse_file(input_pdf, output_dir, model, split_pages=False)
            logger.info(f"[PARSE_ONLY] Parsing complete. Parsed folder: {result_dir}")
            return result_dir

        elif mode == "ocr_only":
            if not parsed_folder:
                logger.error("[ERROR] --parsed_folder is required for ocr_only mode")
                sys.exit(1)
            # Use refactored helper function
            enhanced_md_path = _run_ocr_only_logic(parsed_folder, model)
            return enhanced_md_path

        else:  # full mode
            if not input_pdf:
                logger.error("[ERROR] --input is required for full mode")
                sys.exit(1)

            logger.info("[FULL] Step 1: Parsing PDF and extracting images...")
            # Call parse_file directly instead of subprocess
            parsed_output_dir = parse_file(input_pdf, output_dir, model, split_pages=False)
            parsed_folder_path = Path(output_dir) / Path(input_pdf).stem

            logger.info(f"[FULL] Step 2: Running OCR/OMR on parsed folder: {parsed_folder_path}")
            # Call the core logic of 'ocr_only' mode directly, passing the 'model'
            enhanced_md_path = _run_ocr_only_logic(str(parsed_folder_path), model)

            logger.info("✅ [FULL] All steps completed.")
            return enhanced_md_path

    except Exception as e:
        logger.error(f"[FATAL ERROR] {e}", exc_info=True)  # Log with traceback
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CEDD PDF Parsing CLI Tool (two-phase, memory-safe)")
    parser.add_argument("--mode", choices=["parse_only", "ocr_only", "full"], default="full", help="Run mode: parse_only, ocr_only, or full (default: full)")
    parser.add_argument("--input", help="Input PDF file path (for parse_only or full mode)")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_DIR, help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help=f"MonkeyOCR config file (default: {DEFAULT_CONFIG_PATH})")
    parser.add_argument("--parsed_folder", help="Parsed folder (for ocr_only mode)")
    args = parser.parse_args()

    cedd_parse(input_pdf=args.input, output_dir=args.output, config_path=args.config, parsed_folder=args.parsed_folder, mode=args.mode)
