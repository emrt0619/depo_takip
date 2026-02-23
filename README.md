<p align="center">
  <img src="logo.jpg" width="120" alt="Nanomanyetik Logo" />
</p>

<h1 align="center">Nanomanyetik — Depo Stok Yönetim Sistemi</h1>

<p align="center">
  <strong>Bilimsel cihaz envanterini hızlı, kolay ve modern bir arayüzle yönetin.</strong><br/>
  <sub>Excel → Parquet ETL · Anlık Arama · Çift Dil (TR/EN) · Dark UI</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/streamlit-1.0+-FF4B4B?logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/format-Apache%20Parquet-50ABF1?logo=apache&logoColor=white" />
  <img src="https://img.shields.io/badge/license-MIT-green" />
</p>

---

## 📖 Hakkında

**Nanomanyetik Depo Takip**, [Nanomanyetik Bilimsel Cihazlar](https://nanomanyetik.com) şirketinin depo stok verilerini yönetmek için geliştirilmiş bir web uygulamasıdır. Yöneticiler Excel dosyalarını sisteme yükler, sistem bunları yüksek performanslı Parquet formatına dönüştürür. Kullanıcılar ise anlık arama yaparak stok bilgilerine kolayca erişir.

### Ne İşe Yarar?

| Sorun | Çözüm |
|-------|-------|
| Binlerce satırlık Excel dosyasında ürün aramak yavaş | ⚡ Parquet formatı + anlık arama |
| Stok bilgilerine herkes erişemiyor | 🌐 Web tabanlı — tarayıcıdan erişim |
| Excel'i yanlış kişiler düzenleyebilir | 🔐 Şifre korumalı admin paneli |
| Tek dil (yabancı partnerler için sorun) | 🌍 Türkçe / İngilizce dil desteği |

---

## ✨ Özellikler

- **📊 Excel → Parquet ETL** — `.xlsx` dosyaları yüklendiğinde otomatik olarak Apache Parquet formatına dönüştürülür (10-50× daha küçük, çok daha hızlı okuma)
- **🔍 Anlık Arama** — Tüm sütunlarda eşzamanlı, case-insensitive arama
- **🎯 Satır Seçimi** — Arama sonuçlarında bir hücreye tıklayın, tüm satır vurgulanır
- **🌍 Çift Dil** — Bayrak ikonlu tek butonla Türkçe ↔ İngilizce geçiş
- **🔐 Admin Paneli** — Şifre korumalı yönetici girişi (sidebar)
- **🎨 Premium Dark UI** — Glassmorphism, neon vurgular, mikro-animasyonlar
- **📱 Responsive** — Masaüstü ve tablet ekranlara uyumlu
- **📦 Taşınabilir Build** — PyInstaller ile tek dosya `.exe` oluşturma desteği

---

## 🖼️ Ekran Görüntüleri

<details>
<summary><strong>Ana Sayfa (sidebar kapalı)</strong></summary>
<br/>

Başlangıçta sidebar kapalı gelir. Sol üstteki ☰ butonuyla açılır.

- Nanomanyetik logolu başlık
- İstatistik kartları (toplam kayıt, veri alanı, veritabanı boyutu, son güncelleme)
- Tam genişlik arama çubuğu
</details>

<details>
<summary><strong>Sidebar (açık)</strong></summary>
<br/>

- Şirket logosu ve marka adı
- Bayrak ikonlu dil değiştirme butonu (🇬🇧 / 🇹🇷)
- Yönetici girişi (expander)
- Admin login sonrası dosya yükleme alanı
</details>

---

## 🚀 Kurulum

### Gereksinimler

- Python 3.9+
- pip

### Adımlar

```bash
# 1. Repoyu klonlayın
git clone https://github.com/KULLANICI_ADI/depo_takip.git
cd depo_takip

# 2. Sanal ortam oluşturun (önerilir)
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 4. Uygulamayı başlatın
streamlit run app.py
```

Tarayıcınızda `http://localhost:8501` adresine gidin.

---

## 📁 Proje Yapısı

```
depo_takip/
├── app.py                 # Ana uygulama (Streamlit)
├── sidebar_toggle.js      # Sidebar aç/kapat butonu (JS)
├── build.py               # PyInstaller ile exe paketleme
├── run_app.py             # Paketlenmiş uygulama için başlatıcı
├── requirements.txt       # Python bağımlılıkları
├── logo.jpg               # Nanomanyetik logosu
├── Sample_Warehous.xlsx   # Örnek veri dosyası
├── .streamlit/
│   └── config.toml        # Streamlit tema ayarları
└── data/
    └── *.parquet          # Dönüştürülmüş veri (otomatik oluşur)
```

---

## 🔧 Kullanım

### Veri Yükleme (Admin)

1. Sidebar'ı açın (☰ butonu)
2. **Yönetici Girişi** expander'ını açın
3. Admin şifresini girin → **Giriş Yap**
4. `.xlsx` dosyanızı sürükleyip bırakın
5. Sistem otomatik olarak Parquet'e dönüştürür

### Arama

Arama çubuğuna herhangi bir kelime yazın — stok kodu, ürün adı, grup, birim veya diğer tüm alanlar aynı anda taranır.

### Dil Değiştirme

Sidebar'daki bayraklı butonu tıklayın:
- 🇬🇧 **English** → İngilizce'ye geç
- 🇹🇷 **Türkçe** → Türkçe'ye geç

---

## 📦 Paketleme (Opsiyonel)

Uygulamayı tek bir çalıştırılabilir dosya (`.exe`) olarak dağıtmak için:

```bash
python build.py
```

Çıktı: `dist/NanomanyetikStok.exe`

---

## 🛠️ Teknoloji Yığını

| Katman | Teknoloji |
|--------|-----------|
| Frontend | [Streamlit](https://streamlit.io) + Custom CSS/JS |
| Veri Formatı | [Apache Parquet](https://parquet.apache.org) (Snappy sıkıştırma) |
| Veri İşleme | [Pandas](https://pandas.pydata.org) + [PyArrow](https://arrow.apache.org) |
| Excel Okuma | [openpyxl](https://openpyxl.readthedocs.io) |
| Paketleme | [PyInstaller](https://pyinstaller.org) |
| Tema | Dark glassmorphism — Inter font |

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

---

<p align="center">
  <sub>Geliştirici: <strong>Nanomanyetik Bilimsel Cihazlar</strong> · v2.2</sub>
</p>