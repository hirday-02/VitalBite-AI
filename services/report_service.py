
"""
VitalBite AI — PDF Report Generation Service

Generates formatted PDF reports using ReportLab.
Includes beta indicators and medical safety disclaimers.
Safely handles user-generated text and basic Markdown formatting.
"""

import html
import io
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import (
        getSampleStyleSheet,
        ParagraphStyle,
    )
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        HRFlowable,
        KeepTogether,
    )

    REPORTLAB_AVAILABLE = True

except ImportError:
    REPORTLAB_AVAILABLE = False


class ReportService:
    """Generate safe, readable PDF reports."""

    @staticmethod
    def _escape_text(value: Any) -> str:
        """Escape untrusted text for ReportLab's paragraph parser."""
        return html.escape(str(value), quote=False)

    @staticmethod
    def _format_markdown_inline(text: str) -> str:
        """
        Convert basic Markdown inline formatting into ReportLab markup.

        Text is escaped before formatting, so raw HTML in user input
        cannot introduce arbitrary ReportLab tags.
        """
        safe_text = ReportService._escape_text(text)

        # Bold: **text**
        safe_text = re.sub(
            r"\*\*(.+?)\*\*",
            r"<b>\1</b>",
            safe_text,
        )

        # Italic: *text* or _text_
        safe_text = re.sub(
            r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)",
            r"<i>\1</i>",
            safe_text,
        )
        safe_text = re.sub(
            r"(?<!\w)_(?!\s)(.+?)(?<!\s)_(?!\w)",
            r"<i>\1</i>",
            safe_text,
        )

        # Convert Markdown inline code to plain monospace markup.
        safe_text = re.sub(
            r"`([^`]+)`",
            r'<font name="Courier">\1</font>',
            safe_text,
        )

        return safe_text

    @staticmethod
    def generate_pdf_report(
        title: str,
        report_type: str,
        content_text: str,
        user_name: str = "User",
        profile: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        """
        Generate a downloadable PDF report as bytes.

        The optional profile argument is retained for compatibility.
        """
        now = datetime.now(timezone.utc)
        now_str = now.strftime("%Y-%m-%d %H:%M UTC")

        if not REPORTLAB_AVAILABLE:
            fallback_text = (
                "VITALBITE AI - BETA REPORT\n"
                f"{title}\n\n"
                f"Patient: {user_name}\n"
                f"Report type: {report_type}\n"
                f"Date: {now_str}\n\n"
                f"{content_text}\n\n"
                "DISCLAIMER: Educational purposes only. "
                "This is not a medical diagnosis or prescription."
            )
            return fallback_text.encode("utf-8")

        buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=42,
            bottomMargin=48,
            title=str(title),
            author="VitalBite AI",
        )

        styles = getSampleStyleSheet()

        header_style = ParagraphStyle(
            "VitalBiteReportHeader",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=25,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#1E3A8A"),
            spaceAfter=4,
        )

        subtitle_style = ParagraphStyle(
            "VitalBiteReportSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#0D9488"),
        )

        body_style = ParagraphStyle(
            "VitalBiteReportBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#1E293B"),
            spaceAfter=3,
            splitLongWords=True,
        )

        section_style = ParagraphStyle(
            "VitalBiteReportSection",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#0D9488"),
            spaceBefore=8,
            spaceAfter=5,
            keepWithNext=True,
        )

        bullet_style = ParagraphStyle(
            "VitalBiteReportBullet",
            parent=body_style,
            leftIndent=14,
            firstLineIndent=-10,
            spaceAfter=4,
        )

        disclaimer_style = ParagraphStyle(
            "VitalBiteReportDisclaimer",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#64748B"),
        )

        story = []

        # 1. Report heading.
        story.append(
            Paragraph("VitalBite AI — Beta", subtitle_style)
        )
        story.append(Spacer(1, 5))
        story.append(
            Paragraph(
                ReportService._escape_text(title),
                header_style,
            )
        )
        story.append(
            HRFlowable(
                width="100%",
                thickness=1.4,
                color=colors.HexColor("#1E3A8A"),
                spaceBefore=5,
                spaceAfter=12,
            )
        )

        # 2. Metadata.
        safe_user_name = ReportService._escape_text(user_name)
        safe_report_type = ReportService._escape_text(
            str(report_type).capitalize()
        )

        meta_data = [
            [
                Paragraph(
                    f"<b>Patient Name:</b> {safe_user_name}",
                    body_style,
                ),
                Paragraph(
                    f"<b>Date:</b> {now_str}",
                    body_style,
                ),
            ],
            [
                Paragraph(
                    f"<b>Report Type:</b> {safe_report_type}",
                    body_style,
                ),
                Paragraph(
                    "<b>Status:</b> Beta informational summary",
                    body_style,
                ),
            ],
        ]

        meta_table = Table(
            meta_data,
            colWidths=[266, 266],
            hAlign="LEFT",
        )
        meta_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        colors.HexColor("#F8FAFC"),
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor("#E2E8F0"),
                    ),
                    (
                        "INNERGRID",
                        (0, 0),
                        (-1, -1),
                        0.35,
                        colors.HexColor("#E2E8F0"),
                    ),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )

        story.append(meta_table)
        story.append(Spacer(1, 15))

        # 3. Main content.
        for raw_line in str(content_text or "").splitlines():
            line = raw_line.strip()

            if not line:
                story.append(Spacer(1, 5))
                continue

            # Markdown horizontal rules.
            if re.fullmatch(r"[-*_]{3,}", line):
                story.append(
                    HRFlowable(
                        width="100%",
                        thickness=0.5,
                        color=colors.HexColor("#CBD5E1"),
                        spaceBefore=4,
                        spaceAfter=7,
                    )
                )
                continue

            # Headings: #, ##, ###, etc.
            heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if heading_match:
                heading_text = (
                    ReportService._format_markdown_inline(
                        heading_match.group(2).strip()
                    )
                )
                story.append(
                    Paragraph(heading_text, section_style)
                )
                continue

            # Unordered Markdown bullets.
            bullet_match = re.match(r"^(?:[-*+])\s+(.+)$", line)
            if bullet_match:
                bullet_text = (
                    ReportService._format_markdown_inline(
                        bullet_match.group(1)
                    )
                )
                story.append(
                    Paragraph(
                        f"&bull;&nbsp;&nbsp;{bullet_text}",
                        bullet_style,
                    )
                )
                continue

            # Numbered Markdown lists.
            numbered_match = re.match(r"^(\d+)[.)]\s+(.+)$", line)
            if numbered_match:
                number = numbered_match.group(1)
                item_text = (
                    ReportService._format_markdown_inline(
                        numbered_match.group(2)
                    )
                )
                story.append(
                    Paragraph(
                        f"{number}.&nbsp;&nbsp;{item_text}",
                        bullet_style,
                    )
                )
                continue

            # Normal text, including the original Tension Headache case.
            formatted_line = ReportService._format_markdown_inline(line)
            story.append(
                Paragraph(formatted_line, body_style)
            )

        # 4. Medical disclaimer.
        story.append(Spacer(1, 14))
        story.append(
            HRFlowable(
                width="100%",
                thickness=0.5,
                color=colors.HexColor("#CBD5E1"),
                spaceAfter=9,
            )
        )

        disclaimer_text = (
            "<b>IMPORTANT MEDICAL DISCLAIMER:</b> "
            "Generated by VitalBite AI — Beta. This report is for "
            "general educational and personal reference purposes only. "
            "It is not an official hospital medical record, clinical "
            "diagnostic report, or prescription. Always consult a "
            "licensed healthcare professional for medical diagnosis "
            "and treatment decisions."
        )

        story.append(
            Paragraph(disclaimer_text, disclaimer_style)
        )

        # Build the PDF and return its bytes.
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
