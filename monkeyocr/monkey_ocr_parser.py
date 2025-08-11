#!/usr/bin/env python3
"""
MonkeyOCR Parser for RAGFlow Integration
Integrates CEDD OCR service with RAGFlow document processing
Follows exact flow from cedd_parse.py
"""

import logging
import re
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

# Add monkeyocr to path for CEDD OCR service
import sys
import gc

try:
    import torch
except ImportError:
    torch = None

project_root = Path(__file__).parent.parent.parent
monkeyocr_path = project_root / "monkeyocr"
sys.path.insert(0, str(monkeyocr_path))

# Import the actual cedd_parse function
from monkeyocr.cedd_parse import cedd_parse
from monkeyocr.magic_pdf.model.custom_model import MonkeyOCR

logger = logging.getLogger(__name__)


class MonkeyOCRParser:
    """MonkeyOCR parser for RAGFlow document processing"""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize MonkeyOCR parser"""
        if config_path is None:
            config_path = os.path.join(monkeyocr_path, "model_configs.yaml")

        self.config_path = config_path

    def parse_document(self, file_path: str, output_dir: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Parse a document via MonkeyOCR and return enhanced markdown results.

        Process: load model → run `cedd_parse` → read enhanced markdown → full cleanup.

        Failure conditions are explicitly treated as errors and will return
        a result with ``success=False``:
        - Missing or non-existent enhanced markdown path
        - Empty enhanced markdown content

        Args:
            file_path: Absolute path to the input file to parse.
            output_dir: Optional output directory for intermediate artifacts.
            **kwargs: Reserved for future options.

        Returns:
            Dict[str, Any]: Parsing result including success flag and content on success.
        """
        logger.info(f"📄 parse_document started for file: {file_path}")
        logger.info(f"📁 Output directory: {output_dir}")
        logger.info(f"⚙️ Additional kwargs: {kwargs}")
        
        # Import memory tracking function
        from monkeyocr.magic_pdf.model.custom_model import get_memory_usage
        from monkeyocr.magic_pdf.model.sub_modules.model_init import AtomModelSingleton
        
        # Log initial memory state
        initial_memory = get_memory_usage()
        logger.info(f"Initial memory state: {initial_memory}")
        
        model = None
        try:
            if output_dir is None:
                # Create temporary output directory
                logger.info("📁 Creating temporary output directory...")
                output_dir = tempfile.mkdtemp(prefix="monkeyocr_")
                logger.info(f"✅ Temporary output directory created: {output_dir}")

            logger.info("Starting MonkeyOCR parsing with single-use approach")
            logger.info(f"Input file: {file_path}")
            logger.info(f"Output directory: {output_dir}")

            # Step 1: Load MonkeyOCR model
            logger.info("🚀 Step 1: Loading MonkeyOCR model...")
            start_time = time.time()
            
            model = MonkeyOCR(self.config_path)
            
            load_time = time.time() - start_time
            logger.info(f"Model loaded successfully in {load_time:.2f} seconds")
            
            # Log memory after model loading
            post_load_memory = get_memory_usage()
            logger.info(f"Memory after model load: {post_load_memory}")

            # Step 2: Process document with cedd_parse
            logger.info("🚀 Step 2: Processing document with cedd_parse...")
            start_time = time.time()
            
            enhanced_md_path = cedd_parse(
                input_pdf=file_path, 
                output_dir=output_dir, 
                config_path=self.config_path, 
                MonkeyOCR_model=model,  # Pass the loaded model
                mode="full"
            )
            
            process_time = time.time() - start_time
            logger.info(f"Document processed successfully in {process_time:.2f} seconds")
            logger.info(f"✅ cedd_parse completed, enhanced_md_path: {enhanced_md_path}")

            # Validate enhanced markdown path existence
            if not enhanced_md_path or not os.path.exists(enhanced_md_path):
                error_msg = (
                    f"Enhanced markdown path missing or not found: {enhanced_md_path}"
                )
                logger.error(f"❌ {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "file_path": file_path,
                    "parsed_dir": output_dir,
                }

            # Log memory after processing
            post_process_memory = get_memory_usage()
            logger.info(f"Memory after processing: {post_process_memory}")

            # Read the enhanced markdown content
            logger.info("📖 Reading enhanced markdown content...")
            content = self._read_enhanced_markdown(enhanced_md_path)
            content_length = len(content or "")
            logger.info(f"✅ Enhanced markdown content read, length: {content_length} characters")

            # Treat empty content as failure to avoid producing empty chunks downstream
            if not content or not content.strip():
                error_msg = "Enhanced markdown content is empty"
                logger.error(f"❌ {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "file_path": file_path,
                    "parsed_dir": output_dir,
                    "enhanced_md_path": enhanced_md_path,
                }

            logger.info("MonkeyOCR processing completed successfully")

            result = {
                "success": True,
                "parsed_dir": output_dir,
                "enhanced_md_path": enhanced_md_path,
                "content": content,
                "content_list": [content],
                "file_path": file_path,
            }
            logger.info(f"📊 Returning result: success={result['success']}, content_length={len(content)}")
            
            return result

        except Exception as e:
            logger.error(f"❌ Failed to parse document {file_path}: {e}")
            logger.exception(f"Exception details for parse_document:")
            
            return {"success": False, "error": str(e), "file_path": file_path}
        
        finally:
            # Step 3: Complete cleanup and shutdown
            logger.info("🧹 Step 3: Starting complete cleanup and shutdown...")
            start_time = time.time()
            
            try:
                # Clean up the model instance
                if model is not None:
                    logger.info("Cleaning up MonkeyOCR model...")
                    model.cleanup()
                    del model
                    model = None
                
                # Clean up singleton cached models
                logger.info("Cleaning up singleton cached models...")
                singleton = AtomModelSingleton()
                cached_count = singleton.get_cached_model_count()
                if cached_count > 0:
                    logger.info(f"Found {cached_count} cached models, cleaning up...")
                    singleton.cleanup_models()
                else:
                    logger.info("No cached models found in singleton")
                
                # Force garbage collection
                logger.info("Forcing garbage collection...")
                gc.collect()
                
                # Clear GPU cache
                if torch and torch.cuda.is_available():
                    logger.info("Clearing GPU cache...")
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize()
                
                cleanup_time = time.time() - start_time
                logger.info(f"Cleanup completed in {cleanup_time:.2f} seconds")
                
                # Log final memory state
                final_memory = get_memory_usage()
                logger.info(f"Final memory state: {final_memory}")
                
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
            
            logger.info(f"🏁 parse_document finished for file: {file_path}")

    def _read_enhanced_markdown(self, md_path: str) -> str:
        """Read enhanced markdown content from cedd_parse output"""
        try:
            if os.path.exists(md_path):
                with open(md_path, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                logger.warning(f"Enhanced markdown file not found: {md_path}")
                return ""
        except Exception as e:
            logger.error(f"Failed to read enhanced markdown: {e}")
            return ""

    def get_supported_formats(self) -> List[str]:
        """Get supported file formats"""
        return [".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".bmp"]

    def validate_file(self, file_path: str) -> bool:
        """Validate if file can be processed by MonkeyOCR"""
        try:
            if not os.path.exists(file_path):
                return False

            file_ext = Path(file_path).suffix.lower()
            supported_formats = self.get_supported_formats()
            return file_ext in supported_formats

        except Exception as e:
            logger.error(f"Failed to validate file: {e}")
            return False

    def get_parsing_options(self) -> Dict[str, Any]:
        """Get available parsing options"""
        return {
            "mode": "full",  # full, parse_only, ocr_only
            "split_pages": False,
            "pred_abandon": False,
            "extract_images": True,
            "generate_layout_pdf": True,
            "generate_spans_pdf": True,
        }


def chunk(filename, binary=None, from_page=0, to_page=100000, lang="Chinese", callback=None, **kwargs):
    """
    MonkeyOCR chunk function for RAGFlow integration.
    Follows exact cedd_parse.py flow with 'full' mode.

    Args:
        filename (str): File name
        binary (bytes): File content
        from_page (int): Start page
        to_page (int): End page
        lang (str): Language
        callback (function): Progress callback
        **kwargs: Additional arguments

    Returns:
        list: List of document chunks
    """

    def safe_callback(progress, message):
        if callback:
            callback(progress, message)

    logger.info(f"🔄 MonkeyOCR chunk function started for file: {filename}")
    logger.info(f"📋 Parameters: from_page={from_page}, to_page={to_page}, lang={lang}")
    logger.info(f"📦 Binary size: {len(binary) if binary else 'None'} bytes")
    logger.info(f"⚙️ Parser config: {kwargs.get('parser_config', {})}")

    def _split_text_into_sections(text: str, delimiter: Optional[str]) -> List[tuple]:
        """Split raw text into naive sections by delimiter, producing (text, tag) tuples.

        The tag field is intentionally empty at this step to preserve current behavior
        (no positional tags) until layout adapters are introduced in later steps.
        """
        if not text:
            return []

        # Default delimiter mirrors naive when unspecified
        effective_delimiter = delimiter if delimiter else "\n!?。；！？"

        # Build a regex that splits on any of the delimiter characters while retaining separators
        # for better readability in reconstructed sections
        sep_class = "|".join([re.escape(ch) for ch in effective_delimiter])
        # Split while keeping delimiters as separate tokens
        tokens = re.split(f"({sep_class})", text)

        sections: List[tuple] = []
        buffer: List[str] = []
        for tk in tokens:
            if tk is None or tk == "":
                continue
            buffer.append(tk)
            # If this token is a delimiter character, we end the current section
            if re.fullmatch(sep_class, tk) is not None:
                sec = "".join(buffer).strip()
                if sec:
                    sections.append((sec, ""))
                buffer = []
        # Flush remainder
        tail = "".join(buffer).strip()
        if tail:
            sections.append((tail, ""))
        return sections

    try:
        safe_callback(0.1, "Starting MonkeyOCR processing with cedd_parse flow...")
        logger.info("✅ Step 1: Starting MonkeyOCR processing")

        # Create MonkeyOCR parser instance
        logger.info("🔧 Creating MonkeyOCR parser instance...")
        parser = MonkeyOCRParser()
        logger.info("✅ MonkeyOCR parser instance created")

        # Save binary to temporary file if needed
        if binary:
            logger.info("💾 Saving binary to temporary file...")
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
                tmp_file.write(binary)
                temp_path = tmp_file.name
            logger.info(f"✅ Binary saved to temporary file: {temp_path}")
        else:
            temp_path = filename
            logger.info(f"📁 Using existing file path: {temp_path}")

        safe_callback(0.2, "Validating file format...")
        logger.info("🔍 Step 2: Validating file format...")

        # Validate file format
        if not parser.validate_file(temp_path):
            error_msg = f"Unsupported file format: {filename}"
            logger.error(f"❌ {error_msg}")
            safe_callback(-1, error_msg)
            return []
        
        logger.info("✅ File format validation passed")

        safe_callback(0.3, "Processing document with cedd_parse full mode...")
        logger.info("🚀 Step 3: Processing document with cedd_parse full mode...")

        # Get parser configuration from kwargs
        parser_config = kwargs.get("parser_config", {})
        logger.info(f"⚙️ Parser config: {parser_config}")
        
        # Use layout_recognize field to determine processing mode
        layout_recognize = parser_config.get("layout_recognize", "MonkeyOCR")
        logger.info(f"🎯 Layout recognize mode: {layout_recognize}")
        
        # Parse document using cedd_parse
        logger.info("📄 Calling parser.parse_document...")
        result = parser.parse_document(temp_path)
        logger.info(f"📊 Parse result success: {result.get('success', False)}")
        
        if result.get("success"):
            safe_callback(0.8, "Converting to RAGFlow chunks...")
            logger.info("🔄 Step 4: Converting to RAGFlow chunks...")

            # Convert to RAGFlow format
            try:
                logger.info("📦 Importing rag.nlp modules...")
                from rag.nlp import (
                    tokenize,  # single-chunk path
                    rag_tokenizer,
                    naive_merge,
                    tokenize_chunks,
                )
                logger.info("✅ rag.nlp modules imported successfully")

                content = result.get("content", "")
                content_length = len(content or "")
                logger.info(f"📝 Content length: {content_length} characters")
                if not content or not content.strip():
                    error_msg = "Empty content after successful parse; treating as failure"
                    logger.error(f"❌ {error_msg}")
                    safe_callback(-1, error_msg)
                    return []

                # Determine whether to honor chunking flags
                chunk_token_num = parser_config.get("chunk_token_num")
                delimiter = parser_config.get("delimiter")
                split_pages_flag = bool(parser_config.get("split_pages", False))

                # Build base doc structure
                logger.info("🏗️ Preparing base doc structure...")
                doc = {
                    "docnm_kwd": filename,
                    "title_tks": rag_tokenizer.tokenize(re.sub(r"\.[a-zA-Z]+$", "", filename)),
                    "doc_type_kwd": "monkeyocr",
                }
                # Provide fine-grained tokens to mirror naive structure
                doc["title_sm_tks"] = rag_tokenizer.fine_grained_tokenize(doc["title_tks"])  # type: ignore[attr-defined]

                eng = lang.lower() == "english"
                logger.info(f"🌐 Language: {lang}, English mode: {eng}")

                # If a valid chunk_token_num is explicitly provided, prefer layout-aware chunking.
                # This preserves default behavior (single chunk) when not set.
                if isinstance(chunk_token_num, int) and chunk_token_num > 0:
                    try:
                        # Prefer parse_layout to obtain (text, tag) sections
                        sections, _tables, _figures = parse_layout(
                            filename=filename,
                            binary=binary,
                            from_page=from_page,
                            to_page=to_page,
                            callback=None,
                            parser_config=parser_config,
                            separate_tables_figures=False,
                        )
                    except Exception as e:
                        logger.warning(f"parse_layout failed, falling back to plain-text sectioning: {e}")
                        sections = []

                    if not sections:
                        # Fallback: text-only splitting from Step 1
                        logger.info("🪚 Falling back to text-only splitting; no sections from layout.")
                        sections = _split_text_into_sections(content, delimiter)

                    def _extract_pn(tag: str) -> int:
                        try:
                            return int(tag.lstrip("@@").split("\t")[0])
                        except Exception:
                            return 0

                    if split_pages_flag:
                        logger.info("📄 Performing by-page chunking using section tags...")
                        # Group sections by page index (0 for unknown)
                        page_to_sections: Dict[int, List[Tuple[str, str]]] = {}
                        for sec in sections:
                            text_i, tag_i = sec
                            pn = _extract_pn(tag_i) if tag_i else 0
                            page_to_sections.setdefault(pn, []).append((text_i, tag_i))

                        all_chunks = []
                        for pn in sorted(page_to_sections.keys()):
                            subset = page_to_sections[pn]
                            if not subset:
                                continue
                            chs = naive_merge(subset, int(chunk_token_num), delimiter if delimiter else "\n!?。；！？")
                            all_chunks.extend(chs)
                        res = tokenize_chunks(all_chunks, doc, eng, pdf_parser=None)
                    else:
                        logger.info("🧩 Performing naive-like merge over all sections...")
                        chunks = naive_merge(sections, int(chunk_token_num), delimiter if delimiter else "\n!?。；！？")
                        res = tokenize_chunks(chunks, doc, eng, pdf_parser=None)

                    safe_callback(1.0, "MonkeyOCR processing complete")
                    # Cleanup temporary file
                    if binary and os.path.exists(temp_path):
                        logger.info("🧹 Cleaning up temporary file...")
                        os.unlink(temp_path)
                        logger.info("✅ Temporary file cleaned up")
                    logger.info(f"📤 Returning {len(res)} chunks (layout-aware)")
                    return res

                # Default path: single-chunk behavior unchanged
                logger.info("🔤 Tokenizing content as a single chunk (default behavior)...")
                tokenize(doc, content, eng)
                logger.info("✅ Content tokenization completed")

                safe_callback(1.0, "MonkeyOCR processing complete")
                logger.info("🎉 MonkeyOCR processing completed successfully")

                # Cleanup temporary file
                if binary and os.path.exists(temp_path):
                    logger.info("🧹 Cleaning up temporary file...")
                    os.unlink(temp_path)
                    logger.info("✅ Temporary file cleaned up")

                logger.info(f"📤 Returning {len([doc])} chunks")
                return [doc]
            except ImportError as e:
                logger.error(f"❌ ImportError in rag.nlp: {e}")
                # Fallback if rag.nlp is not available
                safe_callback(0.9, "Using fallback chunk format...")
                logger.info("🔄 Using fallback chunk format...")

                content = result.get("content", "")
                if not content or not content.strip():
                    error_msg = "Empty content; cannot build fallback chunk"
                    logger.error(f"❌ {error_msg}")
                    safe_callback(-1, error_msg)
                    return []

                # Create simple chunk format
                doc = {"docnm_kwd": filename, "title_tks": [filename.replace(".", " ").split()], "doc_type_kwd": "monkeyocr", "content": content, "content_tks": content.split()}
                logger.info("✅ Fallback chunk format created")

                safe_callback(1.0, "MonkeyOCR processing complete - Fallback mode")
                logger.info("🎉 MonkeyOCR processing completed with fallback mode")

                # Cleanup temporary file
                if binary and os.path.exists(temp_path):
                    logger.info("🧹 Cleaning up temporary file...")
                    os.unlink(temp_path)
                    logger.info("✅ Temporary file cleaned up")

                logger.info(f"📤 Returning {len([doc])} chunks (fallback)")
                return [doc]
        else:
            error_msg = f"MonkeyOCR failed: {result.get('error', 'Unknown error')}"
            logger.error(f"❌ {error_msg}")
            safe_callback(-1, error_msg)
            return []

    except Exception as e:
        error_msg = f"MonkeyOCR processing failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        logger.exception(f"Exception details for {filename}:")
        safe_callback(-1, error_msg)
        return []
    finally:
        logger.info(f"🏁 MonkeyOCR chunk function finished for file: {filename}")


def parse_layout(
    filename: str,
    binary: Optional[bytes] = None,
    from_page: int = 0,
    to_page: Optional[int] = None,
    callback=None,
    parser_config: Optional[Dict[str, Any]] = None,
    separate_tables_figures: bool = False,
) -> Tuple[List[Tuple[str, str]], List[Tuple[Tuple[Optional[Any], str], str]], Optional[List[Any]]]:
    """Parse layout-only view from MonkeyOCR enhanced markdown.

    This adapter mirrors the DeepDoc layout contract expected by `rag/app/naive.py`:
    - sections: List[(text, tag)] where tag is a position string or empty
    - tables: List[((image_or_none, html_string), tag_string)]
    - figures: Optional list when `separate_tables_figures=True` (None otherwise)

    Page tags are best-effort. If page markers can be inferred from the enhanced
    markdown (e.g., lines like "Page N" or form-feed separators), tags are attached
    as "@@pn\t0\t0\t0\t0##". Otherwise, tags are empty strings.
    """
    logger.info("[parse_layout] Starting layout-only parse for MonkeyOCR")

    def make_tag(pn: Optional[int]) -> str:
        return f"@@{pn}\t0\t0\t0\t0##" if pn is not None else ""

    def is_table_block(lines_block: List[str]) -> bool:
        # Simple heuristic for markdown tables
        has_pipe = any("|" in ln for ln in lines_block)
        has_sep = any(re.search(r"\|?\s*:?[-]{3,}\s*:?\s*\|", ln) for ln in lines_block)
        return has_pipe and has_sep

    try:
        # Write binary to temp if provided
        if binary:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
                tmp.write(binary)
                file_path = tmp.name
        else:
            file_path = filename

        if callback:
            callback(0.1, "MonkeyOCR parse_layout: parsing document...")

        parser = MonkeyOCRParser()
        result = parser.parse_document(file_path)
        if not result.get("success"):
            logger.error(f"[parse_layout] parse_document failed: {result.get('error')}")
            return [], [], ([] if separate_tables_figures else None)

        # Prefer normalized layout.json if present
        enhanced_md_path = result.get("enhanced_md_path")
        parsed_dir = result.get("parsed_dir")
        layout_sections: List[Tuple[str, str]] = []
        layout_tables: List[Tuple[Tuple[Optional[Any], str], str]] = []
        layout_figures: Optional[List[Any]] = [] if separate_tables_figures else None

        if enhanced_md_path and parsed_dir:
            try:
                enhanced_path = Path(enhanced_md_path)
                local_md_dir = enhanced_path.parent
                stem = enhanced_path.stem
                base_stem = stem[:-5] if stem.endswith("_cedd") else stem
                layout_json_path = local_md_dir / f"{base_stem}_layout.json"
                if layout_json_path.exists():
                    with open(layout_json_path, "r", encoding="utf-8") as f:
                        payload = json.load(f)
                    # Convert to expected Python types
                    for sec in payload.get("sections", []) or []:
                        if isinstance(sec, (list, tuple)) and len(sec) >= 2:
                            layout_sections.append((str(sec[0]), str(sec[1])))
                    for tbl in payload.get("tables", []) or []:
                        # Expect [[image_or_none, html], tag]
                        if isinstance(tbl, (list, tuple)) and len(tbl) >= 2:
                            pair, tag = tbl[0], tbl[1]
                            image_or_none = None
                            html = ""
                            if isinstance(pair, (list, tuple)) and len(pair) >= 2:
                                image_or_none = pair[0]
                                html = pair[1]
                            layout_tables.append(((image_or_none, html), str(tag)))
                    figs = payload.get("figures", None)
                    if separate_tables_figures:
                        layout_figures = figs if isinstance(figs, list) else []
                    else:
                        layout_figures = None

                    if callback:
                        callback(1.0, "MonkeyOCR parse_layout: loaded normalized layout.json")
                    return layout_sections, layout_tables, layout_figures
            except Exception as e:
                logger.warning(f"[parse_layout] Failed to load layout.json, falling back to markdown parsing: {e}")

        # Fallback: parse enhanced markdown content heuristically
        content = result.get("content", "") or ""
        if not content.strip():
            logger.warning("[parse_layout] Empty enhanced markdown content")
            return [], [], ([] if separate_tables_figures else None)

        # Normalize page range
        to_page_eff = to_page if to_page is not None else 1_000_000_000

        # Iterate lines, detect page headers, accumulate paragraphs
        lines = content.splitlines()
        current_page: Optional[int] = None
        seen_page = False
        sections: List[Tuple[str, str]] = []
        tables: List[Tuple[Tuple[Optional[Any], str], str]] = []
        figures: Optional[List[Any]] = [] if separate_tables_figures else None

        block: List[str] = []

        def flush_block():
            nonlocal block, current_page
            if not block:
                return
            blk = "\n".join(block).strip()
            if not blk:
                block = []
                return
            # Classify as table or section
            if is_table_block(block):
                try:
                    from markdown import markdown as md_to_html
                    html = md_to_html(blk, extensions=["markdown.extensions.tables"])  # type: ignore
                except Exception:
                    html = blk  # Degrade to raw markdown
                tables.append(((None, html), make_tag(current_page)))
            else:
                sections.append((blk, make_tag(current_page)))
            block = []

        for ln in lines:
            # Detect explicit page markers
            m = re.match(r"^\s*(?:#+\s*)?(?:Page|PAGE|page)\s+(\d+)\b", ln)
            m2 = re.search(r"\[\[page=(\d+)]]", ln)
            if m or m2:
                # Flush previous block before page change
                flush_block()
                pn = int((m or m2).group(1))
                seen_page = True
                current_page = pn
                continue

            # Form feed as page separator
            if "\f" in ln:
                flush_block()
                current_page = (current_page + 1) if current_page is not None else 1
                seen_page = True
                ln = ln.replace("\f", "")
                if not ln.strip():
                    continue

            # Paragraph separation
            if not ln.strip():
                flush_block()
                continue

            block.append(ln)

        # Flush trailing block
        flush_block()

        # Apply page range filtering if any page numbers observed
        if seen_page:
            def within(tag: str) -> bool:
                if not tag:
                    return False
                try:
                    pn = int(tag.lstrip("@@").split("\t")[0])
                    return from_page <= pn <= to_page_eff
                except Exception:
                    return True

            sections = [(t, tg) for (t, tg) in sections if within(tg)]
            tables = [tbl for tbl in tables if within(tbl[1])]

        if callback:
            callback(1.0, "MonkeyOCR parse_layout: done")

        logger.info(
            f"[parse_layout] Returning sections={len(sections)}, tables={len(tables)}, figures={'[]' if isinstance(figures, list) else 'None'}"
        )
        return sections, tables, figures

    finally:
        # Clean up temp if any
        try:
            if binary and os.path.exists(file_path):
                os.unlink(file_path)
        except Exception:
            pass

if __name__ == "__main__":
    import sys

    def dummy(prog=None, msg=""):
        pass

    chunk(sys.argv[1], from_page=0, to_page=10, callback=dummy)