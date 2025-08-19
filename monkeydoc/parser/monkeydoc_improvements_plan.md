## MonkeyDoc parsing improvements — plan and steps

### 2025-08-14 update — Comprehensive, column-aware chunking (new version)

Context: We will mirror MonkeyOCR’s page pipeline (layout → spans → reading order → grouping → render) and add general column-aware chunking that stitches nearby media (figures/tables) with their anchor text blocks. The old plan remains below (old version).

Key objectives
- Reproduce MonkeyOCR’s `pdf_info` structure semantics to ensure parity with the markdown output (see `pdf_parse_union_core_v2_llm.py` and `PipeResultLLM.union_make`).
- Column-aware chunking that handles all common page layouts, not just “text-left + image-right”.
- Deterministic, configurable rules; stable ordering via LayoutReader; memory-safe OCR.

Terminology
- Block: YOLO-normalized layout region (Text/Title/ImageBody/ImageCaption/TableBody/TableCaption/Footnote/Equation).
- Span/Line: intra-block text line segments built from text-layer or OCR; ordered via LayoutReader.
- Entity: logical unit used for chunking. Types: TextEntity, FigureEntity, TableEntity, MixedEntity.

Phase A — Page entities (MonkeyOCR-compatible)
1) Layout detection and scaling
   - Keep YOLO boxes in px → rescale to PDF units per page using (img_w/pdf_w, img_h/pdf_h).
   - Discard Abandon/unknown; carry `category_id` mapping and scores; configurable `layout_thr`.
2) Build text spans and fill content
   - For text-like categories (Text/Title/ImageCaption/TableCaption/Footnote):
     - Build spans/lines per block; assign pymupdf chars with center-in-span + y-band rules (see `calculate_char_in_span`).
     - `chars_to_content` → content; empty spans → OCR fallback on ROI (in-memory), then reflow as a line.
3) Reading order
   - Collect all line boxes on a page and call LayoutReader (`order_lines`) to obtain order indices; fallback to (top, left).
4) Grouping (caption/footnote with body)
   - Reuse rules from `process_groups` and `revert_group_blocks` to bind TableBody↔TableCaption/Footnote and ImageBody↔ImageCaption/Footnote with median `index` and group bbox.
5) Entities
   - Convert grouped blocks into entities:
     - TextEntity: ordered lines + bbox (union of lines).
     - FigureEntity: body + optional caption text (OCR if handwriting).
     - TableEntity: body + optional caption; HTML generation optional.

References in monkeyocr (source of truth)
- `monkeyocr/cedd_parse.py`: high-level flow calling `pipe_ocr_mode`, dumping md, middle.json, content_list.json.
- `monkeyocr/magic_pdf/operators/models_llm.py::InferenceResultLLM.pipe_ocr_mode` → `pdf_parse_union` (core pipeline assembly).
- `monkeyocr/magic_pdf/pdf_parse_union_core_v2_llm.py`:
  - `ocr_prepare_bboxes_for_layout_split_v2`, `ocr_construct_page_component_v2`, `ocr_cut_image_and_table` — pre-proc to build spans and body blocks.
  - `fill_spans_in_blocks`, `fix_block_spans_v2`, `fill_char_in_spans` — attach glyphs/OCR into spans and produce content.
  - `sort_lines_by_model`, `do_predict` — LayoutReader ordering.
  - `process_groups`, `revert_group_blocks` — caption/footnote ↔ body grouping; group indices for ordering.
- `monkeyocr/magic_pdf/operators/pipes_llm.py::PipeResultLLM` → `union_make` renders pdf_info to markdown.

Phase B — Column-aware stitching (generalized)
Goal: Merge near-by media with the most relevant text anchor to produce coherent chunks.

Anchor candidates (priority)
1) A caption’s anchor is its body (already grouped). If the caption has lines, prepend/append to the body’s textual output.
2) For a Figure/Table entity without explicit caption or with empty caption text, find the best TextEntity anchor on the same page:
   - Vertical overlap ratio: `overlap_y(entity, text) ≥ y_overlap` (default 0.35)
   - Horizontal relation: prefer anchors to the left/right based on entity position; allow both columns.
   - Distance score: `dx_norm + dy_norm`, weighted; choose smallest score, break ties with reading index proximity.
3) If no good anchor, the entity becomes its own chunk.

