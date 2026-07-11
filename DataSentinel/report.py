from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate,
    Table, TableStyle, Paragraph, Spacer)
from reportlab.lib.units import inch
from datetime import datetime
import pandas as pd
import numpy as np

def generate_pdf_report(df, 
                        filename="DataSentinel_Report.pdf"):

    # ── USE LANDSCAPE FOR MORE WIDTH ──
    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(letter),
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    elements = []
    styles = getSampleStyleSheet()

    # ── CUSTOM STYLES ──
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=20,
        textColor=colors.HexColor('#0D1F3C'),
        spaceAfter=6
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#0A7EA4'),
        spaceBefore=16,
        spaceAfter=6
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#1C2333')
    )

    # ── WRAP TEXT HELPER ──
    def wrap(text):
        return Paragraph(str(text), normal_style)

    # ── TITLE ──
    elements.append(Paragraph(
        "🛡️ DataSentinel — Data Quality Report",
        title_style
    ))
    elements.append(Paragraph(
        f"Scanned on: "
        f"{datetime.now().strftime('%d %B %Y, %H:%M')}",
        normal_style
    ))
    elements.append(Spacer(1, 0.2*inch))

    # ── DATASET SUMMARY ──
    elements.append(Paragraph(
        "Dataset Summary", heading_style
    ))

    summary_data = [
        [wrap('Metric'), wrap('Value')],
        [wrap('Total Rows'), 
         wrap(str(df.shape[0]))],
        [wrap('Total Columns'), 
         wrap(str(df.shape[1]))],
        [wrap('Total Cells'), 
         wrap(str(df.shape[0] * df.shape[1]))],
        [wrap('Missing Values'), 
         wrap(str(df.isnull().sum().sum()))],
        [wrap('Duplicate Rows'), 
         wrap(str(df.duplicated().sum()))],
        [wrap('Health Score'), 
         wrap(f"{calculate_health_score(df)}/100")],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[3*inch, 3*inch]
    )
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0),
         colors.HexColor('#0D1F3C')),
        ('TEXTCOLOR', (0,0), (-1,0),
         colors.white),
        ('FONTNAME', (0,0), (-1,0),
         'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ROWBACKGROUNDS', (0,1), (-1,-1),
         [colors.HexColor('#EBF1FB'),
          colors.white]),
        ('GRID', (0,0), (-1,-1),
         0.5, colors.grey),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.2*inch))

    # ── MISSING VALUES ──
    elements.append(Paragraph(
        "Missing Values Report", heading_style
    ))

    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if missing.empty:
        elements.append(Paragraph(
            "✅ No missing values found!",
            normal_style
        ))
    else:
        missing_data = [[
            wrap('Column'),
            wrap('Missing Count'),
            wrap('Missing %'),
            wrap('Status')
        ]]
        for col, count in missing.items():
            pct = round(
                (count / len(df)) * 100, 2
            )
            status = "🔴 High" if pct > 10 else "🟡 Low"
            missing_data.append([
                wrap(col),
                wrap(str(count)),
                wrap(f"{pct}%"),
                wrap(status)
            ])

        # Dynamic column widths
        missing_table = Table(
            missing_data,
            colWidths=[3.5*inch, 1.5*inch,
                      1.5*inch, 1.5*inch]
        )
        missing_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0),
             colors.HexColor('#0A7EA4')),
            ('TEXTCOLOR', (0,0), (-1,0),
             colors.white),
            ('FONTNAME', (0,0), (-1,0),
             'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ROWBACKGROUNDS', (0,1), (-1,-1),
             [colors.HexColor('#EBF1FB'),
              colors.white]),
            ('GRID', (0,0), (-1,-1),
             0.5, colors.grey),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 8),
            ('WORDWRAP', (0,0), (-1,-1), True),
        ]))
        elements.append(missing_table)

    elements.append(Spacer(1, 0.2*inch))

    # ── OUTLIERS ──
    elements.append(Paragraph(
        "Outliers Report", heading_style
    ))

    numeric_cols = df.select_dtypes(
        include=[np.number]).columns
    outlier_data = [[
        wrap('Column'),
        wrap('Outliers Found'),
        wrap('Outlier %'),
        wrap('Status')
    ]]
    found = False

    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = df[
            (df[col] < Q1 - 1.5 * IQR) |
            (df[col] > Q3 + 1.5 * IQR)
        ]
        if len(outliers) > 0:
            pct = round(
                len(outliers)/len(df)*100, 2
            )
            outlier_data.append([
                wrap(col),
                wrap(str(len(outliers))),
                wrap(f"{pct}%"),
                wrap("🟡 Review")
            ])
            found = True

    if not found:
        elements.append(Paragraph(
            "✅ No outliers found!",
            normal_style
        ))
    else:
        outlier_table = Table(
            outlier_data,
            colWidths=[3.5*inch, 1.5*inch,
                      1.5*inch, 1.5*inch]
        )
        outlier_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0),
             colors.HexColor('#0D1F3C')),
            ('TEXTCOLOR', (0,0), (-1,0),
             colors.white),
            ('FONTNAME', (0,0), (-1,0),
             'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ROWBACKGROUNDS', (0,1), (-1,-1),
             [colors.HexColor('#EBF1FB'),
              colors.white]),
            ('GRID', (0,0), (-1,-1),
             0.5, colors.grey),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(outlier_table)

    elements.append(Spacer(1, 0.2*inch))

    # ── SCHEMA TABLE ──
    elements.append(Paragraph(
        "Schema Report", heading_style
    ))

    # Split schema into chunks of 20 columns
    # to avoid overflow
    all_cols = df.columns.tolist()
    chunk_size = 20
    chunks = [all_cols[i:i+chunk_size]
              for i in range(0, len(all_cols),
                            chunk_size)]

    for chunk in chunks:
        schema_data = [[
            wrap('Column Name'),
            wrap('Data Type'),
            wrap('Unique Values'),
            wrap('Null Count'),
            wrap('Sample Value')
        ]]

        for col in chunk:
            try:
                sample = str(df[col].dropna()
                            .iloc[0])[:30]
            except:
                sample = "N/A"

            schema_data.append([
                wrap(str(col)),
                wrap(str(df[col].dtype)),
                wrap(str(df[col].nunique())),
                wrap(str(df[col].isnull()
                             .sum())),
                wrap(sample)
            ])

        # Full width spread across landscape page
        schema_table = Table(
            schema_data,
            colWidths=[2.2*inch, 1.3*inch,
                      1.3*inch, 1.1*inch,
                      2.1*inch]
        )
        schema_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0),
             colors.HexColor('#0A7EA4')),
            ('TEXTCOLOR', (0,0), (-1,0),
             colors.white),
            ('FONTNAME', (0,0), (-1,0),
             'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('ROWBACKGROUNDS', (0,1), (-1,-1),
             [colors.HexColor('#EBF1FB'),
              colors.white]),
            ('GRID', (0,0), (-1,-1),
             0.5, colors.grey),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 6),
            ('WORDWRAP', (0,0), (-1,-1), True),
        ]))
        elements.append(schema_table)
        elements.append(Spacer(1, 0.1*inch))

    elements.append(Spacer(1, 0.2*inch))

    # ── RECOMMENDATIONS ──
    elements.append(Paragraph(
        "Recommendations", heading_style
    ))

    missing_pct = (df.isnull().sum().sum() /
                  (df.shape[0] * df.shape[1])
                  * 100)
    dup_count = df.duplicated().sum()
    score = calculate_health_score(df)
    recs = []

    if missing_pct > 10:
        recs.append(
            "🔴 High missing values — "
            "consider imputation or removal"
        )
    if dup_count > 0:
        recs.append(
            f"🔴 {dup_count} duplicates found "
            f"— remove before analysis"
        )
    if found:
        recs.append(
            "🟡 Outliers detected — "
            "review before running ML models"
        )
    if not recs:
        recs.append(
            "✅ Data looks clean "
            "— ready for analysis!"
        )

    for rec in recs:
        elements.append(Paragraph(
            f"• {rec}", normal_style
        ))
        elements.append(Spacer(1, 0.05*inch))

    # ── FOOTER ──
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(
        "Generated by DataSentinel  |  "
        "github.com/purva-code24/DataSentinel",
        ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey
        )
    ))

    doc.build(elements)
    print(f"✅ PDF saved: {filename}")
    return filename


def calculate_health_score(df):
    score = 100
    missing_pct = (df.isnull().sum().sum() /
                  (df.shape[0] * df.shape[1])
                  * 100)
    score -= missing_pct * 2
    dup_pct = (df.duplicated().sum() /
               len(df) * 100)
    score -= dup_pct * 2
    numeric_cols = df.select_dtypes(
        include=[np.number]).columns
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = df[
            (df[col] < Q1 - 1.5 * IQR) |
            (df[col] > Q3 + 1.5 * IQR)
        ]
        outlier_pct = (len(outliers) /
                      len(df) * 100)
        score -= outlier_pct * 0.5
    return max(0, round(score, 2))