import os
import sys
import json
import socket
from pathlib import Path

# Streamlit CLI'yi programatik olarak çağırmak için
from streamlit.web import cli as stcli

def get_ip_address():
    """Makinenin yerel IP adresini bulur."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Bu adres erişilebilir olmasa bile (örn: internet yoksa) 
        # en uygun yerel IP'yi döndürür.
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def main():
    """
    Uygulama başlatıcı.
    
    1. Konfigürasyon dosyasını (config.json) kontrol eder.
    2. IP ve Port ayarlarını yapar.
    3. Streamlit uygulamasını başlatır.
    """
    # Exe'nin bulunduğu dizini bul (PyInstaller ile çalışırken sys.executable kullanılır)
    if getattr(sys, 'frozen', False):
        application_path = Path(sys.executable).parent
    else:
        application_path = Path(__file__).parent

    print(f"📂 Çalışma Dizini: {application_path}")

    # Varsayılan ayarlar
    config = {
        "ip": "0.0.0.0",  # Tüm ağ arayüzlerinden erişilebilir
        "port": 8501,
        "headless": True
    }

    # config.json varsa oku
    config_path = application_path / "config.json"
    if config_path.exists():
        print(f"⚙️  Ayarlar yükleniyor: {config_path}")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                config.update(user_config)
        except Exception as e:
            print(f"⚠️  Ayarlar okunamadı, varsayılanlar kullanılacak: {e}")
    else:
        # Config yoksa oluştur (kullanıcıya kolaylık olsun)
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            print(f"ℹ️  Varsayılan ayar dosyası oluşturuldu: {config_path}")
        except Exception:
            pass

    # Streamlit ortam değişkenlerini ayarla
    os.environ["STREAMLIT_SERVER_PORT"] = str(config["port"])
    os.environ["STREAMLIT_SERVER_ADDRESS"] = config["ip"]
    os.environ["STREAMLIT_SERVER_HEADLESS"] = str(config["headless"]).lower()
    
    # Uygulama dosyasının yolu
    # PyInstaller ile paketlendiğinde geçici klasörde (_MEI...) olur
    if getattr(sys, 'frozen', False):
        # PyInstaller _MEI klasörü
        bundle_dir = sys._MEIPASS
        app_path = os.path.join(bundle_dir, "app.py")
    else:
        # Normal Python çalıştırması
        app_path = os.path.join(application_path, "app.py")

    print(f"🚀 Başlatılıyor: http://{config['ip']}:{config['port']}")
    print(f"ℹ️  Yerel Ağ Adresi: http://{get_ip_address()}:{config['port']}")

    # Streamlit argümanlarını hazırla
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
    ]

    # Başlat
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()