Compose MixedEntity (stitching)
- For each TextEntity in reading order, attach zero or more media entities that chose it as anchor, respecting text-first then media order. Mark media as consumed to avoid duplicates.
- If a media overlaps multiple TextEntities significantly, split its OCR text by y-slices (optional, off by default) or choose the closest anchor only.

Edge cases handled
- Two columns: media at right stitched to left text if overlap and gap thresholds satisfied.
- Media between two text blocks vertically: anchor to the nearest block by y-center distance.
- Multiple figures beside the same text: stable order by x0 then y0.
- Full-width figures: anchor to the preceding text block in reading order unless caption explicitly anchors elsewhere.
- Sidebars/marginals: treat as separate chunks unless overlap_y with nearby text exceeds `sidebar_y_overlap` (default 0.5) and area ratio < `sidebar_area_ratio`.
- Equations: treat like figures with inline text rendering; optionally inline into text if width within text column.

Rendering to sections (DeepDoc-compatible)
- For TextEntity/MixedEntity: join ordered lines; append OCR text from attached figures/tables under the text, separated by a newline; tag with union bbox of the textual region plus attached media bbox (configurable: union vs text-only bbox).
- For TableEntity: if `table_html=true`, place HTML under its anchor text; else use caption/summary.
- Output list `[(text + @@pos##, ""), …]` in strict page order.

Config (new)
- `parser_config.monkeyocr.layout_thr: float` – min YOLO score.
- `parser_config.monkeyocr.ocr_batch_size: int` – recognition batching (default 8).
- `parser_config.monkeyocr.column: { enabled: true, y_overlap: 0.35, max_hgap_ratio: 0.3, prefer_left: true }`
- `parser_config.monkeyocr.sidebar: { y_overlap: 0.5, area_ratio: 0.2 }`
- `parser_config.monkeyocr.table_html: true|false`.

Pseudocode (stitching)
```
entities = build_entities(page)
groups   = group_captions(entities)
ordered  = order_lines(groups)
anchors  = [e for e in ordered if e.type == Text]
media    = [e for e in ordered if e.type in {Figure, Table}]
for m in media:
  best = argmin_text_anchor(m, anchors, y_overlap, max_hgap_ratio)
  if best: best.attach(m); consumed.add(m)
chunks = []
for a in anchors:
  text = join_lines(a)
  for m in a.attached_media:
    text += "\n" + render_media_text(m)  # OCR or caption/HTML
  chunks.append(section(text, bbox=union_or_text_bbox(a, a.attached_media)))
for m in media - consumed:  # unanchored
  chunks.append(section(render_media_text(m), bbox=m.bbox))
```

Final-stage OCR tasking (memory-aware)
- Process order in one pass per page:
  1) Text-like blocks (non-ImageBody): build spans and fill from text-layer; OCR fallback minimally (small crops) where span text is empty. Keep recognition model unloaded here.
  2) Tables: build structure, associate captions; defer heavy OCR (HTML) to the end.
  3) Figures (CategoryId.ImageBody only): defer ALL figure OCR to the very last stage across the document.
- After lines are ordered and entities are grouped and stitched, perform a single batched OCR stage for remaining media (figures/tables needing HTML):
  - Before this stage: unload layout/reader models and free caches.
  - Create a recognition-only MonkeyOCR instance; run batched OCR with configured `ocr_batch_size`.
  - Attach recognized texts (or HTML) back into entities; render sections.
  - Cleanup recognition model and clear caches.

Rationale: postponing heavy OCR for images to the final stage maximizes available memory (avoids coexistence of YOLO/LayoutReader and VLM), addressing OOM on MPS/CPU.

Two-phase OCR separation (explicit)
- Phase 1 OCR (lightweight): applies to NON-ImageBody categories only
  - Categories: `Text`, `Title`, `OcrText`, `ImageCaption`, `ImageFootnote`, `TableCaption`, `TableFootnote`, optional `InterlineEquation_*`.
  - Trigger: only when text-layer yields empty spans for a block/span.
  - Prompt: simple text extraction; short batch size; in-memory crops; recognition model kept unloaded if text-layer suffices.

- Phase 2 OCR (heavy, final): applies to `ImageBody` (handwriting/figures) exclusively
  - Collect all `ImageBody` ROIs after grouping/stitching.
  - Unload relation/layout; free caches.
  - Instantiate recognition-only model; run OCR with handwriting-oriented prompt; batch by `ocr_batch_size`.
  - Attach results under the anchored text entities (stitching) or as standalone when unanchored.

