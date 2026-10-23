"""scripts/generate_video_script_pdf.py - Generate a professional PDF of the 3-minute video demo script."""

import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)

def build_pdf():
    docs_dir = Path(__file__).resolve().parent.parent / "docs"
    docs_dir.mkdir(exist_ok=True)
    pdf_path = docs_dir / "AegisMCP_Video_Demo_Script.pdf"

    # Page setup
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    c_primary = HexColor("#1A365D")
    c_secondary = HexColor("#2B6CB0")
    c_dark = HexColor("#2D3748")
    c_accent = HexColor("#DD6B20")
    c_muted = HexColor("#718096")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=c_primary,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=c_muted,
    )

    sec_heading_style = ParagraphStyle(
        "SecHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=HexColor("#FFFFFF"),
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=HexColor("#FFFFFF"),
    )

    col_visual_style = ParagraphStyle(
        "ColVisual",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=11.5,
        textColor=HexColor("#1A202C"),
    )

    col_spoken_style = ParagraphStyle(
        "ColSpoken",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=HexColor("#1A202C"),
    )

    badge_style = ParagraphStyle(
        "BadgeStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=HexColor("#FFFFFF"),
        alignment=1,
    )

    meta_key_style = ParagraphStyle(
        "MetaKey",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=c_secondary,
    )

    meta_val_style = ParagraphStyle(
        "MetaVal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=c_dark,
    )

    elements = []

    # 1. Header Banner
    elements.append(Paragraph("AegisMCP -- 3-Minute Video Demo Script & Storyboard", title_style))
    elements.append(Spacer(1, 3))
    elements.append(Paragraph(
        "Track 2: Household Crisis & Scam Assistant via MCP (Streamable HTTP 2025-11-25) | Amazon Developer Hackathon",
        subtitle_style,
    ))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=0, spaceAfter=8))

    # 2. Production Metadata Table
    meta_data = [
        [
            Paragraph("Target Duration", meta_key_style),
            Paragraph("<b>3:00 Minutes</b> (180 seconds exact)", meta_val_style),
            Paragraph("Speaker Pace", meta_key_style),
            Paragraph("~140 words per minute (brisk, confident)", meta_val_style),
        ],
        [
            Paragraph("Display Resolution", meta_key_style),
            Paragraph("1080p (1920x1080), 100% or 110% zoom", meta_val_style),
            Paragraph("Prerequisites", meta_key_style),
            Paragraph("localhost:8080 (Host) & 127.0.0.1:8000 (FastMCP)", meta_val_style),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[1.3 * inch, 2.4 * inch, 1.3 * inch, 2.5 * inch])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HexColor("#EDF2F7")),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#CBD5E0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 10))

    # Helper function for storyboard segments
    def make_segment(sec_title, time_badge_text, rows):
        seg_elements = []

        # Banner Header for Segment
        banner_table = Table(
            [[
                Paragraph(f"<b>{sec_title}</b>", sec_heading_style),
                Paragraph(f"<b>{time_badge_text}</b>", badge_style),
            ]],
            colWidths=[6.3 * inch, 1.2 * inch],
        )
        banner_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), c_primary),
            ("BACKGROUND", (1, 0), (1, 0), c_accent),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        seg_elements.append(banner_table)

        # Table Header
        header_table = Table(
            [[
                Paragraph("Timing & Visual Action (On-Screen)", table_header_style),
                Paragraph("Spoken Narration (Voiceover Script)", table_header_style),
            ]],
            colWidths=[3.2 * inch, 4.3 * inch],
        )
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), c_secondary),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        seg_elements.append(header_table)

        # Rows
        table_rows = []
        for time_range, visual_text, spoken_text in rows:
            vis_cell = [
                Paragraph(f"<b>[{time_range}]</b>", ParagraphStyle("TMark", fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=c_secondary)),
                Paragraph(visual_text, col_visual_style),
            ]
            spk_cell = [
                Paragraph(spoken_text, col_spoken_style),
            ]
            table_rows.append([vis_cell, spk_cell])

        body_table = Table(table_rows, colWidths=[3.2 * inch, 4.3 * inch])
        ts = [
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#CBD5E0")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]
        # Alternating background colors
        for r_idx in range(len(rows)):
            bg = HexColor("#FFFFFF") if r_idx % 2 == 0 else HexColor("#F7FAFC")
            ts.append(("BACKGROUND", (0, r_idx), (-1, r_idx), bg))

        body_table.setStyle(TableStyle(ts))
        seg_elements.append(body_table)
        seg_elements.append(Spacer(1, 8))
        return KeepTogether(seg_elements)

    # Segment 1
    elements.append(make_segment(
        "Segment 1: The Hook & Architectural Overview",
        "0:00 -- 0:30",
        [
            (
                "0:00 -- 0:12",
                "Fullscreen view of Alexa+ Multimodal Console (localhost:8080). Cursor highlights green 'MCP LIVE' and orange 'DEVICES SIMULATED' status pills.",
                '"When a high-stakes emergency strikes at home -- a water heater rupturing next to electrical panels, or a predatory scammer coercing an elderly parent over the phone -- standard smart assistants fall short. They recite generic web search blurbs while disaster unfolds."',
            ),
            (
                "0:12 -- 0:30",
                "Show FastMCP /healthz endpoint returning spec '2025-11-25'. Pan over Dual-Agent architecture diagram (Analyst vs Responder).",
                '"Meet AegisMCP: an autonomous household crisis assistant and scam firewall for Alexa+. Built on the official 2025-11-25 Streamable HTTP MCP specification, it connects Alexa to a secure local MCP server that arbitrates crises across 11 home categories, acts on smart hardware, parses insurance policies, and protects families."',
            ),
        ],
    ))

    # Segment 2
    elements.append(make_segment(
        "Segment 2: Household Emergency & Semantic Policy RAG",
        "0:30 -- 1:15",
        [
            (
                "0:30 -- 0:45",
                "Select 'Water Heater' scenario. Click microphone button 'Speak Voice Command'. Web Speech API displays continuous speech input.",
                '"Let\'s test an urgent scenario using browser-native live voice capture via the Web Speech API. A resident frantically asks Alexa if they should unbolt their leaking water heater."',
            ),
            (
                "0:45 -- 1:00",
                "Click 'Trigger Alexa+ Emergency Response'. Progress bar completes. IoT containment card renders with checkmarks.",
                '"Instantly, AegisMCP calls arbitrate_home_emergency. Notice what happens in parallel: 1) Life Safety: Alexa immediately warns the user away from standing water near electrical circuits. 2) Reversible Containment: It auto-closes the main water shutoff valve. 3) Hardware Bridge: It dispatches real Matter/Zigbee commands to Home Assistant."',
            ),
            (
                "1:00 -- 1:15",
                "Scroll down to highlight Semantic Policy RAG card (Section 4.2.b) and the Caregiver Emergency Alert card.",
                '"Crucially, our Semantic Policy RAG retrieves Section 4.2.b of the standard HO-3 homeowner policy: quoting their exact $500 deductible, issuing a critical warranty alert -- warning that DIY disassembly voids manufacturer coverage -- and dispatching a priority caregiver SMS alert to family members."',
            ),
        ],
    ))

    # Segment 3
    elements.append(make_segment(
        "Segment 3: Scam Firewall & Carrier-Grade Intelligence",
        "1:15 -- 2:00",
        [
            (
                "1:15 -- 1:30",
                "Switch to 'Scam Firewall' tab. Display Chase bank impersonation transcript demanding wire transfer and Apple gift cards.",
                '"Next, let\'s watch Aegis protect vulnerable residents from predatory social-engineering calls. Here, a caller claims to be Chase Fraud Department, demanding immediate gift card purchases and wire transfers."',
            ),
            (
                "1:30 -- 1:45",
                "Click 'Alexa, verify this caller with Aegis'. Threat gauge shoots to 99% (Critical Scam). Highlight Alexa spoken interjection.",
                '"Within milliseconds, Aegis triggers analyze_live_scam_call. Alexa generates an urgent spoken interjection: warning the resident to hang up immediately and reminding them that financial institutions never demand gift cards or verification codes."',
            ),
            (
                "1:45 -- 2:00",
                "Highlight the Carrier-Grade Line Intelligence card (VoIP detected, NPA-NXX area code) and Caregiver Notification status.",
                '"Under the hood, our Carrier Intelligence engine inspects the NPA-NXX area code, detects that the call originates from a non-geographic virtual VoIP burner line rather than an official bank exchange, and automatically dispatches an emergency warning SMS to the resident\'s caregiver."',
            ),
        ],
    ))

    # Segment 4
    elements.append(make_segment(
        "Segment 4: Tamper-Evident Forensic Claim Dossier",
        "2:00 -- 2:35",
        [
            (
                "2:00 -- 2:18",
                "Click 'Claim Packet' tab. Click 'Compile Forensic Claim Packet'. Blue SHA-256 fingerprint box and ledger path appear.",
                '"Once the crisis is contained, homeowners face another nightmare: fighting insurance claims. In one click, Aegis compiles an insurance-ready forensic claim dossier."',
            ),
            (
                "2:18 -- 2:35",
                "Open compiled claim PDF (out/claim_CLM-xxxx.pdf). Show timestamped sensor curve and SHA-256 cryptographic digest in header/footer.",
                '"Every sensor reading, breaker trip, and timestamped valve actuation is compiled into a formal PDF report. To prevent post-incident spoliation, Aegis cryptographically hashes the packet with SHA-256, commits it to an immutable local audit ledger, and embeds the cryptographic fingerprint in the PDF header for adjusters."',
            ),
        ],
    ))

    # Segment 5
    elements.append(make_segment(
        "Segment 5: MCP Streamable HTTP Wire & Open Source",
        "2:35 -- 3:00",
        [
            (
                "2:35 -- 2:48",
                "Click 'Wire Log' tab on the right panel. Show live POST /mcp transactions with 200 OK and Mcp-Session-Id tracking.",
                '"Everything you just saw is driven purely over the official 2025-11-25 Streamable HTTP MCP wire on /mcp. Our host backend has zero direct imports from the server -- it acts as a pure MCP client communicating via JSON-RPC, protected by custom OriginGuard middleware that blocks DNS-rebinding attacks with HTTP 403."',
            ),
            (
                "2:48 -- 3:00",
                "Click 'Real vs Simulated' tab. Show mcp-streamable-crisis-kit package directory in VS Code / explorer.",
                '"For the Open Source Mini Challenge, we extracted mcp-streamable-crisis-kit, providing turnkey OriginGuard and memory wire logging for any developer. AegisMCP: turning smart homes into proactive guardians when every second counts. Thank you!"',
            ),
        ],
    ))

    # Production Tips Footer Box
    tips_table = Table(
        [[
            Paragraph("<b>Production Recording Tips:</b> Record at 1080p (1920x1080) at 100% zoom. Keep <code>out/</code> open in a file viewer to show the PDF in 1 click. Maintain steady brisk pacing (~140 wpm).", col_visual_style)
        ]],
        colWidths=[7.5 * inch]
    )
    tips_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HexColor("#FEFCBF")),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#D69E2E")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(tips_table)

    doc.build(elements)
    print(f"PDF successfully generated at: {pdf_path}")
    return str(pdf_path)

if __name__ == "__main__":
    build_pdf()
