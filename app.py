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

import analytics

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
    # ── Analytics Dashboard Translations ──
    "analytics_btn": {"tr": "📊 Analitik Panel", "en": "📊 Analytics Panel"},
    "analytics_title": {"tr": "📊 Analitik Dashboard", "en": "📊 Analytics Dashboard"},
    "analytics_back": {"tr": "← Ana Sayfaya Dön", "en": "← Back to Main"},
    "analytics_overview": {"tr": "Genel Bakış", "en": "Overview"},
    "analytics_total_visits": {"tr": "Toplam Ziyaret", "en": "Total Visits"},
    "analytics_total_searches": {"tr": "Toplam Arama", "en": "Total Searches"},
    "analytics_today_visits": {"tr": "Bugün Ziyaret", "en": "Today Visits"},
    "analytics_today_searches": {"tr": "Bugün Arama", "en": "Today Searches"},
    "analytics_admin_logins": {"tr": "Admin Girişi", "en": "Admin Logins"},
    "analytics_file_uploads": {"tr": "Dosya Yükleme", "en": "File Uploads"},
    "analytics_yearly_visits": {"tr": "📈 Yıllık Ziyaret Grafiği", "en": "📈 Yearly Visits Chart"},
    "analytics_monthly_visits": {"tr": "📅 Aylık Ziyaret Grafiği", "en": "📅 Monthly Visits Chart"},
    "analytics_select_year": {"tr": "Yıl Seçin", "en": "Select Year"},
    "analytics_daily_trend": {"tr": "📊 Son 30 Gün Trend", "en": "📊 Last 30 Days Trend"},
    "analytics_hourly_dist": {"tr": "⏰ Saatlik Aktivite Dağılımı", "en": "⏰ Hourly Activity Distribution"},
    "analytics_weekday_dist": {"tr": "📆 Haftalık Dağılım", "en": "📆 Weekly Distribution"},
    "analytics_search_stats": {"tr": "🔍 Arama İstatistikleri", "en": "🔍 Search Statistics"},
    "analytics_daily_avg": {"tr": "Günlük Ortalama", "en": "Daily Average"},
    "analytics_unique_terms": {"tr": "Benzersiz Terim", "en": "Unique Terms"},
    "analytics_avg_results": {"tr": "Ort. Sonuç", "en": "Avg. Results"},
    "analytics_top_searches": {"tr": "🏆 En Çok Aranan Terimler", "en": "🏆 Top Search Terms"},
    "analytics_search_term": {"tr": "Arama Terimi", "en": "Search Term"},
    "analytics_search_count": {"tr": "Arama Sayısı", "en": "Search Count"},
    "analytics_login_history": {"tr": "🔐 Admin Giriş Geçmişi", "en": "🔐 Admin Login History"},
    "analytics_login_time": {"tr": "Zaman", "en": "Time"},
    "analytics_login_status": {"tr": "Durum", "en": "Status"},
    "analytics_login_success": {"tr": "✅ Başarılı", "en": "✅ Success"},
    "analytics_login_failed": {"tr": "❌ Başarısız", "en": "❌ Failed"},
    "analytics_no_data": {"tr": "Henüz veri bulunmuyor. Kullanım arttıkça istatistikler burada görünecek.", "en": "No data yet. Statistics will appear here as usage increases."},
    "analytics_export_csv": {"tr": "📥 CSV Dışa Aktar", "en": "📥 Export CSV"},
    "analytics_clear_old": {"tr": "🗑️ Eski Logları Temizle (6 ay+)", "en": "🗑️ Clear Old Logs (6 months+)"},
    "analytics_cleared": {"tr": "{} eski kayıt temizlendi.", "en": "{} old records cleared."},
    "analytics_visits": {"tr": "Ziyaret", "en": "Visits"},
    "analytics_searches": {"tr": "Arama", "en": "Searches"},
    "analytics_search_trend": {"tr": "🔍 Son 30 Gün Arama Trendi", "en": "🔍 Last 30 Days Search Trend"},
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
    """Tüm sütunlarda case-insensitive, çoklu kelime AND araması (vektörize)."""
    if not query.strip():
        return pd.DataFrame()
    tokens = query.strip().lower().split()
    # Tüm sütunları vektörize şekilde tek bir string serisine birleştir
    cols = [df[c].astype(str).str.lower() for c in df.columns]
    combined = cols[0]
    for c in cols[1:]:
        combined = combined.str.cat(c, sep=" ")
    # Her token için vektörize AND kontrolü
    mask = combined.str.contains(tokens[0], na=False, regex=False)
    for token in tokens[1:]:
        mask &= combined.str.contains(token, na=False, regex=False)
    return df.loc[mask].head(MAX_RESULTS)


# ═══════════════════════════════════════════════════════════════════════════
# ANALİTİK DASHBOARD RENDER FONKSİYONU
# ═══════════════════════════════════════════════════════════════════════════

def _build_bar_chart_html(data_dict, max_height=180):
    """Verilen sözlükten CSS bar chart HTML'i oluştur."""
    if not data_dict or all(v == 0 for v in data_dict.values()):
        return '<div class="analytics-no-data"><div class="no-data-icon">📭</div>{}</div>'.format(
            t("analytics_no_data")
        )
    max_val = max(data_dict.values()) or 1
    bars_html = ""
    for label, value in data_dict.items():
        h = max(4, int((value / max_val) * max_height))
        bars_html += """
        <div class="analytics-bar-wrapper">
            <div class="analytics-bar-value">{val}</div>
            <div class="analytics-bar" style="height:{h}px;" title="{label}: {val}"></div>
            <div class="analytics-bar-label">{label}</div>
        </div>""".format(val=value, h=h, label=label)
    return '<div class="analytics-bar-chart">{}</div>'.format(bars_html)


def _build_trend_html(data_dict, max_height=100):
    """Mini trend çizgi grafiği oluştur."""
    if not data_dict or all(v == 0 for v in data_dict.values()):
        return '<div class="analytics-no-data"><div class="no-data-icon">📭</div>{}</div>'.format(
            t("analytics_no_data")
        )
    max_val = max(data_dict.values()) or 1
    bars_html = ""
    for date_str, value in data_dict.items():
        h = max(2, int((value / max_val) * max_height))
        short_label = date_str[-2:]  # Günün sayısı
        bars_html += '<div class="analytics-trend-bar" style="height:{h}px;" title="{d}: {v}"></div>'.format(
            h=h, d=date_str, v=value
        )
    return '<div class="analytics-trend-line">{}</div>'.format(bars_html)