Config additions
- `parser_config.monkeyocr.ocr.phase1.enabled` (default true)
- `parser_config.monkeyocr.ocr.phase2.enabled` (default true)
- `parser_config.monkeyocr.ocr.phase1.batch_size` (default 4)
- `parser_config.monkeyocr.ocr.phase2.batch_size` (default 8)
- `parser_config.monkeyocr.ocr.phase2.prompt`: handwriting-focused prompt string

Implementation tasks
1) Tag blocks by `CategoryId` early and route to Phase 1 vs Phase 2 OCR queues.
2) In `pdf_parser.py`:
   - During span fill, only enqueue NON-ImageBody spans to Phase 1 fallback queue; run small-batch OCR inline.
   - Build entities, order lines, group captions, stitch columns.
   - Collect `ImageBody` entities into a Phase 2 queue; unload layout/reader; run recognition-only OCR once; attach results to entities.
3) Ensure caches are cleared between phases; close recognition model after Phase 2.

Performance & memory
- Use one recognition-only model per doc; unload layout/reader before OCR; batch OCR by config; free caches per stage.

Delivery
- Implement page entities, grouping, stitching, rendering in `monkeydoc/parser/pdf_parser.py` behind the existing MonkeyOCR path. Keep current flow as fallback.

Acceptance
- Two-column pages produce one chunk per logical text block with attached media below the related text.
- Captions group correctly; reading order matches LayoutReader; markdown-equivalent content alignment.
- not only this case, I need to handle all case. This is complex task need comprehensive logic to determine chunk.
---

### Old version (kept for reference)

### Goals
- Reduce duplicate/overlapping chunks and ensure each textual line appears once.
- Maximize use of the PDF text layer; resort to OCR only when no glyph coverage exists.
- Enforce page reading order via MonkeyOCR LayoutReader (Relation model) with XY-cut fallback.
- Surface handwriting/figure/OMR content as real text sections; only attach images when explicitly requested.

### Issues observed
- Too many overlapped/duplicated sections across chunks.
- Most sections fell back to OCR; text-layer coverage showed as 0.
- Reading order did not reflect LayoutReader/Relation model output from `model_configs.yaml`.
- Handwriting and multiple-choice (OMR) content did not appear as text sections; one handwriting entry showed as a "Figure" caption only.

### Hypotheses (root causes)
- Coordinate scaling from YOLO detections to PDF units was incorrect (simple division by `zoomin`), causing poor word–block matching.
- Word–block association used a point-in-rectangle heuristic (center-inside) that is fragile for skewed/tilted layouts and tight margins.
- Reading order used naive sort by `(page, top, x)` instead of invoking LayoutReader ordering.
- Figures/handwriting were treated as images only; no handwriting-oriented OCR prompt to convert them into textual sections.
- OMR pipeline was feature-flagged off by default.

### Planned changes
1) Coordinate scaling correctness
   - Keep YOLO outputs in image pixel space; compute precise scale factors per page: `sx = image.width / page.width`, `sy = image.height / page.height`.
   - Convert YOLO pixel bboxes to PDF coordinate units by dividing by `(sx, sy)`; do not divide by `zoomin` directly.

2) Robust word–block association (maximize text-layer usage)
   - Extract words via `pdfplumber.page.extract_words` with tuned tolerances and hyphen merge.
   - Include a word if the word-bbox IoU with the block ≥ 0.2 (not center-inside).
   - Group words into lines by y proximity; join words with spaces; join lines with newline for titles.
   - OCR fallback is only used when the assembled text is empty after word association.

3) Reading order with LayoutReader
   - Call MonkeyOCR Relation/LayoutReader to order line boxes per page.
   - Implementation hook: `MonkeyOCRService.order_lines(page_blocks, page_w, page_h, line_height, model)` invoking logic similar to `magic_pdf.pdf_parse_union_core_v2_llm.sort_lines_by_model` and `do_predict`.
   - Fallback to XY-cut when the page has too many lines or the model declines.

4) Deduplication and NMS for lines
   - After initial merges, run geometric dedup per page:
     - Overlap metric: `overlap = intersection_area / min(area_a, area_b)`; drop the shorter/contained box if `overlap ≥ 0.6`.
   - Textual dedup: within the same page/layout, if normalized strings are identical and horizontal distance < 5% of page width, keep only one.
   - Avoid double-injection of captions: when appending caption/HTML to sections, skip if an existing text box overlaps the caption bbox with overlap ≥ 0.5.

