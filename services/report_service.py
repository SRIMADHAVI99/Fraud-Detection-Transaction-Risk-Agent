import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from services.transaction_service import TransactionService

class ReportService:
    @staticmethod
    def generate_pdf_report():
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom ReportLab Styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#0F172A')
        )
        
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#64748B')
        )
        
        heading2_style = ParagraphStyle(
            'Heading2Custom',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#1E293B'),
            spaceBefore=12,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['BodyText'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#334155')
        )

        table_text = ParagraphStyle(
            'TableText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#1E293B')
        )

        elements = []

        # 1. Header Title Banner
        elements.append(Paragraph("🛡️ FRAUDGUARD AI — Security Report", title_style))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Confidential", subtitle_style))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=15))

        # 2. Executive Summary Stats
        stats = TransactionService.get_stats()
        elements.append(Paragraph("1. Executive Summary", heading2_style))
        
        summary_data = [
            [
                Paragraph("<b>Total Payments Analyzed</b>", table_text),
                Paragraph(f"<b>{stats['total_transactions']:,}</b>", table_text),
                Paragraph("<b>Safe Payments</b>", table_text),
                Paragraph(f"<font color='#16A34A'><b>{stats['safe_payments']:,}</b></font>", table_text)
            ],
            [
                Paragraph("<b>Need Checking</b>", table_text),
                Paragraph(f"<font color='#D97706'><b>{stats['need_checking']:,}</b></font>", table_text),
                Paragraph("<b>High Risk Alerts</b>", table_text),
                Paragraph(f"<font color='#DC2626'><b>{stats['fraud_alerts']:,}</b></font>", table_text)
            ],
            [
                Paragraph("<b>Blocked Transactions</b>", table_text),
                Paragraph(f"<b>{stats['blocked_payments']:,}</b>", table_text),
                Paragraph("<b>Under Review</b>", table_text),
                Paragraph(f"<b>{stats['under_review']:,}</b>", table_text)
            ]
        ]
        
        summary_table = Table(summary_data, colWidths=[130, 130, 130, 130])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0,0), (-1,-1), 8),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
            ('ALIGN', (3,0), (3,-1), 'RIGHT'),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 15))

        # 3. Top Suspicious & High Risk Transactions Table
        elements.append(Paragraph("2. Top Suspicious & Flagged Payments", heading2_style))
        elements.append(Paragraph("Below is a record of recent payments flagged by the AI risk engine requiring action or review:", body_style))
        elements.append(Spacer(1, 8))

        suspicious_list = TransactionService.get_suspicious_transactions(per_page=15)['items']
        
        table_headers = [
            Paragraph("<b>TXN ID</b>", table_text),
            Paragraph("<b>Amount</b>", table_text),
            Paragraph("<b>Location</b>", table_text),
            Paragraph("<b>Risk Level</b>", table_text),
            Paragraph("<b>Score</b>", table_text),
            Paragraph("<b>Status</b>", table_text),
            Paragraph("<b>Key Reason</b>", table_text)
        ]
        
        rows = [table_headers]
        for item in suspicious_list:
            risk_color = '#DC2626' if item['risk_level'] == 'HIGH RISK' else '#D97706'
            reason_str = item['reasons'][0] if item['reasons'] else 'Pattern anomaly'
            if len(reason_str) > 40:
                reason_str = reason_str[:37] + "..."

            rows.append([
                Paragraph(item['transaction_id'], table_text),
                Paragraph(f"₹{item['amount']:,.2f}", table_text),
                Paragraph(item['location'], table_text),
                Paragraph(f"<font color='{risk_color}'><b>{item['risk_level']}</b></font>", table_text),
                Paragraph(f"{item['risk_score']}%", table_text),
                Paragraph(item['status'], table_text),
                Paragraph(reason_str, table_text)
            ])

        table = Table(rows, colWidths=[65, 75, 75, 75, 45, 70, 135])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('PADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        
        # Override header text color in table style
        for i in range(len(table_headers)):
            table.setStyle(TableStyle([
                ('TEXTCOLOR', (i,0), (i,0), colors.white)
            ]))
            
        elements.append(table)
        elements.append(Spacer(1, 20))

        # 4. Sign-off Footer
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceAfter=10))
        elements.append(Paragraph("Report generated automatically by FRAUDGUARD AI Risk Engine.", subtitle_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer
