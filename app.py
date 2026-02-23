"""
=============================================================================
  NANOMANYETİK BİLİMSEL CİHAZLAR — DEPO STOK YÖNETİM SİSTEMİ
  Production-Ready  ·  v2.2  ·  Multi-Language (TR/EN)
=============================================================================

MİMARİ NOTLARI
──────────────
▸ NEDEN PARQUET?
  Excel (.xlsx) dosyaları satır-bazlı (row-oriented) bir format kullanır.
  Apache Parquet ise kolon-bazlı (columnar) bir formattır:
    • 10-50× daha küçük dosya boyutu (Snappy sıkıştırma ile)
    • Kolon seçici okuma, Pandas + PyArrow entegrasyonu, ultra-hızlı I/O

▸ ADMIN GÜVENLİĞİ
  • Sidebar'da "Yönetici Girişi" expander'ı varsayılan olarak KAPALI durur.
  • Şifre doğrulanmadıkça st.file_uploader ASLA render edilmez.

▸ ÇOK DİL DESTEĞİ
  • Tüm UI metinleri TRANSLATIONS sözlüğünde tanımlıdır.
  • Sidebar'da bayrak butonu ile dil değiştirilebilir (varsayılan: TR).
=============================================================================
"""

import os
import hashlib
import base64
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ═══════════════════════════════════════════════════════════════════════════
# SABİTLER
# ═══════════════════════════════════════════════════════════════════════════

ADMIN_PASSWORD = "admin123"
DATA_DIR = Path(__file__).resolve().parent / "data"
PARQUET_PATH = DATA_DIR / "stok_verisi.parquet"
LOGO_PATH = Path(__file__).resolve().parent / "logo.jpg"
PAGE_TITLE = "Nanomanyetik — Depo Stok Sistemi"
PAGE_ICON = "🔬"
MAX_RESULTS = 500


def get_logo_base64():
    """Logo dosyasını base64 formatına çevir."""
    if LOGO_PATH.exists():
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# ═══════════════════════════════════════════════════════════════════════════
# ÇOK DİL DESTEĞİ
# ═══════════════════════════════════════════════════════════════════════════

TRANSLATIONS = {
    "admin_login_title": {"tr": "🔐 Yönetici Girişi", "en": "🔐 Admin Login"},
    "password_label": {"tr": "Şifre", "en": "Password"},
    "password_placeholder": {"tr": "Yönetici şifresini girin…", "en": "Enter admin password…"},
    "login_btn": {"tr": "Giriş Yap", "en": "Sign In"},
    "logout_btn": {"tr": "Çıkış Yap", "en": "Sign Out"},
    "admin_active": {"tr": "✅ Yönetici Oturumu Aktif", "en": "✅ Admin Session Active"},
    "wrong_password": {"tr": "⛔ Hatalı şifre.", "en": "⛔ Incorrect password."},
    "data_upload_title": {"tr": "### 📤 Veri Yükleme", "en": "### 📤 Data Upload"},
    "file_uploader_label": {"tr": "Excel dosyası seçin (.xlsx)", "en": "Select Excel file (.xlsx)"},
    "file_uploader_help": {
        "tr": "Yüklenen dosya otomatik olarak Parquet formatına dönüştürülür.",
        "en": "Uploaded file will be automatically converted to Parquet format.",
    },
    "converting_spinner": {"tr": "🔄 Excel → Parquet dönüşümü…", "en": "🔄 Converting Excel → Parquet…"},
    "etl_success": {
        "tr": "✅ Dönüştürme başarılı!\n\n• **Satır:** {rows}  |  **Sütun:** {cols}\n• **Boyut:** {size} KB  |  **Format:** Snappy Parquet",
        "en": "✅ Conversion successful!\n\n• **Rows:** {rows}  |  **Columns:** {cols}\n• **Size:** {size} KB  |  **Format:** Snappy Parquet",
    },
    "etl_empty": {
        "tr": "Yüklenen dosya boş. Lütfen geçerli bir Excel dosyası yükleyin.",
        "en": "Uploaded file is empty. Please upload a valid Excel file.",
    },
    "etl_error": {"tr": "❌ Dönüştürme hatası: {}", "en": "❌ Conversion error: {}"},
    "maintenance_title": {"tr": "Sistem Hazırlanıyor", "en": "System Initializing"},
    "maintenance_msg": {
        "tr": "Stok veritabanı henüz yüklenmedi.<br>Yönetici panelinden veri yüklemesi yapılması bekleniyor.",
        "en": "Stock database has not been loaded yet.<br>Awaiting data upload from the admin panel.",
    },
    "stat_total_records": {"tr": "Toplam Kayıt", "en": "Total Records"},
    "stat_data_fields": {"tr": "Veri Alanı", "en": "Data Fields"},
    "stat_database": {"tr": "Veritabanı", "en": "Database"},
    "search_placeholder": {
        "tr": "🔍  Ürün adı, stok kodu veya herhangi bir bilgi ile arayın…",
        "en": "🔍  Search by product name, stock code, or any keyword…",
    },
    "search_guide": {
        "tr": "⬆️ Arama çubuğunu kullanarak depo stok verilerinde arama yapın.",
        "en": "⬆️ Use the search bar above to search the warehouse inventory.",
    },
    "results_found": {
        "tr": "🎯 <strong>{count}</strong> sonuç bulundu{suffix}",
        "en": "🎯 <strong>{count}</strong> result(s) found{suffix}",
    },
    "results_limit_suffix": {"tr": " (ilk {} gösteriliyor)", "en": " (showing first {})"},
    "no_results_title": {
        "tr": '"{q}" ile eşleşen kayıt bulunamadı.',
        "en": 'No records matching "{q}" were found.',
    },
    "no_results_hint": {"tr": "Farklı anahtar kelimeler deneyebilirsiniz.", "en": "Try different keywords."},
    "lang_switch": {"tr": "English", "en": "Türkçe"},
    "stat_last_update": {"tr": "Son Güncelleme", "en": "Last Update"},
}