def _render_analytics_dashboard():
    """Analitik dashboard sayfasını render et."""
    lang = st.session_state.get("lang", "tr")

    # ── Başlık ──
    st.markdown(
        """
        <div class="analytics-header">
            <h1>{title}</h1>
            <p>{sub}</p>
        </div>
        """.format(
            title=t("analytics_title"),
            sub="Nanomanyetik Bilimsel Cihazlar — " + (
                "Kullanım Analizi" if lang == "tr" else "Usage Analytics"
            ),
        ),
        unsafe_allow_html=True,
    )

    # ── Ana Sayfaya Dön ──
    if st.button(t("analytics_back"), key="analytics_back_btn"):
        st.session_state.current_page = "main"
        st.rerun()

    # ── Genel Bakış Metrikleri ──
    stats = analytics.get_overview_stats()
    overview_cards = [
        ("👁️", stats["total_visits"], t("analytics_total_visits")),
        ("🔍", stats["total_searches"], t("analytics_total_searches")),
        ("📅", stats["today_visits"], t("analytics_today_visits")),
        ("🔎", stats["today_searches"], t("analytics_today_searches")),
        ("🔐", stats["total_logins"], t("analytics_admin_logins")),
        ("📤", stats["total_uploads"], t("analytics_file_uploads")),
    ]
    cards_html = ""
    for icon, value, label in overview_cards:
        cards_html += """
        <div class="analytics-metric-card">
            <div class="analytics-metric-icon">{icon}</div>
            <div class="analytics-metric-value">{value}</div>
            <div class="analytics-metric-label">{label}</div>
        </div>""".format(icon=icon, value="{:,}".format(value), label=label)

    st.markdown(
        '<div class="analytics-overview-grid">{}</div>'.format(cards_html),
        unsafe_allow_html=True,
    )

    # ═══ BÖLÜM 1: Ziyaret Grafikleri ═══
    col1, col2 = st.columns(2)

    with col1:
        # ── Yıllık Ziyaret ──
        st.markdown(
            '<div class="analytics-section-title">{}</div>'.format(t("analytics_yearly_visits")),
            unsafe_allow_html=True,
        )
        yearly_data = analytics.get_visit_stats_by_year()
        yearly_chart = _build_bar_chart_html(yearly_data)
        st.markdown(yearly_chart, unsafe_allow_html=True)

    with col2:
        # ── Aylık Ziyaret ──
        st.markdown(
            '<div class="analytics-section-title">{}</div>'.format(t("analytics_monthly_visits")),
            unsafe_allow_html=True,
        )
        available_years = analytics.get_available_years()
        selected_year = st.selectbox(
            t("analytics_select_year"),
            options=available_years,
            index=len(available_years) - 1,
            key="analytics_year_select",
        )
        monthly_data = analytics.get_visit_stats_by_month(selected_year)
        month_names = analytics.MONTH_NAMES.get(lang, analytics.MONTH_NAMES["tr"])
        monthly_labeled = {month_names[m - 1]: v for m, v in monthly_data.items()}
        monthly_chart = _build_bar_chart_html(monthly_labeled)
        st.markdown(monthly_chart, unsafe_allow_html=True)

    # ═══ BÖLÜM 2: Trend Grafikleri ═══
    col3, col4 = st.columns(2)

    with col3:
        st.markdown(
            '<div class="analytics-section-title">{}</div>'.format(t("analytics_daily_trend")),
            unsafe_allow_html=True,
        )
        daily_data = analytics.get_daily_visits(30)
        daily_trend = _build_trend_html(daily_data)
        st.markdown(daily_trend, unsafe_allow_html=True)

    with col4:
        st.markdown(
            '<div class="analytics-section-title">{}</div>'.format(t("analytics_search_trend")),
            unsafe_allow_html=True,
        )
        search_daily = analytics.get_search_daily_trend(30)
        search_trend = _build_trend_html(search_daily)
        st.markdown(search_trend, unsafe_allow_html=True)

    # ═══ BÖLÜM 3: Saatlik & Haftalık Dağılım ═══
    col5, col6 = st.columns(2)

    with col5:
        st.markdown(
            '<div class="analytics-section-title">{}</div>'.format(t("analytics_hourly_dist")),
            unsafe_allow_html=True,
        )
        hourly_data = analytics.get_hourly_distribution()
        hourly_labeled = {"{:02d}".format(h): v for h, v in hourly_data.items()}
        hourly_chart = _build_bar_chart_html(hourly_labeled, max_height=140)
        st.markdown(hourly_chart, unsafe_allow_html=True)

    with col6:
        st.markdown(
            '<div class="analytics-section-title">{}</div>'.format(t("analytics_weekday_dist")),
            unsafe_allow_html=True,
        )
        weekday_data = analytics.get_weekday_distribution(lang)
        weekday_chart = _build_bar_chart_html(weekday_data, max_height=140)
        st.markdown(weekday_chart, unsafe_allow_html=True)

    # ═══ BÖLÜM 4: Arama İstatistikleri ═══
    st.markdown(
        '<div class="analytics-section-title">{}</div>'.format(t("analytics_search_stats")),
        unsafe_allow_html=True,
    )
    search_stats = analytics.get_search_stats()

    search_cards = [
        ("🔍", search_stats["total"], t("analytics_total_searches")),
        ("📊", search_stats["daily_avg"], t("analytics_daily_avg")),
        ("🏷️", search_stats["unique_terms"], t("analytics_unique_terms")),
        ("📋", search_stats["avg_results"], t("analytics_avg_results")),
    ]
    search_cards_html = ""
    for icon, value, label in search_cards:
        search_cards_html += """
        <div class="analytics-metric-card">
            <div class="analytics-metric-icon">{icon}</div>
            <div class="analytics-metric-value">{value}</div>
            <div class="analytics-metric-label">{label}</div>
        </div>""".format(icon=icon, value=value, label=label)
    st.markdown(
        '<div class="analytics-overview-grid">{}</div>'.format(search_cards_html),
        unsafe_allow_html=True,
    )

    # ── En Çok Aranan Terimler ──
    col7, col8 = st.columns(2)

    with col7:
        st.markdown(
            '<div class="analytics-section-title">{}</div>'.format(t("analytics_top_searches")),
            unsafe_allow_html=True,
        )
        top_searches = analytics.get_top_searches(10)
        if top_searches:
            rows_html = ""
            for i, (term, count) in enumerate(top_searches, 1):
                rows_html += "<tr><td>{}</td><td><strong>{}</strong></td><td>{}</td></tr>".format(
                    i, term, count
                )
            table_html = """
            <table class="analytics-table">
                <thead><tr>
                    <th>#</th>
                    <th>{term_col}</th>
                    <th>{count_col}</th>
                </tr></thead>
                <tbody>{rows}</tbody>
            </table>""".format(
                term_col=t("analytics_search_term"),
                count_col=t("analytics_search_count"),
                rows=rows_html,
            )
            st.markdown(table_html, unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="analytics-no-data"><div class="no-data-icon">🔍</div>{}</div>'.format(
                    t("analytics_no_data")
                ),
                unsafe_allow_html=True,
            )

    with col8:
        # ── Admin Giriş Geçmişi ──
        st.markdown(
            '<div class="analytics-section-title">{}</div>'.format(t("analytics_login_history")),
            unsafe_allow_html=True,
        )
        recent_logins = analytics.get_recent_admin_logins(15)
        if recent_logins:
            login_rows = ""
            for login in recent_logins:
                status = t("analytics_login_success") if login["success"] else t("analytics_login_failed")
                login_rows += "<tr><td>{}</td><td>{}</td></tr>".format(
                    login["timestamp"], status
                )
            login_table = """
            <table class="analytics-table">
                <thead><tr>
                    <th>{time_col}</th>
                    <th>{status_col}</th>
                </tr></thead>
                <tbody>{rows}</tbody>
            </table>""".format(
                time_col=t("analytics_login_time"),
                status_col=t("analytics_login_status"),
                rows=login_rows,
            )
            st.markdown(login_table, unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="analytics-no-data"><div class="no-data-icon">🔐</div>{}</div>'.format(
                    t("analytics_no_data")
                ),
                unsafe_allow_html=True,
            )

    # ═══ BÖLÜM 5: Yönetim Araçları ═══
    st.markdown("---")
    tool_col1, tool_col2, _ = st.columns([1, 1, 2])

    with tool_col1:
        # CSV Dışa Aktarma
        csv_data = analytics.export_events_csv()
        if csv_data:
            st.download_button(
                label=t("analytics_export_csv"),
                data=csv_data,
                file_name="analytics_export_{}.csv".format(
                    datetime.now().strftime("%Y%m%d_%H%M")
                ),
                mime="text/csv",
                key="analytics_csv_download",
                use_container_width=True,
            )

    with tool_col2:
        # Eski Logları Temizle
        if st.button(t("analytics_clear_old"), key="analytics_clear_btn", use_container_width=True):
            cleared = analytics.clear_old_logs(180)
            st.success(t("analytics_cleared").format(cleared))


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
if "current_page" not in st.session_state:
    st.session_state.current_page = "main"

