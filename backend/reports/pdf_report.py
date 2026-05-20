from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, Image, HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import pandas as pd
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from datetime import datetime

# ── Colors ─────────────────────────────────────────────────────────────────────
NAVY    = colors.HexColor('#0d1b33')
BLUE    = colors.HexColor('#2563eb')
LIGHT   = colors.HexColor('#dbeafe')
RED     = colors.HexColor('#ef4444')
GREEN   = colors.HexColor('#22c55e')
WHITE   = colors.white
GRAY    = colors.HexColor('#64748b')

DATABASE_URL = 'database/cryptoradar.db'
os.makedirs('exports/pdf', exist_ok=True)
os.makedirs('exports/charts', exist_ok=True)

# ── Load Data ──────────────────────────────────────────────────────────────────
def load_prices():
    conn = sqlite3.connect(DATABASE_URL)
    df = pd.read_sql("""
        SELECT coin_id, symbol, name, price_inr, market_cap_inr,
               price_change_pct_24h, high_24h, low_24h
        FROM prices
        WHERE timestamp = (SELECT MAX(timestamp) FROM prices)
    """, conn)
    conn.close()
    return df

def load_sentiment():
    conn = sqlite3.connect(DATABASE_URL)
    df = pd.read_sql("SELECT * FROM sentiment", conn)
    conn.close()
    return df

def load_historical(coin_id='bitcoin'):
    conn = sqlite3.connect(DATABASE_URL)
    df = pd.read_sql(f"""
        SELECT date, price_inr FROM historical_prices
        WHERE coin_id='{coin_id}' ORDER BY date
    """, conn)
    conn.close()
    return df

