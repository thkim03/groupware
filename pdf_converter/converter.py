"""PDF to Markdown converter core logic using PyMuPDF."""

import os
import re
from pathlib import Path

import fitz  # PyMuPDF


def extract_images(page: fitz.Page, output_dir: Path, page_num: int) -> list[dict]:
    """Extract images from a PDF page and save them to disk."""
    images = []
    image_list = page.get_images(full=True)

    for img_idx, img_info in enumerate(image_list):
        xref = img_info[0]
        try:
            base_image = page.parent.extract_image(xref)
        except Exception:
            continue

        image_ext = base_image["ext"]
        image_bytes = base_image["image"]
        image_name = f"page{page_num + 1}_img{img_idx + 1}.{image_ext}"
        image_path = output_dir / image_name

        with open(image_path, "wb") as f:
            f.write(image_bytes)

        images.append({"name": image_name, "path": str(image_path)})

    return images


def classify_block_as_heading(block_text: str, font_size: float, flags: int) -> int:
    """Heuristic to classify text blocks as heading levels based on font size and style."""
    is_bold = bool(flags & 2**4)
    text = block_text.strip()

    if not text:
        return 0

    if font_size >= 24:
        return 1
    elif font_size >= 18:
        return 2
    elif font_size >= 14 and is_bold:
        return 3
    elif font_size >= 12 and is_bold:
        return 4

    return 0


def process_text_block(block: dict) -> str:
    """Process a text block from PyMuPDF and return markdown-formatted text."""
    lines_md = []
    for line in block.get("lines", []):
        line_text_parts = []
        max_font_size = 0
        flags = 0

        for span in line.get("spans", []):
            text = span.get("text", "")
            if not text.strip():
                continue
            span_flags = span.get("flags", 0)
            span_size = span.get("size", 12)
            flags |= span_flags
            max_font_size = max(max_font_size, span_size)

            is_bold = bool(span_flags & 2**4)
            is_italic = bool(span_flags & 2**1)

            if is_bold and is_italic:
                text = f"***{text}***"
            elif is_bold:
                text = f"**{text}**"
            elif is_italic:
                text = f"*{text}*"

            line_text_parts.append(text)

        line_text = "".join(line_text_parts).strip()
        if not line_text:
            continue

        heading_level = classify_block_as_heading(line_text, max_font_size, flags)
        if heading_level > 0:
            clean_text = re.sub(r"\*+([^*]+)\*+", r"\1", line_text)
            line_text = f"{'#' * heading_level} {clean_text}"

        lines_md.append(line_text)

    return "\n".join(lines_md)


def detect_table_blocks(page: fitz.Page) -> list[list[list[str]]]:
    """Attempt to detect and extract tables from a page."""
    tables = []
    try:
        tab_finder = page.find_tables()
        if tab_finder and tab_finder.tables:
            for table in tab_finder.tables:
                extracted = table.extract()
                if extracted:
                    tables.append(extracted)
    except Exception:
        pass
    return tables


def table_to_markdown(table_data: list[list[str]]) -> str:
    """Convert a 2D table to a Markdown table string."""
    if not table_data or not table_data[0]:
        return ""

    col_count = max(len(row) for row in table_data)
    normalized = []
    for row in table_data:
        cells = [(cell or "").strip().replace("\n", " ") for cell in row]
        while len(cells) < col_count:
            cells.append("")
        normalized.append(cells)

    header = normalized[0]
    lines = ["| " + " | ".join(header) + " |"]
    lines.append("| " + " | ".join(["---"] * col_count) + " |")

    for row in normalized[1:]:
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)


def convert_pdf_to_markdown(
    pdf_path: str,
    output_md_path: str | None = None,
    extract_imgs: bool = True,
    progress_callback=None,
) -> str:
    """
    Convert a PDF file to Markdown format.

    Args:
        pdf_path: Path to the input PDF file.
        output_md_path: Path for the output .md file. If None, uses same name as PDF.
        extract_imgs: Whether to extract and save images.
        progress_callback: Optional callable(current_page, total_pages) for progress updates.

    Returns:
        The generated Markdown content as a string.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if output_md_path is None:
        output_md_path = pdf_path.with_suffix(".md")
    else:
        output_md_path = Path(output_md_path)

    images_dir = output_md_path.parent / f"{output_md_path.stem}_images"
    if extract_imgs:
        images_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(pdf_path))
    total_pages = len(doc)
    markdown_parts = []

    for page_num in range(total_pages):
        page = doc[page_num]

        if page_num > 0:
            markdown_parts.append("\n---\n")

        tables = detect_table_blocks(page)
        for table_data in tables:
            table_md = table_to_markdown(table_data)
            if table_md:
                markdown_parts.append(f"\n{table_md}\n")

        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
        for block in blocks:
            if block["type"] == 0:  # text block
                text_md = process_text_block(block)
                if text_md.strip():
                    markdown_parts.append(text_md + "\n")

        if extract_imgs:
            images = extract_images(page, images_dir, page_num)
            for img in images:
                rel_path = os.path.relpath(img["path"], output_md_path.parent)
                markdown_parts.append(f"\n![{img['name']}]({rel_path})\n")

        if progress_callback:
            progress_callback(page_num + 1, total_pages)

    doc.close()

    markdown_content = "\n".join(markdown_parts)
    markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)

    output_md_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    if extract_imgs and images_dir.exists() and not any(images_dir.iterdir()):
        images_dir.rmdir()

    return markdown_content
