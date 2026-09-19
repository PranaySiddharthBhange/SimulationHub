"""Read a complete problem packet, retaining document and page/row context.

No domain classification, entity extraction, value arbitration, or silent
truncation happens here. Large CSV outputs are kept out of generation prompts.
"""

from __future__ import annotations

import base64
import csv
import io
import json
from dataclasses import dataclass, field
from email import policy
from email.parser import BytesParser
from pathlib import Path

import pymupdf
from docx import Document
from openpyxl import load_workbook


@dataclass
class Source:
    path: str
    text: str
    images: list[str] = field(default_factory=list)
    table: list[dict[str, str]] | None = None


@dataclass
class Packet:
    sources: list[Source]

    def render(self, input_tables: set[str] | None = None, max_chars: int = 300000) -> str:
        blocks = []
        for source in self.sources:
            text = source.text
            if source.table is not None and source.path not in (input_tables or set()):
                # A short schedule may be an input. Large trajectories are
                # described by schema only until Stage 1 establishes their role.
                if len(source.table) > 100 or input_tables is not None:
                    text = table_description(source.table)
            blocks.append(f"<source path={json.dumps(source.path)}>\n{text}\n</source>")
        rendered = "\n\n".join(blocks)
        if len(rendered) > max_chars:
            raise ValueError(
                f"Source context is {len(rendered)} characters (limit {max_chars}). "
                "Split the packet into engineering scopes or increase MAX_CONTEXT_CHARS; "
                "no source has been silently truncated."
            )
        return rendered

    def content(self, input_tables: set[str] | None = None, max_chars: int = 300000) -> list[dict]:
        blocks = [{"type": "input_text", "text": self.render(input_tables, max_chars)}]
        for source in self.sources:
            for page, url in enumerate(source.images, 1):
                blocks.extend([
                    {"type": "input_text", "text": f"Visual evidence: {source.path}, image {page}"},
                    {"type": "input_image", "image_url": url, "detail": "high"},
                ])
        return blocks


def table_description(rows: list[dict[str, str]]) -> str:
    columns = list(rows[0]) if rows else []
    return json.dumps({
        "columns": columns, "rows": len(rows),
        "note": "Table values withheld. Declare this an input table only if it supplies the scenario, not expected outputs.",
    }, ensure_ascii=False)


def _image_url(data: bytes, mime: str = "image/png") -> str:
    return f"data:{mime};base64," + base64.b64encode(data).decode("ascii")


def _text(path: Path) -> str:
    data = path.read_bytes()
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16")
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("cp1252")


def read_source(path: Path, name: str | None = None) -> Source:
    name = name or path.name
    ext = path.suffix.lower()
    if ext == ".pdf":
        chunks, images = [], []
        with pymupdf.open(path) as doc:
            if doc.needs_pass:
                raise ValueError("PDF is password protected")
            for number, page in enumerate(doc, 1):
                chunks.append(f"[page {number}]\n{page.get_text(sort=True)}")
                # Preserve scanned pages and embedded/vector diagrams as visual
                # input. Text remains available for exact numbers and citations.
                if not page.get_text().strip() or page.get_images() or page.get_drawings():
                    chunks.append(f"[page {number} also supplied as visual image {len(images) + 1}]")
                    images.append(_image_url(page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5)).tobytes("png")))
        return Source(name, "\n".join(chunks), images)
    if ext in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}:
        # Pillow is installed with python-docx. Normalize unsupported API image
        # types and preserve every page of a multi-page TIFF.
        from PIL import Image, ImageSequence, ImageOps
        images = []
        with Image.open(path) as im:
            for frame in ImageSequence.Iterator(im):
                output = io.BytesIO()
                ImageOps.exif_transpose(frame).convert("RGB").save(output, format="PNG")
                images.append(_image_url(output.getvalue()))
        return Source(name, "Image evidence is attached; read labels, values, arrows and topology.", images)
    if ext in {".xlsx", ".xlsm"}:
        formulas = load_workbook(path, data_only=False)
        cached = load_workbook(path, data_only=True)
        chunks = []
        try:
            for sheet in formulas:
                chunks.append(f"[sheet {sheet.title}]")
                for row in sheet:
                    values = []
                    for cell in row:
                        if cell.value is None:
                            continue
                        value = str(cell.value)
                        if cell.data_type == "f":
                            result = cached[sheet.title][cell.coordinate].value
                            value += f" [cached value={result!r}; formula not recalculated]"
                        values.append(f"{cell.coordinate}={value}")
                    if values:
                        chunks.append(" | ".join(values))
        finally:
            formulas.close()
            cached.close()
        return Source(name, "\n".join(chunks))
    if ext == ".docx":
        doc = Document(path)
        chunks = []
        # Iteration preserves paragraphs interleaved with their tables.
        for item in doc.iter_inner_content():
            if hasattr(item, "text"):
                chunks.append(item.text)
            else:
                chunks.extend(" | ".join(cell.text for cell in row.cells) for row in item.rows)
        images = []
        for relation in doc.part.rels.values():
            if relation.reltype.endswith("/image") and not relation.is_external:
                part = relation.target_part
                images.append(_image_url(part.blob, part.content_type))
        return Source(name, "\n".join(chunks), images)
    if ext == ".eml":
        message = BytesParser(policy=policy.default).parsebytes(path.read_bytes())
        header = "\n".join(f"{key}: {message[key]}" for key in ("From", "Date", "Subject") if message[key])
        body = message.get_body(preferencelist=("plain", "html"))
        return Source(name, header + "\n\n" + (body.get_content() if body else ""))
    if ext in {".csv", ".tsv"}:
        text = _text(path)
        delimiter = "\t" if ext == ".tsv" else ","
        rows = list(csv.DictReader(io.StringIO(text), delimiter=delimiter))
        return Source(name, text, table=rows)
    if ext in {".txt", ".md", ".json", ".xml", ".html", ".htm", ".yaml", ".yml", ".mo", ".sysml", ".puml", ".log"}:
        return Source(name, _text(path))
    raise ValueError(f"Unsupported format {ext or '(no extension)'}; convert it to a supported format first")


def read_packet(root: Path, problem: Path | None = None) -> Packet:
    paths = sorted(p for p in root.rglob("*") if p.is_file()) if root.is_dir() else [root]
    sources, errors = [], []
    for path in paths:
        try:
            sources.append(read_source(path, path.relative_to(root).as_posix() if root.is_dir() else path.name))
        except Exception as exc:
            errors.append(f"{path}: {exc}")
    if problem is not None:
        try:
            sources.insert(0, read_source(problem, "USER_PROBLEM/" + problem.name))
        except Exception as exc:
            errors.append(f"{problem}: {exc}")
    if errors:
        raise ValueError("Input could not be read completely:\n" + "\n".join(errors))
    if not sources:
        raise ValueError(f"No input documents found in {root}")
    return Packet(sources)
