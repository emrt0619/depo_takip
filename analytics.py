"""
=============================================================================
  ANALİTİK MODÜLÜ — JSON Tabanlı Olay Loglama ve İstatistik
  Nanomanyetik Depo Stok Yönetim Sistemi için hafif analitik altyapısı
=============================================================================
"""

import json
import os
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import List, Dict, Optional, Any

# ═══════════════════════════════════════════════════════════════════════════
# SABİTLER
# ═══════════════════════════════════════════════════════════════════════════

DATA_DIR = Path(__file__).resolve().parent / "data"
ANALYTICS_PATH = DATA_DIR / "analytics.jsonl"
MAX_LOG_SIZE_MB = 50  # Dosya boyutu limiti (MB)

# Ay isimleri (TR/EN)
MONTH_NAMES = {
    "tr": ["Oca", "Şub", "Mar", "Nis", "May", "Haz",
           "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"],
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
}

DAY_NAMES = {
    "tr": ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"],
    "en": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
}


# ═══════════════════════════════════════════════════════════════════════════
# OLAY KAYDI
# ═══════════════════════════════════════════════════════════════════════════

def _ensure_data_dir():
    """Data dizininin var olduğundan emin ol."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _check_log_size():
    """Log dosyası boyutunu kontrol et, limiti aşarsa eski kayıtları temizle."""
    if not ANALYTICS_PATH.exists():
        return
    size_mb = ANALYTICS_PATH.stat().st_size / (1024 * 1024)
    if size_mb > MAX_LOG_SIZE_MB:
        # Son %50'yi tut
        try:
            with open(ANALYTICS_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()
            half = len(lines) // 2
            with open(ANALYTICS_PATH, "w", encoding="utf-8") as f:
                f.writelines(lines[half:])
        except Exception:
            pass


def log_event(event_type: str, data: Optional[Dict[str, Any]] = None):
    """
    Analitik olayını JSONL dosyasına yaz.

    Args:
        event_type: Olay tipi (page_visit, search, admin_login, file_upload)
        data: Ek veri sözlüğü
    """
    try:
        _ensure_data_dir()
        _check_log_size()

        event = {
            "ts": datetime.now().isoformat(),
            "type": event_type,
        }
        if data:
            event["data"] = data

        with open(ANALYTICS_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        # Analitik kaydı asla ana uygulamayı bozmamalı
        pass


# ═══════════════════════════════════════════════════════════════════════════
# VERİ OKUMA
# ═══════════════════════════════════════════════════════════════════════════

def _load_events(
    event_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[Dict]:
    """
    JSONL dosyasından olayları oku ve filtrele.
    """
    if not ANALYTICS_PATH.exists():
        return []

    events = []
    try:
        with open(ANALYTICS_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Tip filtresi
                if event_type and ev.get("type") != event_type:
                    continue

                # Tarih filtresi
                try:
                    ev_time = datetime.fromisoformat(ev["ts"])
                except (KeyError, ValueError):
                    continue

                if start_date and ev_time < start_date:
                    continue
                if end_date and ev_time > end_date:
                    continue

                ev["_dt"] = ev_time
                events.append(ev)
    except Exception:
        pass

    return events


# ═══════════════════════════════════════════════════════════════════════════
# İSTATİSTİK FONKSİYONLARI
# ═══════════════════════════════════════════════════════════════════════════

def get_overview_stats() -> Dict[str, int]:
    """Genel istatistikleri döndür."""
    events = _load_events()
    total_visits = sum(1 for e in events if e["type"] == "page_visit")
    total_searches = sum(1 for e in events if e["type"] == "search")
    total_logins = sum(1 for e in events if e["type"] == "admin_login")
    total_uploads = sum(1 for e in events if e["type"] == "file_upload")

    # Bugünkü istatistikler
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_visits = sum(
        1 for e in events
        if e["type"] == "page_visit" and e.get("_dt", datetime.min) >= today
    )
    today_searches = sum(
        1 for e in events
        if e["type"] == "search" and e.get("_dt", datetime.min) >= today
    )

    return {
        "total_visits": total_visits,
        "total_searches": total_searches,
        "total_logins": total_logins,
        "total_uploads": total_uploads,
        "today_visits": today_visits,
        "today_searches": today_searches,
    }


def get_visit_stats_by_year() -> Dict[int, int]:
    """Yıl bazında ziyaret sayısı."""
    events = _load_events(event_type="page_visit")
    year_counts = Counter()
    for ev in events:
        dt = ev.get("_dt")
        if dt:
            year_counts[dt.year] += 1
    return dict(sorted(year_counts.items()))


def get_visit_stats_by_month(year: Optional[int] = None) -> Dict[int, int]:
    """Ay bazında ziyaret sayısı (1-12)."""
    if year is None:
        year = datetime.now().year
    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31, 23, 59, 59)
    events = _load_events(event_type="page_visit", start_date=start, end_date=end)

    month_counts = {m: 0 for m in range(1, 13)}
    for ev in events:
        dt = ev.get("_dt")
        if dt:
            month_counts[dt.month] += 1
    return month_counts


def get_daily_visits(days: int = 30) -> Dict[str, int]:
    """Son N gün günlük ziyaret sayısı."""
    end = datetime.now()
    start = end - timedelta(days=days)
    events = _load_events(event_type="page_visit", start_date=start, end_date=end)

    daily = defaultdict(int)
    for ev in events:
        dt = ev.get("_dt")
        if dt:
            daily[dt.strftime("%Y-%m-%d")] += 1

    # Tüm günleri doldur (boş günler 0 olsun)
    result = {}
    for i in range(days + 1):
        day = (start + timedelta(days=i)).strftime("%Y-%m-%d")
        result[day] = daily.get(day, 0)
    return result


def get_hourly_distribution() -> Dict[int, int]:
    """Saatlik aktivite dağılımı (0-23)."""
    events = _load_events(event_type="page_visit")
    hourly = {h: 0 for h in range(24)}
    for ev in events:
        dt = ev.get("_dt")
        if dt:
            hourly[dt.hour] += 1
    return hourly


def get_weekday_distribution(lang: str = "tr") -> Dict[str, int]:
    """Haftanın günü bazında dağılım."""
    events = _load_events(event_type="page_visit")
    weekday_counts = {i: 0 for i in range(7)}
    for ev in events:
        dt = ev.get("_dt")
        if dt:
            weekday_counts[dt.weekday()] += 1

    names = DAY_NAMES.get(lang, DAY_NAMES["tr"])
    return {names[i]: weekday_counts[i] for i in range(7)}


def get_search_stats() -> Dict[str, Any]:
    """Arama istatistikleri."""
    events = _load_events(event_type="search")
    total = len(events)

    if total == 0:
        return {
            "total": 0,
            "daily_avg": 0,
            "unique_terms": 0,
            "avg_results": 0,
        }

    # Tarih aralığı
    dates = [ev["_dt"] for ev in events if "_dt" in ev]
    if dates:
        min_date = min(dates)
        max_date = max(dates)
        day_span = max((max_date - min_date).days, 1)
        daily_avg = round(total / day_span, 1)
    else:
        daily_avg = 0

    # Benzersiz terimler
    terms = [
        ev.get("data", {}).get("query", "").lower().strip()
        for ev in events
        if ev.get("data", {}).get("query")
    ]
    unique_terms = len(set(terms))

    # Ortalama sonuç sayısı
    result_counts = [
        ev.get("data", {}).get("result_count", 0)
        for ev in events
        if "data" in ev and "result_count" in ev["data"]
    ]
    avg_results = round(sum(result_counts) / len(result_counts), 1) if result_counts else 0

    return {
        "total": total,
        "daily_avg": daily_avg,
        "unique_terms": unique_terms,
        "avg_results": avg_results,
    }


def get_top_searches(limit: int = 10) -> List[tuple]:
    """En çok aranan terimler."""
    events = _load_events(event_type="search")
    terms = [
        ev.get("data", {}).get("query", "").lower().strip()
        for ev in events
        if ev.get("data", {}).get("query")
    ]
    return Counter(terms).most_common(limit)


def get_recent_admin_logins(limit: int = 20) -> List[Dict]:
    """Son admin giriş denemeleri."""
    events = _load_events(event_type="admin_login")
    events.sort(key=lambda e: e.get("ts", ""), reverse=True)
    result = []
    for ev in events[:limit]:
        result.append({
            "timestamp": ev.get("_dt", datetime.min).strftime("%d.%m.%Y — %H:%M:%S"),
            "success": ev.get("data", {}).get("success", False),
        })
    return result


def get_search_daily_trend(days: int = 30) -> Dict[str, int]:
    """Son N gün günlük arama sayısı."""
    end = datetime.now()
    start = end - timedelta(days=days)
    events = _load_events(event_type="search", start_date=start, end_date=end)

    daily = defaultdict(int)
    for ev in events:
        dt = ev.get("_dt")
        if dt:
            daily[dt.strftime("%Y-%m-%d")] += 1

    result = {}
    for i in range(days + 1):
        day = (start + timedelta(days=i)).strftime("%Y-%m-%d")
        result[day] = daily.get(day, 0)
    return result


def get_available_years() -> List[int]:
    """Veri bulunan yılları döndür."""
    events = _load_events(event_type="page_visit")
    years = set()
    for ev in events:
        dt = ev.get("_dt")
        if dt:
            years.add(dt.year)
    if not years:
        years.add(datetime.now().year)
    return sorted(years)


def clear_old_logs(days: int = 180):
    """Belirtilen gün sayısından eski logları sil."""
    cutoff = datetime.now() - timedelta(days=days)
    events = _load_events()
    kept = [
        ev for ev in events
        if ev.get("_dt", datetime.min) >= cutoff
    ]
    try:
        with open(ANALYTICS_PATH, "w", encoding="utf-8") as f:
            for ev in kept:
                ev_copy = {k: v for k, v in ev.items() if k != "_dt"}
                f.write(json.dumps(ev_copy, ensure_ascii=False) + "\n")
        return len(events) - len(kept)
    except Exception:
        return 0


def export_events_csv() -> Optional[str]:
    """Olayları CSV formatında döndür."""
    events = _load_events()
    if not events:
        return None

    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp", "Event Type", "Details"])
    for ev in events:
        details = json.dumps(ev.get("data", {}), ensure_ascii=False)
        writer.writerow([ev.get("ts", ""), ev.get("type", ""), details])
    return output.getvalue()