5) Tables, figures, handwriting
   - Captions: search nearest caption blocks with sufficient horizontal overlap; if not found, OCR a narrow region below/above the body.
   - Handwriting: treat `figure` blocks as OCR candidates with a handwriting prompt: "This is a handwriting region. Extract readable text only." If non-empty, inject as a text section (with tags) in addition to optional image.
   - Images: only crop/return when `parser_config.monkeyocr.return_images=true`; otherwise, append text/HTML into sections only.

6) OMR (multiple-choice / circle forms)
   - Enable OMR by default for MonkeyOCR path.
   - Prefilter figure-like blocks by area/aspect; run `MonkeyOCRService.omr_ratings_batch` and inject ratings as text sections with position tags. If OMR-negative, fall back to figure caption path.

7) Section assembly
   - Build sections strictly in the predicted reading order from LayoutReader.
   - Format tags as `@@{page}\t{x0}\t{x1}\t{top}\t{bottom}##` with 1-decimal precision.
   - Preserve newlines for `title` to separate blocks semantically.

8) Logging & metrics
   - Per page: word coverage %, OCR fallback count, dedup count, lines ordered by LayoutReader vs XY-cut, figure/table/OMR counts.
   - Sample the first N joined lines for quick visual inspection.

### Config knobs
- `parser_config.monkeyocr.return_images` (bool, default: false)
- `parser_config.monkeyocr.layout_thr` (float): ignore YOLO blocks with score < thr
- `parser_config.monkeyocr.text_word_iou` (float, default: 0.2)
- `parser_config.monkeyocr.dedupe_overlap_min` (float, default: 0.6)
- `parser_config.monkeyocr.table_html` (bool, default: true)
- `parser_config.monkeyocr.omr.enabled` (bool, default: true)
- `parser_config.monkeyocr.omr.min_area` (float)
- `parser_config.monkeyocr.omr.max_aspect` (float)

### Acceptance criteria
- Text-layer used for the majority of text blocks; OCR fallbacks only when words are absent (e.g., scanned pages, handwriting).
- No obvious duplicate/overlapping sections in the chunk list for the same page.
- Sections follow the visual reading order; titles and paragraphs appear in expected sequence.
- Handwriting and OMR appear as text sections; table HTML shows when `table_html=true`.

### Implementation checklist (files to modify)
1) `monkeydoc/service/model_service.py`
   - Add `order_lines(...)` method that wraps LayoutReader ordering (see `magic_pdf.pdf_parse_union_core_v2_llm.sort_lines_by_model`).
   - Expose a `normalize_layout_blocks(...)` that scales YOLO pixel coordinates to PDF units using per-page `(sx, sy)`.

2) `monkeydoc/parser/pdf_parser.py`
   - Fix scaling: compute `(sx, sy)` from `self.page_images[p].size` and `pdfplumber_page.width/height` captured during `_render_pages`.
   - Replace center-inside with IoU-based word association and update line grouping.
   - Call `MonkeyOCRService.order_lines(...)` to order lines per page, with fallback to XY-cut.
   - Add dedup (geometric + textual) after merges and before section build.
   - For figures: add handwriting OCR prompt path; inject text as section even when not returning images.
   - Switch OMR default on; keep thresholds in `parser_config.monkeyocr.omr`.

3) `rag/app/monkey_ocr_parser.py`
   - Ensure `return_images` defaults to `false` and `omr.enabled` defaults to `true` for MonkeyOCR.
   - Keep the DeepDoc-compatible sections-only path as default; images only when requested.

### Testing
- Run on `5 RNN005(2).pdf` with 2–3 pages:
  - Validate: non-zero word coverage, minimal OCR fallback; verify reading order visually via first 10 sections.
  - Confirm no duplicated sections: check dedup metrics and spot-check chunk list.
  - Handwriting present as text; at least one OMR section appears when applicable.
  - When `return_images=true`, verify that image chunks exist and positions match.

### Rollout & toggles
- Feature guarded by `parser_config.layout_recognize == "MonkeyOCR"`.
- Safe fallback: enhanced-markdown path remains as a backup if parser raises.
- Add `MONKEYOCR_DEV=1` to enable extra diagnostics and optional overlay images (dev only).

### Risks & mitigations
- LayoutReader inference cost on CPU/MPS: limit to pages with ≤ 200 lines; else fallback to XY-cut to keep latency bounded.
- Aggressive dedup might remove legitimate near-duplicates (headers/footers): exclude regions classified as header/footer or near page margins beyond given thresholds.
