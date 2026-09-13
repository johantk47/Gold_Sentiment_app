import streamlit as st
import pandas as pd
import feedparser
import requests
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from urllib.parse import quote

# Konfigurasi Halaman Web
st.set_page_config(page_title="Gold Sentiment Analyzer", layout="wide", page_icon="🥇")

# Inisialisasi VADER
analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    scores = analyzer.polarity_scores(text)
    polarity = scores['compound']
    if polarity > 0.05:
        sentiment = 'Bullish'
    elif polarity < -0.05:
        sentiment = 'Bearish'
    else:
        sentiment = 'Neutral'
    return polarity, sentiment

# Bagian Header / Judul
st.title("🥇 Gold Market Sentiment Analyzer")
st.write("Aplikasi ini mengambil berita terbaru tentang emas dari Google News dan menganalisis sentimen pasarnya.")

# Tombol Mulai
if st.button("Mulai Analisis Berita", type="primary"):
    
    # Menampilkan animasi loading
    with st.spinner("Sedang mengambil dan menganalisis data dari Google News... Mohon tunggu."):
        
        queries = [
            "gold market", "gold price", "gold news", 
            "gold trends", "gold analysis", "gold forecast", "gold investment"
        ]
        num_articles_per_query = 10
        
        data = []
        summary = {"Bullish": 0, "Bearish": 0, "Neutral": 0}
        article_count = 0

        # Proses Scraping
        for query in queries:
            rss_url = f"https://news.google.com/rss/search?q={quote(query)}"
            feed = feedparser.parse(rss_url)
            news_items = feed.entries[:num_articles_per_query]

            for item in news_items:
                article_count += 1
                title = item.title
                published = item.published
                
                # Analisis Sentimen pada Judul
                polarity, sentiment = analyze_sentiment(title)
                summary[sentiment] += 1
                
                # Simpan ke list data
                data.append({
                    "No": article_count,
                    "Judul Berita": title,
                    "Sentimen": sentiment,
                    "Polaritas": round(polarity, 2),
                    "Tanggal": published
                })

        # Menghitung Persentase untuk Ringkasan
        total = article_count
        pct_bull = (summary['Bullish'] / total) * 100 if total > 0 else 0
        pct_bear = (summary['Bearish'] / total) * 100 if total > 0 else 0
        pct_neut = (summary['Neutral'] / total) * 100 if total > 0 else 0

        # --- Menampilkan Ringkasan (Bagian Bawah di Tkinter) ---
        st.markdown("### Ringkasan Sentimen Pasar")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Total Artikel", f"{total}")
        col2.metric("Bullish 🟢", f"{summary['Bullish']}", f"{pct_bull:.2f}%")
        col3.metric("Bearish 🔴", f"{summary['Bearish']}", f"-{pct_bear:.2f}%") # Tanda minus agar panah di web jadi merah
        col4.metric("Neutral ⚪", f"{summary['Neutral']}", f"{pct_neut:.2f}%", delta_color="off")

        st.divider()

        # --- Menampilkan Tabel Berita (Bagian Tengah di Tkinter) ---
        st.markdown("### Detail Berita")
        
        # Ubah list menjadi DataFrame Pandas (Tabel pintar)
        df = pd.DataFrame(data)
        
        # Tampilkan tabel di web (bisa di-sortir dan di-scroll otomatis oleh Streamlit)
        st.dataframe(df, use_container_width=True, hide_index=True)