# ── Sayfa ziyaret logu (oturum başına 1 kez) ──
if "_visit_logged" not in st.session_state:
    st.session_state._visit_logged = True
    analytics.log_event("page_visit")


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
        position: relative;
    }
    .table-container table {
        width: max-content;
        min-width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem;
        white-space: nowrap;
    }
    .table-container thead {
        position: sticky;
        top: 0;
        z-index: 11;
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
        padding: 14px 20px 14px 16px;
        border-bottom: 2px solid rgba(0, 212, 255, 0.2);
        text-align: left;
        cursor: pointer;
        user-select: none;
        -webkit-user-select: none;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .table-container thead th:hover {
        background: linear-gradient(135deg, #101830 0%, #152040 100%);
    }
    .table-container thead th.sort-asc::after,
    .table-container thead th.sort-desc::after {
        margin-left: 6px;
        font-size: 0.6rem;
        opacity: 0.9;
    }
    .table-container thead th.sort-asc::after { content: '▲'; }
    .table-container thead th.sort-desc::after { content: '▼'; }
    /* Multi-column sort rank badge */
    .table-container thead th[data-sort-rank]::before {
        content: attr(data-sort-rank);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 16px; height: 16px;
        font-size: 0.55rem;
        font-weight: 800;
        background: rgba(0, 212, 255, 0.2);
        color: #00d4ff;
        border-radius: 50%;
        margin-right: 5px;
        vertical-align: middle;
        line-height: 1;
    }
    /* Sort reset button */
    .sort-reset-wrapper {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 8px;
        min-height: 30px;
    }
    .sort-reset-btn {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 5px 14px;
        font-family: 'Inter', sans-serif;
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        color: #ff6b6b;
        background: rgba(255, 107, 107, 0.08);
        border: 1px solid rgba(255, 107, 107, 0.2);
        border-radius: 999px;
        cursor: pointer;
        opacity: 0;
        pointer-events: none;
        transform: translateY(4px);
        transition: all 0.25s ease;
    }
    .sort-reset-btn.visible {
        opacity: 1;
        pointer-events: auto;
        transform: translateY(0);
    }
    .sort-reset-btn:hover {
        background: rgba(255, 107, 107, 0.15);
        border-color: rgba(255, 107, 107, 0.4);
        box-shadow: 0 0 12px rgba(255, 107, 107, 0.15);
    }
    /* Resize handle */
    .th-resize-handle {
        position: absolute;
        right: -4px; top: 0; bottom: 0;
        width: 9px;
        cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 32 32'%3E%3Cpath d='M5 16h22M5 16l5-5M5 16l5 5M27 16l-5-5M27 16l-5 5' stroke='white' stroke-width='2.5' stroke-linecap='round' fill='none'/%3E%3C/svg%3E") 16 16, col-resize;
        background: transparent;
        z-index: 20;
        transition: background 0.15s;
    }
    .th-resize-handle:hover,
    .th-resize-handle.resizing {
        background: rgba(255, 255, 255, 0.35);
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
        caret-color: white !important;
        cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='28' viewBox='0 0 20 28'%3E%3Cpath d='M6 1H14M10 1V27M6 27H14' stroke='white' stroke-width='2.5' stroke-linecap='round' fill='none'/%3E%3C/svg%3E") 10 14, text !important;
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

    /* ═══ ANALYTICS DASHBOARD ═══ */
    .analytics-header {
        text-align: center;
        padding: 16px 20px 8px 20px;
        animation: fadeSlideUp 0.5s ease-out;
    }
    .analytics-header h1 {
        font-size: 1.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 50%, #33e0ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 4px;
        letter-spacing: 1px;
    }
    .analytics-header p {
        color: #3a5068;
        font-size: 0.8rem;
        letter-spacing: 1px;
    }
    .analytics-overview-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 12px;
        margin: 16px auto 24px auto;
        max-width: 1000px;
        animation: fadeSlideUp 0.6s ease-out;
    }
    .analytics-metric-card {
        background: linear-gradient(145deg, rgba(10,16,30,0.95), rgba(14,22,44,0.95));
        border: 1px solid rgba(0, 212, 255, 0.08);
        border-radius: 14px;
        padding: 18px 16px;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .analytics-metric-card:hover {
        border-color: rgba(0, 212, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 212, 255, 0.1);
        transform: translateY(-3px);
    }
    .analytics-metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, transparent, #00d4ff, transparent);
        opacity: 0.4;
    }
    .analytics-metric-icon {
        font-size: 1.5rem;
        margin-bottom: 6px;
        filter: drop-shadow(0 0 8px rgba(0, 212, 255, 0.3));
    }
    .analytics-metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #00d4ff;
        line-height: 1.2;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.15);
    }
    .analytics-metric-label {
        font-size: 0.6rem;
        color: #3a5068;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 4px;
        font-weight: 600;
    }
    .analytics-section-title {
        font-size: 1rem;
        font-weight: 700;
        color: #a0b4c8;
        margin: 28px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(0, 212, 255, 0.08);
        letter-spacing: 0.5px;
    }
    .analytics-bar-chart {
        display: flex;
        align-items: flex-end;
        gap: 6px;
        height: 200px;
        padding: 12px 0;
        margin: 8px 0;
    }
    .analytics-bar-wrapper {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        height: 100%;
        justify-content: flex-end;
    }
    .analytics-bar {
        width: 100%;
        max-width: 60px;
        background: linear-gradient(180deg, #00d4ff 0%, #0077aa 100%);
        border-radius: 6px 6px 2px 2px;
        min-height: 4px;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }
    .analytics-bar:hover {
        background: linear-gradient(180deg, #33e0ff 0%, #0099cc 100%);
        box-shadow: 0 0 16px rgba(0, 212, 255, 0.3);
    }
    .analytics-bar-value {
        font-size: 0.65rem;
        color: #00d4ff;
        font-weight: 700;
        margin-bottom: 4px;
        text-align: center;
    }
    .analytics-bar-label {
        font-size: 0.6rem;
        color: #3a5068;
        margin-top: 6px;
        text-align: center;
        font-weight: 500;
    }
    .analytics-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem;
        margin: 8px 0;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(0, 212, 255, 0.08);
    }
    .analytics-table thead th {
        background: linear-gradient(135deg, #0d1224 0%, #111a33 100%);
        color: #00d4ff;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.68rem;
        padding: 12px 16px;
        border-bottom: 2px solid rgba(0, 212, 255, 0.15);
        text-align: left;
    }
    .analytics-table tbody tr {
        transition: background 0.15s ease;
    }
    .analytics-table tbody tr:nth-child(even) {
        background: rgba(10, 16, 32, 0.6);
    }
    .analytics-table tbody tr:nth-child(odd) {
        background: rgba(6, 10, 20, 0.8);
    }
    .analytics-table tbody tr:hover {
        background: rgba(0, 212, 255, 0.06) !important;
    }
    .analytics-table tbody td {
        padding: 10px 16px;
        color: #b0c4d8;
        border-bottom: 1px solid rgba(0, 212, 255, 0.04);
    }
    .analytics-no-data {
        text-align: center;
        padding: 48px 20px;
        color: #3a5068;
        font-size: 0.9rem;
        animation: fadeSlideUp 0.5s ease-out;
    }
    .analytics-no-data .no-data-icon {
        font-size: 3rem;
        margin-bottom: 16px;
        opacity: 0.4;
    }
    .analytics-trend-line {
        display: flex;
        align-items: flex-end;
        gap: 2px;
        height: 120px;
        padding: 8px 0;
        margin: 8px 0;
    }
    .analytics-trend-bar {
        flex: 1;
        background: linear-gradient(180deg, rgba(0,212,255,0.7) 0%, rgba(0,119,170,0.3) 100%);
        border-radius: 3px 3px 0 0;
        min-height: 2px;
        transition: all 0.3s ease;
    }
    .analytics-trend-bar:hover {
        background: linear-gradient(180deg, #00d4ff 0%, #0077aa 100%);
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
                    analytics.log_event("admin_login", {"success": True})
                elif pw:
                    st.session_state._admin_login_error = True
                    analytics.log_event("admin_login", {"success": False})

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

        # ── Analitik Butonu (Admin) ──
        if st.button(t("analytics_btn"), key="analytics_nav_btn", use_container_width=True):
            st.session_state.current_page = (
                "main" if st.session_state.current_page == "analytics" else "analytics"
            )
            st.rerun()

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
                analytics.log_event("file_upload", {"filename": uploaded_file.name})
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

# ═══════════════════════════════════════════════════════════════════════════
# ANALYTICS DASHBOARD SAYFASI
# ═══════════════════════════════════════════════════════════════════════════

if st.session_state.get("current_page") == "analytics" and st.session_state.admin_authenticated:
    _render_analytics_dashboard()
    st.stop()

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

    # ── Arama olayını logla ──
    _search_log_key = "_last_logged_search"
    if st.session_state.get(_search_log_key) != search_query:
        analytics.log_event("search", {
            "query": search_query,
            "result_count": len(results),
        })
        st.session_state[_search_log_key] = search_query

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
        _table_js = """
        <script>
        (function(){
            var pd = window.parent ? window.parent.document : document;
            setTimeout(function(){
                var container = pd.querySelector('.table-container');
                if (!container) return;
                var table = container.querySelector('table');
                if (!table) return;
                var headers = table.querySelectorAll('thead th');

                // ── Colgroup'u ilk resize'da oluştur (başlangıçta tablo kompakt kalır) ──
                function ensureColgroup() {
                    var cg = table.querySelector('colgroup');
                    if (cg) return cg;
                    // Mevcut doğal genişlikleri ölç
                    var widths = [];
                    headers.forEach(function(th) {
                        widths.push(th.offsetWidth);
                    });
                    cg = pd.createElement('colgroup');
                    widths.forEach(function(w) {
                        var col = pd.createElement('col');
                        col.style.width = w + 'px';
                        cg.appendChild(col);
                    });
                    table.insertBefore(cg, table.firstChild);
                    table.style.tableLayout = 'fixed';
                    return cg;
                }

                // ── Sütun başlıklarına position:relative ekle ──
                headers.forEach(function(th) {
                    th.style.position = 'relative';
                });

                // ── Resize Handle Ekleme ──
                headers.forEach(function(th, idx){
                    if (th.querySelector('.th-resize-handle')) return;
                    var handle = pd.createElement('div');
                    handle.className = 'th-resize-handle';
                    th.appendChild(handle);

                    var startX, startW;
                    handle.addEventListener('mousedown', function(e){
                        e.stopPropagation();
                        e.preventDefault();
                        var cg = ensureColgroup();
                        var col = cg.querySelectorAll('col')[idx];
                        startX = e.pageX;
                        startW = parseInt(col.style.width) || th.offsetWidth;
                        handle.classList.add('resizing');

                        function onMove(ev){
                            var newW = startW + (ev.pageX - startX);
                            if (newW < 40) newW = 40;
                            col.style.width = newW + 'px';
                        }
                        function onUp(){
                            handle.classList.remove('resizing');
                            pd.removeEventListener('mousemove', onMove);
                            pd.removeEventListener('mouseup', onUp);
                        }
                        pd.addEventListener('mousemove', onMove);
                        pd.addEventListener('mouseup', onUp);
                    });

                    // ── Çift tıklama ile auto-fit ──
                    handle.addEventListener('dblclick', function(e){
                        e.stopPropagation();
                        e.preventDefault();
                        var cg = ensureColgroup();
                        var col = cg.querySelectorAll('col')[idx];
                        // İçeriğin tam genişliğini hesapla
                        var maxW = th.scrollWidth;
                        table.querySelectorAll('tbody tr').forEach(function(row){
                            var cell = row.children[idx];
                            if (cell) {
                                var w = cell.scrollWidth + 20;
                                if (w > maxW) maxW = w;
                            }
                        });
                        col.style.width = maxW + 'px';
                    });
                });

                // ── Yeni Nesil Akıllı Sıralama (Smart Sorting Engine) ──

                // ▸ Sıfırlama butonu (Python tarafından st.markdown içinde container içine eklendi)
                // Bu sayede arama yapıldığında Streamlit tüm tabloyu butonla birlikte siler.
                var wrapper = container.parentElement;
                var resetBtn = wrapper.querySelector('.sort-reset-btn');
                if (!resetBtn) return;
                
                // Yeni tablo render edildiğinde butonu her zaman gizli tut
                resetBtn.classList.remove('visible');

                // ── Temel Chunk-Based Doğal Sıralama (Natural Sort) ──
                function chunkify(str) {
                    var tokens = [];
                    // Rakamları ve harf bloklarını ayır (0.5 veya 10 gibi)
                    var regex = /(\d+\.?\d*)|(\D+)/g;
                    var match;
                    while ((match = regex.exec(str)) !== null) {
                        if (match[1] !== undefined && match[1] !== '') {
                            tokens.push(parseFloat(match[1]));
                        } else if (match[2] !== undefined && match[2] !== '') {
                            tokens.push(match[2].toLowerCase());
                        }
                    }
                    return tokens;
                }

                function compareValues(aVal, bVal, dir) {
                    var aEmpty = (aVal === '' || aVal.replace(/\s/g, '') === '');
                    var bEmpty = (bVal === '' || bVal.replace(/\s/g, '') === '');

                    // Kural: Boş veya null değerler DAİMA en sona atılır
                    if (aEmpty && bEmpty) return 0;
                    if (aEmpty) return 1;
                    if (bEmpty) return -1;

                    var dirMult = (dir === 'asc') ? 1 : -1;
                    var aChunks = chunkify(aVal);
                    var bChunks = chunkify(bVal);
                    var len = Math.max(aChunks.length, bChunks.length);

                    for (var i = 0; i < len; i++) {
                        var aC = aChunks[i];
                        var bC = bChunks[i];

                        if (aC === undefined) return -1 * dirMult; // Blok biterse küçüktür
                        if (bC === undefined) return 1 * dirMult;

                        var aIsNum = typeof aC === 'number';
                        var bIsNum = typeof bC === 'number';

                        if (aIsNum && bIsNum) {
                            if (aC !== bC) return (aC - bC) * dirMult;
                        } else if (aIsNum && !bIsNum) {
                            return -1 * dirMult; // ASCII kuralı: Sayılar metinlerden ÖNCE gelir
                        } else if (!aIsNum && bIsNum) {
                            return 1 * dirMult;
                        } else {
                            // İkisi de metin (localeCompare ÇÖPE ATILDI, düz ASCII string fallback)
                            if (aC !== bC) {
                                return (aC < bC ? -1 : 1) * dirMult;
                            }
                        }
                    }
                    return 0;
                }

                // ── Çoklu sıralama state (IDLE -> ASC -> DESC) ──
                var sortKeys = [];

                function findSortKeyIndex(colIdx) {
                    for (var i = 0; i < sortKeys.length; i++) {
                        if (sortKeys[i].col === colIdx) return i;
                    }
                    return -1;
                }

                // ── Çoklu kıstasa göre sırala ──
                function performSort() {
                    var tbody = table.querySelector('tbody');
                    var rows = Array.prototype.slice.call(tbody.querySelectorAll('tr'));

                    if (sortKeys.length === 0) {
                        // Sıralama kalmadıysa orijinal sıraya dön
                        rows.sort(function(a, b) {
                            return (parseInt(a.dataset.origIdx) || 0) - (parseInt(b.dataset.origIdx) || 0);
                        });
                    } else {
                        rows.sort(function(a, b) {
                            for (var k = 0; k < sortKeys.length; k++) {
                                var key = sortKeys[k];
                                var aCell = a.children[key.col];
                                var bCell = b.children[key.col];
                                var aVal = aCell ? aCell.textContent.trim() : '';
                                var bVal = bCell ? bCell.textContent.trim() : '';
                                
                                var cmp = compareValues(aVal, bVal, key.dir);
                                if (cmp !== 0) return cmp;
                            }
                            return (parseInt(a.dataset.origIdx) || 0) - (parseInt(b.dataset.origIdx) || 0);
                        });
                    }
                    rows.forEach(function(row) { tbody.appendChild(row); });
                }

                // ── Orijinal sıra indeksi kaydet ──
                var allRows = table.querySelectorAll('tbody tr');
                allRows.forEach(function(row, i) {
                    if (!row.dataset.origIdx) row.dataset.origIdx = i;
                });

                // ── Header sınıflarını ve rank göstergelerini güncelle ──
                function updateHeaderClasses() {
                    headers.forEach(function(h) {
                        h.classList.remove('sort-asc', 'sort-desc');
                        h.removeAttribute('data-sort-rank');
                    });
                    sortKeys.forEach(function(key, idx) {
                        var th = headers[key.col];
                        if (th) {
                            th.classList.add('sort-' + key.dir);
                            if (sortKeys.length > 1) {
                                th.setAttribute('data-sort-rank', String(idx + 1));
                            }
                        }
                    });
                    // Reset butonu görünürlüğü
                    if (sortKeys.length > 0) {
                        resetBtn.classList.add('visible');
                    } else {
                        resetBtn.classList.remove('visible');
                    }
                }

                // ── Reset butonu tıklama olayı ──
                resetBtn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    sortKeys = [];
                    updateHeaderClasses();
                    performSort();
                });

                // ── Sütun başlıklarına tıklama olayı ──
                headers.forEach(function(th, colIdx) {
                    if (th.dataset.sortBound) return;
                    th.dataset.sortBound = '1';
                    th.addEventListener('click', function(e) {
                        if (e.target.classList.contains('th-resize-handle')) return;

                        var existingIdx = findSortKeyIndex(colIdx);

                        if (e.shiftKey) {
                            // Çoklu Sıralama: IDLE -> ASC -> DESC -> IDLE
                            if (existingIdx !== -1) {
                                if (sortKeys[existingIdx].dir === 'asc') sortKeys[existingIdx].dir = 'desc';
                                else sortKeys.splice(existingIdx, 1);
                            } else {
                                sortKeys.push({ col: colIdx, dir: 'asc' });
                            }
                        } else {
                            // Tek Sütun Sıralaması:
                            if (existingIdx !== -1 && sortKeys.length === 1) {
                                if (sortKeys[0].dir === 'asc') sortKeys[0].dir = 'desc';
                                else sortKeys = []; // DESC'den sonra IDLE
                            } else {
                                sortKeys = [{ col: colIdx, dir: 'asc' }];
                            }
                        }

                        updateHeaderClasses();
                        performSort();
                    });
                });

                // ── Satır Seçme (Row Click) ──
                allRows.forEach(function(row){
                    if (row.dataset.clickBound) return;
                    row.dataset.clickBound = '1';
                    row.addEventListener('click', function(){
                        var wasSelected = this.classList.contains('row-selected');
                        var siblings = this.closest('tbody').querySelectorAll('tr');
                        siblings.forEach(function(r){ r.classList.remove('row-selected'); });
                        if(!wasSelected) this.classList.add('row-selected');
                    });
                });

            }, 500);
        })();
        </script>
        """
        _table_html = f'''
        <div class="table-wrapper">
            <div class="sort-reset-wrapper"><button class="sort-reset-btn">✕ Sıralamayı Sıfırla</button></div>
            <div class="table-container">{_raw_table}</div>
        </div>
        '''
        st.markdown(_table_html, unsafe_allow_html=True)
        # Tablo etkileşim JS'ini components.html ile enjekte et
        components.html(_table_js, height=0)
else:
    st.markdown(
        '<div class="guide-text">{}</div>'.format(t("search_guide")),
        unsafe_allow_html=True,
    )
    # Arama temizlendiğinde DOM'da yetim kalan sıralama sıfırlama butonlarını temizle
    components.html("""
    <script>
    (function(){
        var pd = window.parent ? window.parent.document : document;
        var wrappers = pd.querySelectorAll('.sort-reset-wrapper');
        wrappers.forEach(function(w){ w.remove(); });
    })();
    </script>
    """, height=0)

# ═══════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════

st.markdown(
    """
    <div class="app-footer">
        <div class="footer-line">© 2026 Nanomanyetik Bilimsel Cihazlar</div>
        <div class="footer-version">Depo Stok Yönetim Sistemi · v2.3</div>
    </div>
    """,
    unsafe_allow_html=True,
)
