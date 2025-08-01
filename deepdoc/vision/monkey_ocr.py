#!/usr/bin/env python3
"""
MonkeyOCR Integration for RAGFlow
Provides a clean interface to MonkeyOCR functionality for document parsing and OCR
"""

import logging
import tempfile
from pathlib import Path
from typing import Optional, Dict, List, Union
import json

# Add monkeyocr to path for imports
monkeyocr_path = Path(__file__).parent.parent / "monkeyocr"

from monkeyocr.magic_pdf.model.custom_model import MonkeyOCR
from monkeyocr.magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from monkeyocr.magic_pdf.data.dataset import PymuDocDataset, ImageDataset
from monkeyocr.magic_pdf.model.doc_analyze_by_custom_model_llm import doc_analyze_llm

logger = logging.getLogger(__name__)


class MonkeyOCRProcessor:
    """
    MonkeyOCR processor for RAGFlow integration
    Handles document parsing, OCR, and OMR (Optical Mark Recognition)
    """

    def __init__(self, config_path: Optional[str] = None, model: Optional[MonkeyOCR] = None):
        """
        Initialize MonkeyOCR processor

        Args:
            config_path: Path to MonkeyOCR config file
            model: Pre-initialized MonkeyOCR model instance
        """
        self.config_path = config_path or str(monkeyocr_path / "model_configs.yaml")
        self.model = model
        self._ensure_model_loaded()

    def _ensure_model_loaded(self):
        """Ensure MonkeyOCR model is loaded"""
        if self.model is None:
            try:
                logger.info("Loading MonkeyOCR model...")
                self.model = MonkeyOCR(self.config_path)
                logger.info("MonkeyOCR model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load MonkeyOCR model: {e}")
                raise RuntimeError(f"MonkeyOCR model initialization failed: {e}")

    def parse_document(self, input_file: Union[str, Path], output_dir: Optional[str] = None, split_pages: bool = False, pred_abandon: bool = False) -> str:
        """
        Parse PDF or image document and extract content

        Args:
            input_file: Path to input PDF or image file
            output_dir: Output directory for results
            split_pages: Whether to split results by pages
            pred_abandon: Whether to predict abandon elements

        Returns:
            Path to output directory containing results
        """
        input_file = Path(input_file)
        if not input_file.exists():
            raise FileNotFoundError(f"Input file does not exist: {input_file}")

        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="monkeyocr_")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Parsing document: {input_file}")
        logger.info(f"Output directory: {output_dir}")

        # Create output structure
        name_without_suff = input_file.stem
        local_image_dir = output_dir / name_without_suff / "images"
        local_md_dir = output_dir / name_without_suff
        image_dir = local_image_dir.name

        local_image_dir.mkdir(parents=True, exist_ok=True)
        local_md_dir.mkdir(parents=True, exist_ok=True)

        # Initialize writers
        image_writer = FileBasedDataWriter(str(local_image_dir))
        md_writer = FileBasedDataWriter(str(local_md_dir))
        reader = FileBasedDataReader()

        # Read file
        file_bytes = reader.read(str(input_file))
        file_extension = input_file.suffix.lower().lstrip(".")

        # Create dataset
        if file_extension == "pdf":
            dataset = PymuDocDataset(file_bytes)
        else:
            dataset = ImageDataset(file_bytes)

        # Perform document analysis
        logger.info("Performing document analysis...")
        infer_result = dataset.apply(doc_analyze_llm, MonkeyOCR_model=self.model, split_pages=split_pages, pred_abandon=pred_abandon)

        # Process results
        if isinstance(infer_result, list):
            logger.info(f"Processing {len(infer_result)} pages separately...")
            for page_idx, page_infer_result in enumerate(infer_result):
                self._process_page_result(page_infer_result, page_idx, name_without_suff, output_dir, self.model)
        else:
            logger.info("Processing as single result...")
            self._process_single_result(infer_result, name_without_suff, local_md_dir, image_writer, md_writer, image_dir)

        logger.info(f"Document parsing completed. Results saved to: {local_md_dir}")
        return str(local_md_dir)

    def _process_page_result(self, page_infer_result, page_idx, name_without_suff, output_dir, model):
        """Process individual page result"""
        page_dir_name = f"page_{page_idx}"
        page_local_image_dir = output_dir / name_without_suff / page_dir_name / "images"
        page_local_md_dir = output_dir / name_without_suff / page_dir_name
        page_image_dir = page_local_image_dir.name

        page_local_image_dir.mkdir(parents=True, exist_ok=True)
        page_local_md_dir.mkdir(parents=True, exist_ok=True)

        page_image_writer = FileBasedDataWriter(str(page_local_image_dir))
        page_md_writer = FileBasedDataWriter(str(page_local_md_dir))

        logger.info(f"Processing page {page_idx}")

        page_pipe_result = page_infer_result.pipe_ocr_mode(page_image_writer, MonkeyOCR_model=model)
        page_infer_result.draw_model(str(page_local_md_dir / f"{name_without_suff}_page_{page_idx}_model.pdf"))
        page_pipe_result.draw_layout(str(page_local_md_dir / f"{name_without_suff}_page_{page_idx}_layout.pdf"))
        page_pipe_result.draw_span(str(page_local_md_dir / f"{name_without_suff}_page_{page_idx}_spans.pdf"))
        page_pipe_result.dump_md(page_md_writer, f"{name_without_suff}_page_{page_idx}.md", page_image_dir)
        page_pipe_result.dump_content_list(page_md_writer, f"{name_without_suff}_page_{page_idx}_content_list.json", page_image_dir)
        page_pipe_result.dump_middle_json(page_md_writer, f"{name_without_suff}_page_{page_idx}_middle.json")

    def _process_single_result(self, infer_result, name_without_suff, local_md_dir, image_writer, md_writer, image_dir):
        """Process single result"""
        pipe_result = infer_result.pipe_ocr_mode(image_writer, MonkeyOCR_model=self.model)
        infer_result.draw_model(str(local_md_dir / f"{name_without_suff}_model.pdf"))
        pipe_result.draw_layout(str(local_md_dir / f"{name_without_suff}_layout.pdf"))
        pipe_result.draw_span(str(local_md_dir / f"{name_without_suff}_spans.pdf"))
        pipe_result.dump_md(md_writer, f"{name_without_suff}.md", image_dir)
        pipe_result.dump_content_list(md_writer, f"{name_without_suff}_content_list.json", image_dir)
        pipe_result.dump_middle_json(md_writer, f"{name_without_suff}_middle.json")

    def extract_text_from_images(self, image_paths: List[Union[str, Path]], task: str = "text") -> Dict[str, str]:
        """
        Extract text from images using OCR

        Args:
            image_paths: List of image file paths
            task: Task type ('text', 'formula', 'table')

        Returns:
            Dictionary mapping filename to extracted text
        """
        from PIL import Image

        # Task instructions
        task_instructions = {
            "text": "Please output the text content from the image.",
            "formula": "Please write out the expression of the formula in the image using LaTeX format.",
            "table": "This is the image of a table. Please output the table in html format.",
        }

        instruction = task_instructions.get(task, task_instructions["text"])
        images = []
        file_names = []

        # Load and preprocess images
        for image_path in image_paths:
            try:
                img = Image.open(str(image_path))
                # Resize if too large (max 1280px)
                max_dim = 1280
                w, h = img.size
                if w > max_dim or h > max_dim:
                    scale = min(max_dim / w, max_dim / h)
                    new_size = (int(w * scale), int(h * scale))
                    logger.info(f"Resizing image {Path(image_path).name} from {w}x{h} to {new_size[0]}x{new_size[1]}")
                    img = img.resize(new_size)
                images.append(img)
                file_names.append(Path(image_path).name)
            except Exception as e:
                logger.error(f"Failed to load image {image_path}: {e}")
                continue

        if not images:
            return {}

        # Perform batch inference
        instructions = [instruction] * len(images)
        responses = []

        try:
            responses = self.model.chat_model.batch_inference(images, instructions)
        except Exception as e:
            logger.error(f"Batch inference failed: {e}. Falling back to single-image processing.")
            responses = []
            for img, instr, fname in zip(images, instructions, file_names):
                try:
                    resp = self.model.chat_model.batch_inference([img], [instr])[0]
                except Exception as e2:
                    resp = f"[ERROR] {str(e2)}"
                    logger.warning(f"Failed processing {fname}: {e2}")
                responses.append(resp)

        # Clean up images
        for img in images:
            try:
                img.close()
            except Exception as e:
                logger.warning(f"Error during image cleanup: {e}")

        # Return results
        return dict(zip(file_names, responses))

    def get_parsed_content(self, parsed_dir: Union[str, Path]) -> Dict[str, any]:
        """
        Extract structured content from parsed directory

        Args:
            parsed_dir: Path to parsed directory

        Returns:
            Dictionary containing extracted content
        """
        parsed_dir = Path(parsed_dir)

        # Find markdown file
        markdown_file = None
        for item in parsed_dir.iterdir():
            if item.is_file() and item.suffix == ".md":
                markdown_file = item
                break

        if not markdown_file:
            raise FileNotFoundError("No markdown file found in parsed directory")

        # Read markdown content
        with open(markdown_file, "r", encoding="utf-8") as f:
            markdown_content = f.read()

        # Find content list JSON
        content_list_file = None
        for item in parsed_dir.iterdir():
            if item.is_file() and item.name.endswith("_content_list.json"):
                content_list_file = item
                break

        content_list = []
        if content_list_file:
            with open(content_list_file, "r", encoding="utf-8") as f:
                content_list = json.load(f)

        return {"markdown_content": markdown_content, "content_list": content_list, "parsed_dir": str(parsed_dir), "markdown_file": str(markdown_file)}