def t(key):
    """Aktif dile göre çeviri döndürür."""
    lang = st.session_state.get("lang", "tr")
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    return entry.get(lang, entry.get("tr", key))


# ═══════════════════════════════════════════════════════════════════════════
# YARDIMCI FONKSİYONLAR (Sidebar'dan ÖNCE tanımlanmalı!)
# ═══════════════════════════════════════════════════════════════════════════

def ensure_data_dir():
    """Data dizininin var olduğundan emin ol."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def convert_excel_to_parquet(uploaded_file):
    # type: (...) -> Tuple[bool, str]
    """ETL: Excel → Parquet dönüştürücü."""
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl", dtype=str)
        if df.empty:
            return False, t("etl_empty")

        df.columns = df.columns.str.strip()
        # Boş hücreleri temizle
        df = df.fillna("")
        ensure_data_dir()

        df.to_parquet(PARQUET_PATH, engine="pyarrow", compression="snappy", index=False)

        rows, cols = df.shape
        size_kb = PARQUET_PATH.stat().st_size / 1024
        msg = t("etl_success").format(
            rows="{:,}".format(rows), cols=cols, size="{:,.1f}".format(size_kb),
        )
        return True, msg
    except Exception as exc:
        return False, t("etl_error").format(exc)


def load_parquet_data():
    # type: () -> Optional[pd.DataFrame]
    """Parquet dosyasını RAM'e yükler ve önbellekler."""
    if not PARQUET_PATH.exists():
        return None
    try:
        return pd.read_parquet(PARQUET_PATH, engine="pyarrow")
    except Exception:
        return None


def search_dataframe(df, query):
    # type: (pd.DataFrame, str) -> pd.DataFrame
    """Tüm sütunlarda case-insensitive arama."""
    if not query.strip():
        return pd.DataFrame()
    query_lower = query.strip().lower()
    mask = pd.Series(False, index=df.index)
    for col in df.columns:
        mask |= df[col].astype(str).str.lower().str.contains(query_lower, na=False, regex=False)
    return df.loc[mask].head(MAX_RESULTS)


# ═══════════════════════════════════════════════════════════════════════════
# STREAMLIT SAYFA AYARLARI
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "lang" not in st.session_state:
    st.session_state.lang = "tr"
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False