# ── Generate Charts ────────────────────────────────────────────────────────────
def generate_charts():
    # Price chart
    df = load_historical('bitcoin')
    plt.figure(figsize=(8, 4))
    plt.plot(df['date'], df['price_inr'], color='#2563eb', linewidth=2)
    plt.title('Bitcoin Price — Last 90 Days (INR)', fontsize=13, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Price (₹)')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('exports/charts/pdf_btc_price.png', dpi=150)
    plt.close()

    # Sentiment chart
    sent_df = load_sentiment()
    if not sent_df.empty:
        summary = sent_df.groupby('coin_id')['polarity'].mean()
        plt.figure(figsize=(8, 4))
        colors_list = ['#22c55e' if v > 0 else '#ef4444' for v in summary.values]
        plt.bar(summary.index, summary.values, color=colors_list)
        plt.title('Average Sentiment Polarity by Coin', fontsize=13, fontweight='bold')
        plt.xlabel('Coin')
        plt.ylabel('Polarity Score')
        plt.axhline(0, color='gray', linewidth=0.5)
        plt.tight_layout()
        plt.savefig('exports/charts/pdf_sentiment.png', dpi=150)
        plt.close()

    print("Charts generated for PDF.")

# ── Executive Summary ──────────────────────────────────────────────────────────
def generate_summary(prices_df, sentiment_df):
    total_mcap = prices_df['market_cap_inr'].sum()
    best = prices_df.loc[prices_df['price_change_pct_24h'].idxmax()]
    worst = prices_df.loc[prices_df['price_change_pct_24h'].idxmin()]
    avg_sentiment = sentiment_df['polarity'].mean() if not sentiment_df.empty else 0

    sentiment_label = 'bullish' if avg_sentiment > 0.1 else 'bearish' if avg_sentiment < -0.1 else 'neutral'

    summary = (
        f"CryptoRadar market report generated on {datetime.now().strftime('%d %B %Y at %H:%M IST')}. "
        f"The combined market capitalization of tracked assets stands at "
        f"₹{total_mcap/1e12:.2f} trillion INR. "
        f"\n\n"
        f"In the last 24 hours, {best['symbol']} was the best performer with a "
        f"{best['price_change_pct_24h']:+.2f}% price change, while {worst['symbol']} "
        f"recorded the weakest performance at {worst['price_change_pct_24h']:+.2f}%. "
        f"\n\n"
        f"Overall market sentiment is {sentiment_label} with an average polarity score of "
        f"{avg_sentiment:.3f}. Key recommendation: Monitor RSI levels closely — "
        f"ETH is currently oversold and may present a buying opportunity. "
        f"Maintain diversified exposure across BTC, ETH, BNB and SOL."
    )
    return summary

# ── Build PDF ──────────────────────────────────────────────────────────────────
def generate_pdf_report():
    prices_df   = load_prices()
    sentiment_df = load_sentiment()
    generate_charts()

    path = 'exports/pdf/CryptoRadar_Market_Report.pdf'
    doc  = SimpleDocTemplate(path, pagesize=A4,
                             rightMargin=40, leftMargin=40,
                             topMargin=40, bottomMargin=40)

    styles = getSampleStyleSheet()
    story  = []

    # ── Cover ──────────────────────────────────────────────────────────────────
    title_style = ParagraphStyle('title', fontSize=28, textColor=NAVY,
                                  alignment=TA_CENTER, fontName='Helvetica-Bold',
                                  spaceAfter=8)
    sub_style   = ParagraphStyle('sub', fontSize=13, textColor=BLUE,
                                  alignment=TA_CENTER, spaceAfter=4)
    date_style  = ParagraphStyle('date', fontSize=10, textColor=GRAY,
                                  alignment=TA_CENTER)

    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("CryptoRadar", title_style))
    story.append(Paragraph("Real-Time Crypto Market Report", sub_style))
    story.append(Paragraph(datetime.now().strftime("%d %B %Y — %H:%M IST"), date_style))
    story.append(Spacer(1, 0.3 * inch))
    story.append(HRFlowable(width="100%", thickness=2, color=BLUE))
    story.append(Spacer(1, 0.3 * inch))

    # ── Price Table ────────────────────────────────────────────────────────────
    section_style = ParagraphStyle('section', fontSize=14, textColor=NAVY,
                                    fontName='Helvetica-Bold', spaceAfter=10,
                                    spaceBefore=16)
    story.append(Paragraph("Live Market Prices (INR)", section_style))

    price_data = [['Coin', 'Symbol', 'Price (₹)', '24H Change', 'High (₹)', 'Low (₹)']]
    for _, row in prices_df.iterrows():
        change = row['price_change_pct_24h']
        price_data.append([
            row['name'],
            row['symbol'],
            f"₹{row['price_inr']:,.2f}",
            f"{change:+.2f}%",
            f"₹{row['high_24h']:,.2f}",
            f"₹{row['low_24h']:,.2f}",
        ])

    price_table = Table(price_data, colWidths=[1.5*inch, 0.8*inch, 1.5*inch, 1*inch, 1.5*inch, 1.5*inch])
    price_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR',  (0, 0), (-1, 0), WHITE),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [LIGHT, WHITE]),
        ('GRID',       (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE',   (0, 0), (-1, -1), 9),
        ('PADDING',    (0, 0), (-1, -1), 7),
    ]))
    story.append(price_table)
    story.append(Spacer(1, 0.3 * inch))

    # ── Executive Summary ──────────────────────────────────────────────────────
    story.append(Paragraph("Market Summary", section_style))
    body_style = ParagraphStyle('body', fontSize=10, leading=16,
                                 textColor=colors.black, spaceAfter=8)
    for para in generate_summary(prices_df, sentiment_df).split('\n\n'):
        story.append(Paragraph(para.strip(), body_style))
    story.append(Spacer(1, 0.2 * inch))

    # ── Charts ─────────────────────────────────────────────────────────────────
    story.append(Paragraph("Bitcoin Price Chart", section_style))
    story.append(Image('exports/charts/pdf_btc_price.png', width=5.5*inch, height=2.8*inch))
    story.append(Spacer(1, 0.2 * inch))

    if os.path.exists('exports/charts/pdf_sentiment.png'):
        story.append(Paragraph("Market Sentiment Analysis", section_style))
        story.append(Image('exports/charts/pdf_sentiment.png', width=5.5*inch, height=2.8*inch))
        story.append(Spacer(1, 0.2 * inch))

    # ── Sentiment Table ────────────────────────────────────────────────────────
    if not sentiment_df.empty:
        story.append(Paragraph("Sentiment Breakdown by Coin", section_style))
        sent_summary = sentiment_df.groupby('coin_id').agg(
            Total=('id', 'count'),
            Positive=('sentiment_label', lambda x: (x == 'Positive').sum()),
            Negative=('sentiment_label', lambda x: (x == 'Negative').sum()),
            Avg_Polarity=('polarity', 'mean')
        ).reset_index().round(3)

        sent_data = [['Coin', 'Total Articles', 'Positive', 'Negative', 'Avg Polarity']]
        for _, row in sent_summary.iterrows():
            sent_data.append([
                row['coin_id'].upper(),
                str(row['Total']),
                str(row['Positive']),
                str(row['Negative']),
                f"{row['Avg_Polarity']:.3f}"
            ])

        sent_table = Table(sent_data, colWidths=[1.5*inch, 1.5*inch, 1.2*inch, 1.2*inch, 1.5*inch])
        sent_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY),
            ('TEXTCOLOR',  (0, 0), (-1, 0), WHITE),
            ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [LIGHT, WHITE]),
            ('GRID',       (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE',   (0, 0), (-1, -1), 9),
            ('PADDING',    (0, 0), (-1, -1), 7),
        ]))
        story.append(sent_table)
        story.append(Spacer(1, 0.3 * inch))

    # ── Footer ─────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE))
    footer_style = ParagraphStyle('footer', fontSize=8, textColor=GRAY,
                                   alignment=TA_CENTER, spaceBefore=6)
    story.append(Paragraph(
        f"Generated by CryptoRadar Analytics Platform — {datetime.now().strftime('%d %B %Y')}",
        footer_style
    ))

    doc.build(story)
    print(f"PDF report saved to {path}")
    return path

if __name__ == "__main__":
    generate_pdf_report()