from io import BytesIO
from pathlib import Path
import os
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.shared import Inches, Pt
from fpdf import FPDF

from utils.text_utils import sanitize_text


BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_DIR / "assets" / "logo.png"


def _safe_filename(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip())
    return value.strip("_") or "document"


def format_txt(text: str) -> bytes:
    return sanitize_text(text).encode("utf-8")


def format_docx(text: str, doc_type: str) -> bytes:
    document = Document()
    section = document.sections[0]
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.9)
    section.right_margin = Inches(0.9)

    if LOGO_PATH.exists():
        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.add_run().add_picture(str(LOGO_PATH), width=Inches(1.2))

    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(doc_type.upper())
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(16)

    for raw_block in sanitize_text(text).split("\n\n"):
        block = raw_block.strip()
        if not block:
            continue

        lines = block.splitlines()
        first = lines[0].strip()

        if _is_heading(first):
            p = document.add_paragraph()
            run = p.add_run(first)
            run.bold = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)
            if len(lines) > 1:
                _add_body_paragraph(document, "\n".join(lines[1:]))
        else:
            _add_body_paragraph(document, block)

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_run = footer.add_run("LegalEase — Draft for review")
    footer_run.font.name = "Times New Roman"
    footer_run.font.size = Pt(9)

    output = BytesIO()
    document.save(output)
    return output.getvalue()


def _add_body_paragraph(document: Document, text: str) -> None:
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(7)

    run = paragraph.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(11)


def _is_heading(line: str) -> bool:
    return (
        bool(re.match(r"^\d+[\.\)]\s+", line))
        or (
            len(line) < 90
            and line == line.upper()
            and any(char.isalpha() for char in line)
        )
    )


class LegalEasePDF(FPDF):
    def __init__(self, doc_type: str):
        super().__init__()
        self.doc_type = doc_type

    def header(self):
        if LOGO_PATH.exists():
            try:
                self.image(str(LOGO_PATH), x=90, y=8, w=30)
                self.set_y(28)
            except Exception:
                self.set_y(10)
        else:
            self.set_y(10)

        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, self.doc_type.upper(), align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 8)
        self.cell(
            0,
            8,
            "LegalEase — Draft for review | Page " + str(self.page_no()),
            align="C",
        )


def format_pdf(text: str, doc_type: str) -> bytes:
    pdf = LegalEasePDF(doc_type)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    clean = sanitize_text(text)

    for block in clean.split("\n\n"):
        block = block.strip()
        if not block:
            continue

        lines = block.splitlines()
        first = lines[0].strip()

        if _is_heading(first):
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 7, first)
            if len(lines) > 1:
                pdf.set_font("Helvetica", "", 10)
                pdf.multi_cell(0, 6, "\n".join(lines[1:]))
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 6, block)

        pdf.ln(2)

    return bytes(pdf.output())


def get_download_name(doc_type: str, extension: str) -> str:
    return f"{_safe_filename(doc_type)}.{{extension}}".format(extension=extension)