# ═══════════════════════════════════════════════════════════════════════════
# CUSTOM CSS
# ═══════════════════════════════════════════════════════════════════════════

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ═══ GLOBAL ═══ */
    .stApp {
        background: #060a14;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        color: #c8d6e5;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    div[data-testid="stToolbar"] {display: none;}
    div[data-testid="stDecoration"] {display: none;}
    header[data-testid="stHeader"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    div[data-testid="stStatusWidget"] {
        display: none !important;
    }

    /* ═══ ÜST PADDİNG SIFIRLA — İçerik hemen başlasın ═══ */
    .main .block-container {
        max-width: 95% !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding-top: 1rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-bottom: 0 !important;
    }
    .main {
        padding-left: 0 !important;
        transition: none !important;
    }
    section.main > div {
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    [data-testid="stSidebar"] {
        transition: none !important;
    }
    [data-testid="stSidebar"] ~ .main {
        transition: none !important;
    }

    /* ═══ CUSTOM HTML TABLE ═══ */
    .table-container {
        width: 100%;
        max-height: 600px;
        overflow-x: auto !important;
        overflow-y: auto !important;
        border-radius: 12px;
        border: 1px solid rgba(0, 212, 255, 0.12);
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
        margin: 0 auto;
    }
    .table-container table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem;
        white-space: nowrap;
    }
    .table-container thead th {
        position: sticky;
        top: 0;
        z-index: 10;
        background: linear-gradient(135deg, #0d1224 0%, #111a33 100%);
        color: #00d4ff;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-size: 0.7rem;
        padding: 14px 16px;
        border-bottom: 2px solid rgba(0, 212, 255, 0.2);
        text-align: left;
    }
    .table-container tbody tr {
        transition: background 0.15s ease;
    }
    .table-container tbody tr:nth-child(even) {
        background: rgba(10, 16, 32, 0.6);
    }
    .table-container tbody tr:nth-child(odd) {
        background: rgba(6, 10, 20, 0.8);
    }
    .table-container tbody tr:hover {
        background: rgba(0, 212, 255, 0.06) !important;
    }
    .table-container tbody tr.row-selected {
        background: rgba(0, 212, 255, 0.15) !important;
        border-left: 3px solid #00d4ff;
    }
    .table-container tbody tr.row-selected td {
        color: #ffffff !important;
        font-weight: 600;
    }
    .table-container tbody tr.row-selected td:first-child {
        padding-left: 13px;
    }
    .table-container tbody td {
        padding: 10px 16px;
        color: #b0c4d8;
        border-bottom: 1px solid rgba(0, 212, 255, 0.04);
        max-width: 300px;
        overflow: hidden;
        text-overflow: ellipsis;
        cursor: pointer;
    }
    .table-container::-webkit-scrollbar { width: 8px; height: 8px; }
    .table-container::-webkit-scrollbar-track { background: #0a0e1a; border-radius: 4px; }
    .table-container::-webkit-scrollbar-thumb {
        background: rgba(0, 212, 255, 0.2);
        border-radius: 4px;
    }
    .table-container::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 212, 255, 0.4);
    }
    .table-container::-webkit-scrollbar-corner { background: #0a0e1a; }

    /* ── Sidebar — Glassmorphism ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg,
            rgba(10, 16, 32, 0.98) 0%,
            rgba(8, 12, 24, 0.98) 50%,
            rgba(12, 20, 40, 0.98) 100%) !important;
        border-right: 1px solid rgba(0, 212, 255, 0.1) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown {
        color: #a0b4c8 !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(0, 212, 255, 0.08) !important;
        margin: 12px 0 !important;
    }

    /* ── Sidebar Butonlar ── */
    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
        color: #060a14;
        font-weight: 700;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        letter-spacing: 0.3px;
        font-size: 0.85rem;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, #33e0ff 0%, #00b8e6 100%);
        box-shadow: 0 0 24px rgba(0, 212, 255, 0.35);
        transform: translateY(-2px);
    }

    /* ── Arama Kutusu (Ana sayfa) ── */
    .stTextInput > div > div > input {
        border-radius: 999px !important;
        padding: 18px 32px !important;
        font-size: 17px !important;
        font-family: 'Inter', sans-serif !important;
        border: 1.5px solid rgba(0, 212, 255, 0.15) !important;
        box-shadow: 0 4px 32px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255,255,255,0.02) !important;
        background: rgba(10, 14, 26, 0.95) !important;
        color: #e8f0fe !important;
        caret-color: #00d4ff !important;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
        letter-spacing: 0.2px !important;
    }
    .stTextInput > div > div > input::placeholder { color: #3a5068 !important; }
    .stTextInput > div > div > input:focus {
        border-color: #00d4ff !important;
        box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.06), 0 8px 40px rgba(0,0,0,0.6) !important;
    }
    .stTextInput > label {
        font-size: 0px !important; height: 0px !important;
        margin: 0 !important; padding: 0 !important;
    }

    /* ── Sidebar Input ── */
    section[data-testid="stSidebar"] .stTextInput > div > div > input {
        border-radius: 10px !important;
        background: rgba(0, 0, 0, 0.35) !important;
        border: 1px solid rgba(0, 212, 255, 0.12) !important;
        color: #c8d6e5 !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
    }
    section[data-testid="stSidebar"] .stTextInput > div > div > input:focus {
        border-color: #00d4ff !important;
        box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.08) !important;
    }

    /* ── Sidebar Expander ── */
    section[data-testid="stSidebar"] .streamlit-expanderHeader {
        color: #a0b4c8 !important;
        font-weight: 600;
        background: rgba(0, 212, 255, 0.03);
        border-radius: 10px;
        border-left: 3px solid rgba(0, 212, 255, 0.3);
        padding-left: 12px;
    }

    /* ═══ BRAND ═══ */
    .brand-section {
        text-align: center;
        padding: 10px 20px 4px 20px;
    }
    .brand-logo {
        margin-bottom: 8px;
    }
    .brand-logo img {
        width: 56px;
        height: 56px;
        object-fit: contain;
        filter: drop-shadow(0 0 24px rgba(0, 212, 255, 0.4));
        border-radius: 12px;
    }
    .brand-logo-emoji {
        font-size: 2.2rem;
        margin-bottom: 4px;
        filter: drop-shadow(0 0 24px rgba(0, 212, 255, 0.5));
    }
    .brand-name {
        font-size: 1.15rem;
        font-weight: 800;
        letter-spacing: 4px;
        white-space: nowrap;
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 40%, #00d4ff 80%, #33e0ff 100%);
        background-size: 300% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 5s ease-in-out infinite;
        margin-bottom: 2px;
    }
    @keyframes shimmer {
        0%, 100% { background-position: 0% center; }
        50% { background-position: 300% center; }
    }
    .brand-subtitle {
        font-size: 0.65rem;
        color: #3a5068;
        letter-spacing: 4px;
        font-weight: 500;
    }
    .brand-divider {
        width: 60px; height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0,212,255,0.4), transparent);
        margin: 10px auto 0 auto;
    }

    /* ═══ STAT CARDS ═══ */
    @keyframes fadeSlideUp {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stats-container {
        display: flex; justify-content: center;
        gap: 14px; flex-wrap: wrap;
        margin: 16px auto 20px auto; max-width: 820px;
        animation: fadeSlideUp 0.6s ease-out;
    }
    .stat-card {
        background: linear-gradient(145deg, rgba(10,16,30,0.95), rgba(14,22,44,0.95));
        border: 1px solid rgba(0, 212, 255, 0.08);
        border-radius: 14px; padding: 16px 24px;
        text-align: center; min-width: 140px; flex: 1;
        position: relative; overflow: hidden;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stat-card:hover {
        border-color: rgba(0, 212, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 212, 255, 0.1), inset 0 1px 0 rgba(0,212,255,0.05);
        transform: translateY(-3px);
    }
    .stat-card::before {
        content: ''; position: absolute;
        top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, transparent, #00d4ff, transparent);
        opacity: 0.4;
    }
    .stat-icon {
        font-size: 1.3rem; margin-bottom: 4px;
        filter: drop-shadow(0 0 8px rgba(0, 212, 255, 0.3));
    }
    .stat-value {
        font-size: 1.5rem; font-weight: 700;
        color: #00d4ff; line-height: 1.2;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.15);
    }
    .stat-label {
        font-size: 0.62rem; color: #3a5068;
        text-transform: uppercase; letter-spacing: 2px;
        margin-top: 4px; font-weight: 600;
    }

    /* ═══ RESULT BADGE ═══ */
    .result-badge {
        display: flex; align-items: center; justify-content: center;
        gap: 8px; margin: 16px auto 14px auto;
        max-width: fit-content;
        padding: 8px 24px;
        background: linear-gradient(135deg, rgba(0,212,255,0.06), rgba(0,153,204,0.04));
        border: 1px solid rgba(0, 212, 255, 0.12);
        border-radius: 999px;
        animation: fadeSlideUp 0.4s ease-out;
    }
    .result-badge .rb-icon {
        font-size: 0.9rem;
    }
    .result-badge .rb-text {
        font-size: 0.82rem;
        color: #6b8299;
        letter-spacing: 0.3px;
    }
    .result-badge .rb-count {
        color: #00d4ff;
        font-weight: 700;
        font-size: 0.9rem;
    }

    /* ═══ MAINTENANCE ═══ */
    .maintenance-card {
        max-width: 480px; margin: 60px auto;
        background: linear-gradient(145deg, rgba(10,16,30,0.98), rgba(14,22,44,0.95));
        border: 1px solid rgba(0, 212, 255, 0.08);
        border-radius: 20px; padding: 48px 36px;
        text-align: center; position: relative; overflow: hidden;
        animation: fadeSlideUp 0.6s ease-out;
    }
    .maintenance-card::before {
        content: ''; position: absolute;
        top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, transparent, #ff9500, #ffcc00, transparent);
    }
    .maintenance-card .m-icon {
        font-size: 3rem; margin-bottom: 16px;
        filter: drop-shadow(0 0 12px rgba(255, 153, 0, 0.4));
    }
    .maintenance-card h2 {
        color: #e8f0fe; font-size: 1.3rem; font-weight: 700;
        margin-bottom: 10px; letter-spacing: 0.5px;
    }
    .maintenance-card p { color: #4a6785; font-size: 0.88rem; line-height: 1.7; }
    .maintenance-pulse {
        display: inline-block; width: 8px; height: 8px;
        background: #ff9500; border-radius: 50%;
        margin-right: 6px; animation: pulse 2s ease-in-out infinite;
        vertical-align: middle;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(255,153,0,0.5); }
        50% { opacity: 0.6; box-shadow: 0 0 0 8px rgba(255,153,0,0); }
    }

    /* ═══ EMPTY / GUIDE ═══ */
    .empty-state {
        text-align: center; padding: 40px 20px;
        animation: fadeSlideUp 0.4s ease-out;
    }
    .empty-state .empty-icon { font-size: 2.5rem; margin-bottom: 12px; opacity: 0.5; }
    .empty-state .empty-title { font-size: 0.95rem; color: #5a7a94; margin-bottom: 4px; }
    .empty-state .empty-hint { font-size: 0.8rem; color: #2e4458; }

    .guide-text {
        text-align: center; padding: 20px 0;
        color: #2e4458; font-size: 0.85rem; letter-spacing: 0.3px;
    }

    /* ═══ ADMIN BADGE ═══ */
    .admin-badge {
        background: linear-gradient(135deg, rgba(6,95,70,0.8), rgba(4,120,87,0.8));
        color: #a7f3d0; padding: 12px 18px; border-radius: 12px;
        text-align: center; font-weight: 600; font-size: 0.85rem;
        border: 1px solid rgba(167, 243, 208, 0.12); margin-bottom: 12px;
        backdrop-filter: blur(4px);
    }

    /* ═══ FOOTER ═══ */
    .app-footer {
        text-align: center;
        padding: 24px 20px 16px 20px;
        margin-top: 40px;
        border-top: 1px solid rgba(0, 212, 255, 0.06);
    }
    .footer-line {
        font-size: 0.65rem;
        color: #1e3348;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 500;
    }
    .footer-version {
        font-size: 0.58rem;
        color: #152535;
        margin-top: 4px;
        letter-spacing: 1px;
    }

    /* ═══ PARTICLE GRID ═══ */
    .stApp::before {
        content: ''; position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: radial-gradient(circle at 1px 1px, rgba(0, 212, 255, 0.025) 1px, transparent 0);
        background-size: 48px 48px;
        pointer-events: none; z-index: 0;
    }

    /* ═══ SCROLLBAR ═══ */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #060a14; }
    ::-webkit-scrollbar-thumb {
        background: rgba(0, 212, 255, 0.15);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 212, 255, 0.3);
    }

    /* ═══ INPUT HELPER TEXT GİZLE ═══ */
    div[data-testid="InputInstructions"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════

with st.sidebar:

    # Sidebar branding
    _logo_b64 = get_logo_base64()
    if _logo_b64:
        _sidebar_logo_html = '<img src="data:image/jpeg;base64,{}" style="width:48px; height:48px; object-fit:contain; border-radius:8px;"/>'.format(_logo_b64)
    else:
        _sidebar_logo_html = '<span style="font-size:1.5rem;">🔬</span>'
    st.markdown(
        """
        <div style="text-align:center; padding: 8px 0 4px 0;">
            {logo}
            <div style="font-size:0.65rem; letter-spacing:3px; text-transform:uppercase;
                        color:#4a6785; margin-top:4px; font-weight:600;">Nanomanyetik</div>
        </div>
        """.format(logo=_sidebar_logo_html),
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # ── Dil Değiştirici ──
    _current_lang = st.session_state.get("lang", "tr")
    _btn_label = "English" if _current_lang == "tr" else "Türkçe"
    if st.button(_btn_label, key="lang_toggle_btn", use_container_width=True):
        st.session_state.lang = "en" if st.session_state.lang == "tr" else "tr"
        st.rerun()
    st.markdown("---")

    # ── Admin Kimlik Doğrulama ──
    with st.expander(t("admin_login_title"), expanded=False):
        if not st.session_state.admin_authenticated:
            def _try_login():
                pw = st.session_state.get("admin_pw_input", "")
                if pw == ADMIN_PASSWORD:
                    st.session_state.admin_authenticated = True
                elif pw:
                    st.session_state._admin_login_error = True

            password = st.text_input(
                t("password_label"),
                type="password",
                placeholder=t("password_placeholder"),
                key="admin_pw_input",
                on_change=_try_login,
            )
            login_clicked = st.button(t("login_btn"), key="admin_login_btn")
            if login_clicked:
                _try_login()
                if st.session_state.admin_authenticated:
                    st.rerun()
            if st.session_state.get("_admin_login_error"):
                st.error(t("wrong_password"))
                st.session_state._admin_login_error = False
            if st.session_state.admin_authenticated:
                st.rerun()
        else:
            st.markdown(
                '<div class="admin-badge">{}</div>'.format(t("admin_active")),
                unsafe_allow_html=True,
            )
            if st.button(t("logout_btn"), key="admin_logout_btn"):
                st.session_state.admin_authenticated = False
                st.rerun()

    # ── Dosya Yükleme (Sadece Admin) ──
    if st.session_state.admin_authenticated:
        st.markdown("---")
        st.markdown(t("data_upload_title"))

        uploaded_file = st.file_uploader(
            t("file_uploader_label"),
            type=["xlsx"],
            key="excel_uploader",
            help=t("file_uploader_help"),
        )

        if uploaded_file is not None:
            with st.spinner(t("converting_spinner")):
                success, message = convert_excel_to_parquet(uploaded_file)
            if success:
                st.success(message)
            else:
                st.error(message)

        if PARQUET_PATH.exists():
            st.markdown("---")
            mod_time = datetime.fromtimestamp(PARQUET_PATH.stat().st_mtime)
            size_kb = PARQUET_PATH.stat().st_size / 1024
            st.caption("📅 {}".format(mod_time.strftime('%d.%m.%Y – %H:%M')))
            st.caption("💾 {:,.1f} KB".format(size_kb))

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR AÇMA BUTONU (JS ile parent document'e enjekte)
# ═══════════════════════════════════════════════════════════════════════════

# Harici JS dosyasını oku ve enjekte et
_toggle_js_path = Path(__file__).resolve().parent / "sidebar_toggle.js"
if _toggle_js_path.exists():
    _toggle_js = _toggle_js_path.read_text(encoding="utf-8")
    components.html("<script>{}</script>".format(_toggle_js), height=0)

# ═══════════════════════════════════════════════════════════════════════════
# ANA SAYFA
# ═══════════════════════════════════════════════════════════════════════════

_main_logo_b64 = get_logo_base64()
if _main_logo_b64:
    _main_logo_html = '<div class="brand-logo"><img src="data:image/jpeg;base64,{}" alt="Nanomanyetik"/></div>'.format(_main_logo_b64)
else:
    _main_logo_html = '<div class="brand-logo-emoji">🔬</div>'

st.markdown(
    """
    <div class="brand-section">
        {logo}
        <div class="brand-name">NANOMANYETİK BİLİMSEL CİHAZLAR</div>
        <div class="brand-subtitle">DEPO STOK YÖNETİM SİSTEMİ</div>
        <div class="brand-divider"></div>
    </div>
    """.format(logo=_main_logo_html),
    unsafe_allow_html=True,
)

# ── Veri Kontrolü ──
df = load_parquet_data()

if df is None:
    st.markdown(
        """
        <div class="maintenance-card">
            <div class="m-icon">⚠️</div>
            <h2><span class="maintenance-pulse"></span> {title}</h2>
            <p>{msg}</p>
        </div>
        """.format(title=t("maintenance_title"), msg=t("maintenance_msg")),
        unsafe_allow_html=True,
    )
    st.stop()

# ── İstatistik Kartları ──
total_rows, total_cols = df.shape
parquet_size_kb = PARQUET_PATH.stat().st_size / 1024
_mod_ts = datetime.fromtimestamp(PARQUET_PATH.stat().st_mtime)
_last_update_str = _mod_ts.strftime("%d.%m.%Y — %H:%M")
st.markdown(
    """
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-value">{rows}</div>
            <div class="stat-label">{lbl_records}</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">📋</div>
            <div class="stat-value">{cols}</div>
            <div class="stat-label">{lbl_fields}</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">💾</div>
            <div class="stat-value">{size} KB</div>
            <div class="stat-label">{lbl_db}</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🕐</div>
            <div class="stat-value" style="font-size:1.1rem;">{last_update}</div>
            <div class="stat-label">{lbl_update}</div>
        </div>
    </div>
    """.format(
        rows="{:,}".format(total_rows),
        cols=total_cols,
        size="{:,.0f}".format(parquet_size_kb),
        last_update=_last_update_str,
        lbl_records=t("stat_total_records"),
        lbl_fields=t("stat_data_fields"),
        lbl_db=t("stat_database"),
        lbl_update=t("stat_last_update"),
    ),
    unsafe_allow_html=True,
)

# ── Arama Çubuğu (Custom Component — gerçek zamanlı arama) ──

_search_component = components.declare_component(
    "live_search",
    path=str(Path(__file__).resolve().parent / "search_component"),
)

search_query = _search_component(
    placeholder=t("search_placeholder"),
    default_value=st.session_state.get("last_search", ""),
    key="search_input",
    default="",
)
if search_query is None:
    search_query = st.session_state.get("last_search", "")
else:
    st.session_state["last_search"] = search_query

# ── Sonuçlar ──
if search_query and search_query.strip():
    results = search_dataframe(df, search_query)

    if results.empty:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-icon">🔍</div>
                <div class="empty-title">{title}</div>
                <div class="empty-hint">{hint}</div>
            </div>
            """.format(
                title=t("no_results_title").format(q=search_query),
                hint=t("no_results_hint"),
            ),
            unsafe_allow_html=True,
        )
    else:
        result_count = len(results)
        suffix = t("results_limit_suffix").format(MAX_RESULTS) if result_count >= MAX_RESULTS else ""
        st.markdown(
            '<div class="result-badge"><span class="rb-icon">🎯</span><span class="rb-text"><span class="rb-count">{count}</span> {suffix_text}</span></div>'.format(
                count="{:,}".format(result_count),
                suffix_text=(t("stat_total_records").lower() if st.session_state.get("lang") == "en" else "sonuç bulundu") + suffix,
            ),
            unsafe_allow_html=True,
        )
        # HTML tablo oluştur
        _display_df = results.reset_index(drop=True)
        _raw_table = _display_df.to_html(index=False, escape=True, classes='')
        _row_click_js = """
        <script>
        (function(){
            var pd = window.parent ? window.parent.document : document;
            setTimeout(function(){
                var tables = pd.querySelectorAll('.table-container tbody tr');
                tables.forEach(function(row){
                    row.addEventListener('click', function(){
                        var wasSelected = this.classList.contains('row-selected');
                        // Önceki seçimi temizle
                        var allRows = this.closest('tbody').querySelectorAll('tr');
                        allRows.forEach(function(r){ r.classList.remove('row-selected'); });
                        // Toggle
                        if(!wasSelected) this.classList.add('row-selected');
                    });
                });
            }, 500);
        })();
        </script>
        """
        _table_html = '<div class="table-container">' + _raw_table + '</div>'
        st.markdown(_table_html, unsafe_allow_html=True)
        # Satır tıklama JS'ini components.html ile enjekte et
        components.html(_row_click_js, height=0)
else:
    st.markdown(
        '<div class="guide-text">{}</div>'.format(t("search_guide")),
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════

st.markdown(
    """
    <div class="app-footer">
        <div class="footer-line">© 2026 Nanomanyetik Bilimsel Cihazlar</div>
        <div class="footer-version">Depo Stok Yönetim Sistemi · v2.2</div>
    </div>
    """,
    unsafe_allow_html=True,
)
