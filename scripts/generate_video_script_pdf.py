"""scripts/generate_video_script_pdf.py - Generate a clean, smooth, spoken-language PDF script."""

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

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.45 * inch,
        bottomMargin=0.45 * inch,
    )

    styles = getSampleStyleSheet()

    c_primary = HexColor("#1A365D")
    c_secondary = HexColor("#2B6CB0")
    c_dark = HexColor("#2D3748")
    c_accent = HexColor("#C05621")
    c_muted = HexColor("#718096")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=c_primary,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=c_muted,
    )

    sec_heading_style = ParagraphStyle(
        "SecHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=HexColor("#FFFFFF"),
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=HexColor("#FFFFFF"),
    )

    col_visual_style = ParagraphStyle(
        "ColVisual",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=HexColor("#2D3748"),
    )

    col_spoken_style = ParagraphStyle(
        "ColSpoken",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
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
        fontSize=8,
        leading=10,
        textColor=c_secondary,
    )

    meta_val_style = ParagraphStyle(
        "MetaVal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=c_dark,
    )

    elements = []

    # 1. Header Banner
    elements.append(Paragraph("AegisMCP -- 3-Minute Video Demo Script (Smooth & Conversational)", title_style))
    elements.append(Spacer(1, 2))
    elements.append(Paragraph(
        "Track 2: Household Crisis & Scam Assistant via MCP | Simple, natural spoken English for smooth presentation",
        subtitle_style,
    ))
    elements.append(Spacer(1, 6))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=0, spaceAfter=6))

    # 2. Production Metadata Table
    meta_data = [
        [
            Paragraph("Duration", meta_key_style),
            Paragraph("<b>3 Minutes</b> (180 seconds)", meta_val_style),
            Paragraph("Speaking Style", meta_key_style),
            Paragraph("Simple, conversational, friendly and clear", meta_val_style),
        ],
        [
            Paragraph("Screen Setup", meta_key_style),
            Paragraph("localhost:8080 (1080p, 100% zoom)", meta_val_style),
            Paragraph("Key Click Actions", meta_key_style),
            Paragraph("Emergency Trigger -> Scam Verify -> Claim Packet", meta_val_style),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[1.1 * inch, 2.6 * inch, 1.2 * inch, 2.6 * inch])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HexColor("#EDF2F7")),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#CBD5E0")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 8))

    def make_segment(sec_title, time_badge_text, rows):
        seg_elements = []

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
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        seg_elements.append(banner_table)

        header_table = Table(
            [[
                Paragraph("What To Show On Screen", table_header_style),
                Paragraph("What To Say (Smooth Spoken Script)", table_header_style),
            ]],
            colWidths=[2.9 * inch, 4.6 * inch],
        )
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), c_secondary),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        seg_elements.append(header_table)

        table_rows = []
        for time_range, visual_text, spoken_text in rows:
            vis_cell = [
                Paragraph(f"<b>[{time_range}]</b>", ParagraphStyle("TMark", fontName="Helvetica-Bold", fontSize=7.5, leading=9, textColor=c_secondary)),
                Paragraph(visual_text, col_visual_style),
            ]
            spk_cell = [
                Paragraph(spoken_text, col_spoken_style),
            ]
            table_rows.append([vis_cell, spk_cell])

        body_table = Table(table_rows, colWidths=[2.9 * inch, 4.6 * inch])
        ts = [
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#CBD5E0")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]
        for r_idx in range(len(rows)):
            bg = HexColor("#FFFFFF") if r_idx % 2 == 0 else HexColor("#F7FAFC")
            ts.append(("BACKGROUND", (0, r_idx), (-1, r_idx), bg))

        body_table.setStyle(TableStyle(ts))
        seg_elements.append(body_table)
        seg_elements.append(Spacer(1, 6))
        return KeepTogether(seg_elements)

    # Segment 1
    elements.append(make_segment(
        "Part 1: The Problem & What AegisMCP Does",
        "0:00 -- 0:30",
        [
            (
                "0:00 -- 0:15",
                "Show localhost:8080 on screen. Point cursor at the title and the green 'MCP LIVE' badge at the top right.",
                '"Hi everyone! When a real crisis happens at home -- like a broken water heater flooding your basement, or a scammer on the phone tricking an elderly parent -- regular voice assistants can\'t really help. They just read out generic search results while the damage keeps getting worse."',
            ),
            (
                "0:15 -- 0:30",
                "Scroll across the 11 emergency buttons (Water Heater, Gas Leak, Electrical Surge, Fire, etc.).",
                '"That\'s why we built AegisMCP: a smart crisis assistant and scam firewall for Alexa+. Powered by the Model Context Protocol, Aegis doesn\'t just talk -- it takes action. It protects life safety, shuts off dangerous valves, checks your insurance policy, and alerts your family."',
            ),
        ],
    ))

    # Segment 2
    elements.append(make_segment(
        "Part 2: Live Emergency & Insurance Check",
        "0:30 -- 1:15",
        [
            (
                "0:30 -- 0:45",
                "Select 'Water Heater'. Click 'Speak Voice Command'. Show the question in the text box.",
                '"Let\'s see it in action. I can simply click the mic and speak naturally: \'Alexa, my water heater just burst and water is flooding the basement! Should I try to unscrew the valve myself?\' Now, I click Trigger Response."',
            ),
            (
                "0:45 -- 1:00",
                "Click blue button 'Trigger Alexa+ Emergency Response'. Point to the green checkmarks and safety instructions.",
                '"Look at what happens in seconds: First, safety: Alexa warns the user to stay away from the water to avoid electric shock. Second, containment: it automatically sends a command to shut the main water valve to stop the flooding. It can even control real smart home valves through Home Assistant."',
            ),
            (
                "1:00 -- 1:15",
                "Scroll to show the Policy RAG box ($500 deductible) and the Caregiver Alert box.",
                '"Third, it reads our actual home insurance policy. It finds the exact clause, quotes our 500-dollar deductible, and gives a crucial warning: \'Do not take apart the heater yourself, or you will void your warranty.\' At the same time, it sends an emergency SMS to a family caregiver."',
            ),
        ],
    ))

    # Segment 3
    elements.append(make_segment(
        "Part 3: Scam Firewall & Phone Number Inspection",
        "1:15 -- 2:00",
        [
            (
                "1:15 -- 1:30",
                "Click 'Scam Firewall' tab. Show the Chase bank impersonation text demanding gift cards.",
                '"Now let\'s check out the Scam Firewall. Here is a common phone scam: a caller claims to be from Chase Bank, threatening that your account is frozen unless you buy Apple gift cards right now."',
            ),
            (
                "1:30 -- 1:45",
                "Click 'Alexa, verify this caller with Aegis'. Watch the threat gauge spike to 99% red.",
                '"I click \'Verify Caller\'. Instantly, Aegis analyzes the conversation. The threat gauge shoots up to 99% -- Critical Scam! Alexa speaks up with an urgent warning: \'Hang up right now. Banks will never ask for gift cards or secret codes.\'"',
            ),
            (
                "1:45 -- 2:00",
                "Highlight the Carrier Intelligence box (VoIP detected) and the Caregiver Alert.",
                '"Even better, Aegis inspects the caller\'s phone number. It detects that the call is coming from an untrusted internet VoIP burner line -- not a real bank. And once again, it instantly sends an alert to the family caregiver so no one gets tricked."',
            ),
        ],
    ))

    # Segment 4
    elements.append(make_segment(
        "Part 4: One-Click Insurance Claim Dossier",
        "2:00 -- 2:30",
        [
            (
                "2:00 -- 2:15",
                "Click 'Claim Packet' tab. Click 'Compile Forensic Claim Packet'. Blue SHA-256 box appears.",
                '"After an emergency, dealing with insurance paperwork is a nightmare. With Aegis, you just click \'Compile Forensic Claim Packet\'. In one second, it generates a complete insurance claim report."',
            ),
            (
                "2:15 -- 2:30",
                "Open the generated PDF from out/ folder to show the table and footer.",
                '"It pulls together sensor logs, timestamps, valve shutoff times, and photos into a clean PDF document for the insurance adjuster. To prove the data is real and hasn\'t been altered, Aegis gives it a unique digital security fingerprint using SHA-256."',
            ),
        ],
    ))

    # Segment 5
    elements.append(make_segment(
        "Part 5: Under the Hood & Wrap-up",
        "2:30 -- 3:00",
        [
            (
                "2:30 -- 2:45",
                "Click 'Wire Log' tab on the right. Show the real HTTP POST /mcp entries with 200 OK.",
                '"Finally, look at the Wire Log tab on the right. Everything you just saw runs on the official 2025-11-25 Streamable HTTP MCP standard. Our frontend and server talk purely through secure JSON-RPC over the wire, protected against malicious web attacks."',
            ),
            (
                "2:45 -- 3:00",
                "Click 'Real vs Simulated' tab. Conclude with a warm smile and thank the judges.",
                '"We also open-sourced our crisis security kit on GitHub so any developer can use it. AegisMCP turns smart homes into proactive guardians when every second counts. Thank you!"',
            ),
        ],
    ))

    # Helpful Prompt Box
    tips_table = Table(
        [[
            Paragraph("<b>Presentation Tip:</b> Speak naturally just like talking to a friend. Pause for 1 second after each click so the viewer can see the UI change before you explain it.", col_visual_style)
        ]],
        colWidths=[7.5 * inch]
    )
    tips_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HexColor("#FEFCBF")),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#D69E2E")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(tips_table)

    doc.build(elements)
    print(f"Simple PDF generated at: {pdf_path}")
    return str(pdf_path)

if __name__ == "__main__":
    build_pdf()
