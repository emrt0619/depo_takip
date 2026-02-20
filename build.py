import os
import sys
import shutil
import platform
import subprocess

def build():
    """
    PyInstaller ile çalıştırılabilir dosya oluşturur.
    Hem MacOS hem de Ubuntu (Linux) üzerinde çalışır.
    """
    # İşletim sistemini kontrol et
    os_name = platform.system()
    separator = ";" if os_name == "Windows" else ":"
    
    print(f"🖥️  İşletim Sistemi: {os_name}")
    print("📦 Paketleme işlemi başlıyor...")

    # Gerekli dosyalar
    # Format: "kaynak_dosya:hedef_klasör"
    datas = [
        f"app.py{separator}.",  # app.py'yi kök dizine koy
        f"logo.jpg{separator}.", # logo.jpg'yi kök dizine koy
    ]

    # Data klasörü varsa ekle
    if os.path.exists("data"):
        datas.append(f"data{separator}data")

    # .streamlit/config.toml varsa ekle
    if os.path.exists(".streamlit/config.toml"):
        datas.append(f".streamlit/config.toml{separator}.streamlit")

    # PyInstaller komutunu hazırla
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",  # Konsol penceresi açılmasın (MacOS/Windows)
        "--name", "NanomanyetikStok",
        "--clean",
        # Hidden imports: Streamlit'in dinamik yüklediği paketler
        "--hidden-import", "streamlit",
        "--hidden-import", "pandas",
        "--hidden-import", "pyarrow",
        "--hidden-import", "openpyxl",
        "--hidden-import", "altair",
        "--hidden-import", "pillow",
        "--hidden-import", "rich",
        "--hidden-import", "click",
        "--hidden-import", "tornado",
        "--hidden-import", "blinker",
        "--hidden-import", "watchdog",
    ]

    # Veri dosyalarını ekle
    for data in datas:
        cmd.extend(["--add-data", data])

    # Ana dosya
    cmd.append("run_app.py")

    print(f"🚀 Çalıştırılan komut: {' '.join(cmd)}")

    # Komutu çalıştır
    try:
        subprocess.check_call(cmd)
        print("\n✅ Paketleme tamamlandı!")
        print(f"📂 Çalıştırılabilir dosya 'dist/' klasöründe: dist/NanomanyetikStok")
        if os_name == "Darwin": # MacOS
             print("ℹ️  MacOS'ta çalıştırmadan önce izin vermeniz gerekebilir: chmod +x dist/NanomanyetikStok")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Hata oluştu: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # PyInstaller kurulu mu kontrol et
    try:
        import PyInstaller
    except ImportError:
        print("⚠️  PyInstaller bulunamadı. Yükleniyor...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller yüklendi.")

    build()
