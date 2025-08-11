#!/usr/bin/env python3
"""
MonkeyOCR Parser for RAGFlow Integration - MOCK VERSION FOR TESTING
Integrates CEDD OCR service with RAGFlow document processing.
This mock mirrors the current MonkeyOCR parser's public API and return formats,
without loading heavy models, so you can test locally.
"""

import logging
import json
import re
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

# Add monkeyocr to path for CEDD OCR service
import sys

project_root = Path(__file__).parent.parent.parent
monkeyocr_path = project_root / "monkeyocr"
sys.path.insert(0, str(monkeyocr_path))

# Mock imports - don't actually import the heavy modules

logger = logging.getLogger(__name__)


class MonkeyOCRParserMock:
    """MonkeyOCR parser for RAGFlow document processing - MOCK VERSION"""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize MonkeyOCR parser (MOCK VERSION). No heavy model load."""
        if config_path is None:
            config_path = os.path.join(monkeyocr_path, "model_configs.yaml")

        self.config_path = config_path
        self.monkey_ocr_model = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the MonkeyOCR model (MOCK VERSION FOR TESTING)"""
        try:
            print("🔄 [MOCK] Loading MonkeyOCR model...")
            print(f"🔄 [MOCK] Config path: {self.config_path}")
            print("🔄 [MOCK] Model loading phase completed")

            # Mock model object for testing
            self.monkey_ocr_model = type("MockMonkeyOCR", (), {"config_path": self.config_path, "is_loaded": True})()

            logger.info("MonkeyOCR model initialized successfully (MOCK)")
            print("✅ [MOCK] MonkeyOCR model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MonkeyOCR model: {e}")
            print(f"❌ [MOCK] Failed to initialize MonkeyOCR model: {e}")
            raise

    def parse_document(self, file_path: str, output_dir: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Parse document using MonkeyOCR following exact cedd_parse.py flow (MOCK VERSION FOR TESTING)

        Args:
            file_path: Input file path
            output_dir: Output directory (optional)
            **kwargs: Additional arguments

        Returns:
            Dict with parsing results
        """
        try:
            # Use canned outputs under monkeyocr/5 RNN005 directly if present
            canned_dir = project_root / "monkeyocr" / "5 RNN005"
            enhanced_md_path = str(canned_dir / "5 RNN005_cedd.md")
            if os.path.exists(enhanced_md_path):
                content = self._read_enhanced_markdown(enhanced_md_path)
                print(f"🔄 [MOCK] Using canned output from {enhanced_md_path}")
                return {
                    "success": True,
                    "parsed_dir": str(canned_dir),
                    "enhanced_md_path": enhanced_md_path,
                    "content": content,
                    "content_list": [content] if content else [],
                    "file_path": file_path,
                }
            # Check if file exists first
            if not os.path.exists(file_path):
                return {"success": False, "error": f"File not found: {file_path}", "file_path": file_path}

            if output_dir is None:
                # Create temporary output directory
                output_dir = tempfile.mkdtemp(prefix="monkeyocr_")

            print("🔄 [MOCK] Starting MonkeyOCR parsing with cedd_parse flow")
            print(f"🔄 [MOCK] Input file: {file_path}")
            print(f"🔄 [MOCK] Output directory: {output_dir}")

            # Mock the cedd_parse flow without actually calling it
            print("🔄 [MOCK] Step 1: Parsing PDF and extracting images...")
            print("🔄 [MOCK] Step 2: Classifying images (text vs OMR forms)...")
            print("🔄 [MOCK] Step 3: Running OCR on text images...")
            print("🔄 [MOCK] Step 4: Running OMR on form images...")
            print("🔄 [MOCK] Step 5: Generating enhanced markdown...")

            # Instead of calling cedd_parse, just read the original file content
            content = self._read_file_content(file_path)
            # Ensure sufficiently long mock content to exercise chunking paths
            content = self._ensure_min_length_content(content)

            # Create mock enhanced markdown path
            enhanced_md_path = os.path.join(output_dir, f"{Path(file_path).stem}_cedd.md")

            # Write mock content to the enhanced markdown file
            with open(enhanced_md_path, "w", encoding="utf-8") as f:
                f.write(content)

            print("✅ [MOCK] MonkeyOCR processing completed successfully")

            content_read = self._read_enhanced_markdown(enhanced_md_path)

            return {"success": True, "parsed_dir": output_dir, "enhanced_md_path": enhanced_md_path, "content": content_read, "content_list": [content_read] if content_read else [], "file_path": file_path}

        except Exception as e:
            print(f"❌ [MOCK] Failed to parse document {file_path}: {e}")
            logger.error(f"Failed to parse document {file_path}: {e}")
            return {"success": False, "error": str(e), "file_path": file_path}

    def _read_file_content(self, file_path: str) -> str:
        """Read file content directly (MOCK VERSION FOR TESTING)"""
        try:
            print(f"📖 [MOCK] Reading file content: {file_path}")

            if os.path.exists(file_path):
                # Try to read as text first
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        print(f"📖 [MOCK] Successfully read text file: {len(content)} characters")
                        return content
                except UnicodeDecodeError:
                    # If it's a binary file, return a mock OCR result
                    print("📖 [MOCK] Binary file detected, returning mock OCR content")
                    base = (
                        f"[MOCK OCR RESULT] Content extracted from {Path(file_path).name}\n\n"
                        "This is a mock OCR result for testing purposes. The actual file would be processed by MonkeyOCR "
                        "with full OCR and OMR capabilities.\n\n"
                        f"File: {file_path}\nSize: {os.path.getsize(file_path)} bytes\nType: {Path(file_path).suffix}"
                    )
                    return base
            else:
                print(f"❌ [MOCK] File not found: {file_path}")
                return f"[MOCK OCR RESULT] File not found: {file_path}"

        except Exception as e:
            print(f"❌ [MOCK] Failed to read file content: {e}")
            logger.error(f"Failed to read file content: {e}")
            return f"[MOCK OCR RESULT] Error reading file: {str(e)}"

    def _ensure_min_length_content(self, content: str, min_chars: int = 10000) -> str:
        """Ensure mock content is long enough to test chunking logic.

        If the supplied content is shorter than the threshold, append generated
        paragraphs including common delimiters ("\n!?。；！？") and markdown-like
        headings so tests can exercise splitting and token-based merging.
        """
        if content is None:
            content = ""
        if len(content) >= min_chars:
            return content

        base_block = (
            "## Section: MonkeyOCR Mock\n"
            "This is a long mock paragraph to validate chunking behavior across different delimiters! "
            "It includes sentences with punctuation? It also includes Chinese punctuation。再加上一些中文内容来模拟多语言；"
            "并且包含感叹号！和问号？\n\n"
            "### Subsection\n"
            "- Bullet one: explains the purpose.\n"
            "- Bullet two: adds more tokens!\n"
            "- Bullet three: even more tokens？\n\n"
            "Another paragraph follows with numbers 1, 2, 3 and symbols ~ @ # $ % ^ & *.\n"
        )
        repeats = max(10, (min_chars - len(content)) // max(1, len(base_block)) + 1)
        long_tail = "\n".join(f"{i:03d}. {base_block}" for i in range(repeats))
        return content + "\n\n" + long_tail

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

    def parse_only(self, file_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse only mode - extract images and layout without OCR (MOCK VERSION FOR TESTING)
        Follows cedd_parse.py parse_only mode
        """
        try:
            if output_dir is None:
                output_dir = tempfile.mkdtemp(prefix="monkeyocr_parse_")

            print("🔄 [MOCK] Starting parse_only mode")
            print(f"🔄 [MOCK] Input file: {file_path}")
            print(f"🔄 [MOCK] Output directory: {output_dir}")

            # Mock parse_only flow
            print("🔄 [MOCK] Step 1: Extracting images from PDF...")
            print("🔄 [MOCK] Step 2: Analyzing document layout...")
            print("🔄 [MOCK] Step 3: Generating layout PDF...")
            print("🔄 [MOCK] Step 4: Saving parsed results...")

            # Create mock parsed directory structure
            parsed_dir = os.path.join(output_dir, Path(file_path).stem)
            os.makedirs(parsed_dir, exist_ok=True)

            print("✅ [MOCK] Parse only mode completed successfully")

            return {"success": True, "parsed_dir": parsed_dir, "file_path": file_path}

        except Exception as e:
            print(f"❌ [MOCK] Parse only mode failed: {e}")
            logger.error(f"Parse only mode failed: {e}")
            return {"success": False, "error": str(e), "file_path": file_path}

    def ocr_only(self, parsed_folder: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        OCR only mode - run OCR/OMR on already parsed folder (MOCK VERSION FOR TESTING)
        Follows cedd_parse.py ocr_only mode
        """
        try:
            if output_dir is None:
                output_dir = tempfile.mkdtemp(prefix="monkeyocr_ocr_")

            print("🔄 [MOCK] Starting ocr_only mode on folder: {parsed_folder}")
            print(f"🔄 [MOCK] Parsed folder: {parsed_folder}")
            print(f"🔄 [MOCK] Output directory: {output_dir}")

            # Mock ocr_only flow
            print("🔄 [MOCK] Step 1: Reading parsed folder...")
            print("🔄 [MOCK] Step 2: Running OCR on text images...")
            print("🔄 [MOCK] Step 3: Running OMR on form images...")
            print("🔄 [MOCK] Step 4: Generating enhanced markdown...")

            # Create mock enhanced markdown
            enhanced_md_path = os.path.join(output_dir, f"{Path(parsed_folder).stem}_cedd.md")
            content = f"[MOCK OCR RESULT] Enhanced content from {parsed_folder}\n\nThis is a mock OCR result for testing purposes."

            with open(enhanced_md_path, "w", encoding="utf-8") as f:
                f.write(content)

            print("✅ [MOCK] OCR only mode completed successfully")

            return {"success": True, "enhanced_md_path": enhanced_md_path, "content": content, "parsed_folder": parsed_folder}

        except Exception as e:
            print(f"❌ [MOCK] OCR only mode failed: {e}")
            logger.error(f"OCR only mode failed: {e}")
            return {"success": False, "error": str(e), "parsed_folder": parsed_folder}

    def get_supported_formats(self) -> List[str]:
        """Get supported file formats"""
        return [".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".txt"]

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
    MonkeyOCR chunk function for RAGFlow integration - MOCK VERSION.
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

    def _split_text_into_sections(text: str, delimiter: Optional[str]) -> List[tuple]:
        """Split raw text into naive sections by delimiter, producing (text, tag) tuples.

        Mirrors the production parser Step 1 behavior; tags are empty strings here.
        """
        if not text:
            return []

        effective_delimiter = delimiter if delimiter else "\n!?。；！？"
        sep_class = "|".join([re.escape(ch) for ch in effective_delimiter])
        tokens = re.split(f"({sep_class})", text)

        sections: List[tuple] = []
        buffer: List[str] = []
        for tk in tokens:
            if tk is None or tk == "":
                continue
            buffer.append(tk)
            if re.fullmatch(sep_class, tk) is not None:
                sec = "".join(buffer).strip()
                if sec:
                    sections.append((sec, ""))
                buffer = []
        tail = "".join(buffer).strip()
        if tail:
            sections.append((tail, ""))
        return sections

    try:
        safe_callback(0.1, "Starting MonkeyOCR processing with cedd_parse flow (MOCK)...")

        # Create MonkeyOCR parser instance (MOCK)
        parser = MonkeyOCRParserMock()

        # Save binary to temporary file if needed
        if binary:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
                tmp_file.write(binary)
                temp_path = tmp_file.name
        else:
            temp_path = filename

        safe_callback(0.2, "Validating file format...")

        # Validate file format
        if not parser.validate_file(temp_path):
            safe_callback(-1, f"Unsupported file format: {filename}")
            return []

        safe_callback(0.3, "Processing document with cedd_parse full mode (MOCK)...")

        # Parse document using cedd_parse full mode (MOCK)
        result = parser.parse_document(temp_path)

        if result.get("success"):
            safe_callback(0.8, "Converting to RAGFlow chunks...")

            # Convert to RAGFlow format based on chunking method
            try:
                from rag.nlp import (
                    tokenize,
                    rag_tokenizer,
                    naive_merge,
                    tokenize_chunks,
                )

                content = result.get("content", "")
                if not content:
                    content = f"MonkeyOCR processed: {filename}"

                # Parse parser_config flags akin to Step 1 in real parser
                parser_config = kwargs.get("parser_config", {})
                chunk_token_num = parser_config.get("chunk_token_num")
                delimiter = parser_config.get("delimiter")
                split_pages_flag = bool(parser_config.get("split_pages", False))

                # Create base doc structure
                doc = {
                    "docnm_kwd": filename,
                    "title_tks": rag_tokenizer.tokenize(re.sub(r"\.[a-zA-Z]+$", "", filename)),
                    "doc_type_kwd": "monkeyocr",
                }
                # Provide fine-grained tokens for parity
                doc["title_sm_tks"] = rag_tokenizer.fine_grained_tokenize(doc["title_tks"])  # type: ignore[attr-defined]

                eng = lang.lower() == "english"
                # If chunk_token_num is provided, perform layout-aware chunking when possible
                if isinstance(chunk_token_num, int) and chunk_token_num > 0:
                    try:
                        sections, _tables, _figures = parse_layout(
                            filename=filename,
                            binary=binary,
                            from_page=from_page,
                            to_page=to_page,
                            callback=None,
                            parser_config=parser_config,
                            separate_tables_figures=False,
                        )
                    except Exception:
                        sections = []

                    if not sections:
                        sections = _split_text_into_sections(content, delimiter)

                    def _extract_pn(tag: str) -> int:
                        try:
                            return int(tag.lstrip("@@").split("\t")[0])
                        except Exception:
                            return 0

                    if split_pages_flag:
                        page_to_sections: Dict[int, List[Tuple[str, str]]] = {}
                        for text_i, tag_i in sections:
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
                        chunks = naive_merge(sections, int(chunk_token_num), delimiter if delimiter else "\n!?。；！？")
                        res = tokenize_chunks(chunks, doc, eng, pdf_parser=None)

                    safe_callback(1.0, "MonkeyOCR processing complete (MOCK)")
                    if binary and os.path.exists(temp_path):
                        os.unlink(temp_path)
                    return res

                # Default single-chunk behavior
                tokenize(doc, content, eng)
                safe_callback(1.0, "MonkeyOCR processing complete (MOCK)")
                if binary and os.path.exists(temp_path):
                    os.unlink(temp_path)
                return [doc]
            except ImportError:
                # Fallback if rag.nlp is not available
                safe_callback(0.9, "Using fallback chunk format...")

                content = result.get("content", f"MonkeyOCR processed: {filename}")

                # Create simple chunk format
                doc = {"docnm_kwd": filename, "title_tks": [filename.replace(".", " ").split()], "doc_type_kwd": "monkeyocr", "content": content, "content_tks": content.split()}

                safe_callback(1.0, "MonkeyOCR processing complete (MOCK) - Fallback mode")

                # Cleanup temporary file
                if binary and os.path.exists(temp_path):
                    os.unlink(temp_path)

                return [doc]
        else:
            safe_callback(-1, f"MonkeyOCR failed: {result.get('error', 'Unknown error')}")
            return []

    except Exception as e:
        safe_callback(-1, f"MonkeyOCR processing failed: {str(e)}")
        logger.error(f"Error processing {filename}: {e}")
        return []

if __name__ == "__main__":
    import sys

    def dummy(prog=None, msg=""):
        pass

    chunk(sys.argv[1], from_page=0, to_page=10, callback=dummy)


def parse_layout(
    filename: str,
    binary: Optional[bytes] = None,
    from_page: int = 0,
    to_page: Optional[int] = None,
    callback=None,
    parser_config: Optional[Dict[str, Any]] = None,
    separate_tables_figures: bool = False,
) -> Tuple[List[Tuple[str, str]], List[Tuple[Optional[Any], str]], Optional[List[Any]]]:
    """Layout-only adapter (MOCK) matching DeepDoc contract.

    Produces sections and tables from the mock enhanced markdown. Page tags are
    best-effort based on simple patterns. Figures are returned as empty list
    when requested via `separate_tables_figures`.
    """
    def make_tag(pn: Optional[int]) -> str:
        return f"@@{pn}\t0\t0\t0\t0##" if pn is not None else ""

    def is_table_block(lines_block: List[str]) -> bool:
        has_pipe = any("|" in ln for ln in lines_block)
        has_sep = any(re.search(r"\|?\s*:?[-]{3,}\s*:?\s*\|", ln) for ln in lines_block)
        return has_pipe and has_sep

    # Use canned fixture content_list.json when available
    fixture_dir = project_root / "monkeyocr" / "5 RNN005"
    content_list_path = str(fixture_dir / "5 RNN005_content_list.json")
    if os.path.exists(content_list_path):
        sections: List[Tuple[str, str]] = []
        tables: List[Tuple[Optional[Any], str]] = []
        figures: Optional[List[Any]] = [] if separate_tables_figures else None
        try:
            with open(content_list_path, "r", encoding="utf-8") as f:
                items = json.load(f)
            for item in items if isinstance(items, list) else []:
                if not isinstance(item, dict):
                    continue
                if item.get("type") == "text":
                    txt = item.get("text", "")
                    pn = int(item.get("page_idx", 0)) + 1
                    sections.append((txt, f"@@{pn}\t0\t0\t0\t0##"))
                # images are ignored for tables/figures in the mock fixture (Option A)
        except Exception:
            pass
        return sections, tables, figures

    # Write binary to temp if needed
    if binary:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            tmp.write(binary)
            file_path = tmp.name
    else:
        file_path = filename

    try:
        parser = MonkeyOCRParserMock()
        result = parser.parse_document(file_path)
        if not result.get("success"):
            return [], [], ([] if separate_tables_figures else None)

        content = result.get("content", "") or ""
        if not content.strip():
            return [], [], ([] if separate_tables_figures else None)

        lines = content.splitlines()
        to_page_eff = to_page if to_page is not None else 1_000_000_000

        sections: List[Tuple[str, str]] = []
        tables: List[Tuple[Tuple[Optional[Any], str], str]] = []
        figures: Optional[List[Any]] = [] if separate_tables_figures else None
        current_page: Optional[int] = None
        seen_page = False

        block: List[str] = []

        def flush_block():
            nonlocal block, current_page
            if not block:
                return
            blk = "\n".join(block).strip()
            if not blk:
                block = []
                return
            if is_table_block(block):
                try:
                    from markdown import markdown as md_to_html
                    html = md_to_html(blk, extensions=["markdown.extensions.tables"])  # type: ignore
                except Exception:
                    html = blk
                tables.append(((None, html), make_tag(current_page)))
            else:
                sections.append((blk, make_tag(current_page)))
            block = []

        for ln in lines:
            m = re.match(r"^\s*(?:#+\s*)?(?:Page|PAGE|page)\s+(\d+)\b", ln)
            m2 = re.search(r"\[\[page=(\d+)]]", ln)
            if m or m2:
                flush_block()
                pn = int((m or m2).group(1))
                seen_page = True
                current_page = pn
                continue

            if "\f" in ln:
                flush_block()
                current_page = (current_page + 1) if current_page is not None else 1
                seen_page = True
                ln = ln.replace("\f", "")
                if not ln.strip():
                    continue

            if not ln.strip():
                flush_block()
                continue

            block.append(ln)

        flush_block()

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

        return sections, tables, figures
    finally:
        try:
            if binary and os.path.exists(file_path):
                os.unlink(file_path)
        except Exception:
            pass


def _resolve_mock_fixture(parser_config: Optional[Dict[str, Any]]) -> Optional[str]:
    # Deprecated: fixed canned outputs only
    return None