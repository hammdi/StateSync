"""
PDF generator — produces real downloadable government documents.
Uses fpdf2 to create professional official PDFs.
"""

from fpdf import FPDF


def _sanitize(text: str) -> str:
    """Replace Unicode characters not supported by standard PDF fonts."""
    return (
        str(text)
        .replace("\u2014", "-")   # em dash
        .replace("\u2013", "-")   # en dash
        .replace("\u2018", "'")   # left single quote
        .replace("\u2019", "'")   # right single quote
        .replace("\u201c", '"')   # left double quote
        .replace("\u201d", '"')   # right double quote
        .replace("\u2026", "...")  # ellipsis
        .replace("\u2022", "-")   # bullet
        .replace("\u00b2", "2")   # superscript 2
    )


class OfficialPDF(FPDF):
    """A4 official government document."""

    def __init__(self, doc: dict):
        super().__init__(format="A4")
        self.doc = doc
        self._hdr = doc.get("header", {})
        self._ref = doc.get("reference", "")
        self._footer_text = doc.get("footer", "")
        self.set_auto_page_break(auto=True, margin=38)

    # ── Page header ──────────────────────────────────

    def header(self):
        # Outer border
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.4)
        self.rect(8, 8, 194, 281)
        # Inner border
        self.set_line_width(0.15)
        self.rect(10, 10, 190, 277)

        # Country name
        self.set_xy(10, 14)
        self.set_font("Helvetica", "B", 15)
        self.cell(190, 7, self._hdr.get("country", ""), align="C")
        self.ln(8)

        # Decorative double line
        y = self.get_y()
        self.set_draw_color(0, 48, 120)
        self.set_line_width(0.6)
        self.line(35, y, 175, y)
        self.set_line_width(0.2)
        self.line(35, y + 1.5, 175, y + 1.5)
        self.ln(4)

        # Ministry name
        self.set_font("Helvetica", "", 12)
        self.set_text_color(0, 48, 120)
        self.cell(190, 6, self._hdr.get("ministry", ""), align="C")
        self.ln(5)

        # "OFFICIAL DOCUMENT"
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(150, 150, 150)
        self.cell(190, 4, "OFFICIAL DOCUMENT", align="C")
        self.set_text_color(0, 0, 0)
        self.ln(8)

    # ── Page footer ──────────────────────────────────

    def footer(self):
        self.set_y(-36)
        self.set_draw_color(180, 180, 180)
        self.set_line_width(0.2)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(3)

        self.set_font("Helvetica", "I", 6.5)
        self.set_text_color(120, 120, 120)
        # Footer text
        self.multi_cell(180, 3, self._footer_text, align="C")
        self.ln(1)
        # Reference
        self.set_font("Courier", "", 7)
        self.cell(0, 3, f"REF: {self._ref}", align="C")
        self.ln(3)
        # Verification
        vurl = self.doc.get("verification_url", "")
        if vurl:
            self.set_font("Helvetica", "I", 6)
            self.cell(0, 3, f"Verify: {vurl}", align="C")
        self.set_text_color(0, 0, 0)

    # ── Build the full PDF ───────────────────────────

    def build(self) -> bytes:
        self.add_page()

        # Document title
        self.set_font("Helvetica", "B", 20)
        self.cell(180, 10, self.doc.get("title", ""), align="C")
        self.ln(6)

        # Reference & date bar
        self.set_font("Helvetica", "", 8)
        self.set_text_color(100, 100, 100)
        parts = [f"Ref: {self._ref}", f"Issued: {self.doc.get('issued_date', '')}"]
        if self.doc.get("valid_until"):
            parts.append(f"Valid until: {self.doc['valid_until']}")
        self.cell(180, 5, "   |   ".join(parts), align="C")
        self.set_text_color(0, 0, 0)
        self.ln(10)

        # Citizen info box
        citizen = self.doc.get("citizen", {})
        if citizen:
            self._draw_citizen_box(citizen)
            self.ln(6)

        # Content sections
        for section in self.doc.get("sections", []):
            self._draw_section(section)

        # Signature block
        self._draw_signature()

        return bytes(self.output())

    # ── Citizen info box ─────────────────────────────

    def _draw_citizen_box(self, c: dict):
        y0 = self.get_y()
        self.set_fill_color(245, 247, 250)
        self.rect(15, y0, 180, 22, style="F")
        self.set_xy(18, y0 + 2)

        self.set_font("Helvetica", "B", 8)
        self.set_text_color(80, 80, 80)
        self.cell(30, 4, "CITIZEN:")
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(0, 0, 0)
        self.cell(100, 4, c.get("full_name", ""))
        self.ln(5)
        self.set_x(18)

        self.set_font("Helvetica", "", 8)
        self.set_text_color(80, 80, 80)
        items = [
            f"CIN: {c.get('cin', '')}",
            f"Born: {c.get('birth_date', '')}",
            f"Nationality: {c.get('nationality', '')}",
        ]
        self.cell(180, 4, "     ".join(items))
        self.set_text_color(0, 0, 0)
        self.set_y(y0 + 24)

    # ── Section rendering ────────────────────────────

    def _draw_section(self, sec: dict):
        heading = sec.get("heading", "")

        # Check page space
        if self.get_y() > 240:
            self.add_page()

        # Section heading bar
        self.set_fill_color(0, 48, 120)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 9)
        self.cell(180, 7, f"  {heading}", fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(4)

        # Key-value fields
        if sec.get("fields"):
            for label, value in sec["fields"]:
                self.set_font("Helvetica", "", 9)
                self.set_text_color(100, 100, 100)
                self.cell(55, 6, _sanitize(f"  {label}"))
                self.set_font("Helvetica", "B", 9)
                self.set_text_color(0, 0, 0)
                self.cell(125, 6, _sanitize(str(value)) if value else "N/A")
                self.ln()

        # Free text paragraph
        if sec.get("text"):
            self.ln(2)
            self.set_font("Helvetica", "", 10)
            self.set_x(15)
            self.multi_cell(180, 5.5, _sanitize(sec["text"]))

        # Bullet list
        if sec.get("list"):
            self.ln(1)
            self.set_font("Helvetica", "", 9)
            for item in sec["list"]:
                self.set_x(20)
                self.cell(4, 5, "-")
                self.multi_cell(166, 5, _sanitize(item))

        self.ln(4)

    # ── Signature block ──────────────────────────────

    def _draw_signature(self):
        if self.get_y() > 230:
            self.add_page()

        self.ln(10)
        self.set_font("Helvetica", "", 9)
        self.cell(90, 5, f"  Issued on: {self.doc.get('issued_date', '')}")
        self.ln(20)

        # Right-aligned signature block
        self.set_x(120)
        self.set_draw_color(0, 0, 0)
        self.line(125, self.get_y(), 190, self.get_y())
        self.ln(2)
        self.set_x(120)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(80, 80, 80)
        self.cell(70, 4, "Authorized Signature & Official Seal", align="C")
        self.set_text_color(0, 0, 0)


def _sanitize_deep(obj):
    """Recursively sanitize all strings in a nested structure."""
    if isinstance(obj, str):
        return _sanitize(obj)
    if isinstance(obj, dict):
        return {k: _sanitize_deep(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_deep(i) for i in obj]
    return obj


def generate_pdf(doc_content: dict) -> bytes:
    """Generate a professional PDF from document content."""
    clean = _sanitize_deep(doc_content)
    pdf = OfficialPDF(clean)
    return pdf.build()
