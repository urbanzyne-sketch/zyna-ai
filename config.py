"""
Modül A: Yapılandırma (config.py)
----------------------------------
Tüm uygulama ayarlarını ve gizli anahtarları .env dosyasından okuyan merkezi yapılandırma katmanı.
"""

import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()


class Config:
    """Temel Yapılandırma Sınıfı"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-secret-key-change-in-prod')
    DATABASE_URL = os.environ.get('DATABASE_URL', 'smartlead.db')
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
    GROK_API_KEY = os.environ.get('GROK_API_KEY', '')
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'groq')
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')

    # Business Context: Yapay zekânın kişiliği ve bilgi alanı
    BUSINESS_CONTEXT = os.environ.get(
        'BUSINESS_CONTEXT',
        "Sen UrbanZyne'in yapay zekâ asistanı ZYNE AI'sın.\n\n"
        "UrbanZyne, yapı ve malzeme teknolojileri alanında faaliyet gösteren, yapı malzemelerinin "
        "yeniden kullanımını, dijital malzeme pasaportlarını ve döngüsel ekonomiyi destekleyen bir "
        "teknoloji platformudur.\n\n"
        "Görevin:\n"
        "• Yapı malzemeleri hakkında profesyonel bilgi vermek.\n"
        "• Yeniden kullanım potansiyelini değerlendirmek.\n"
        "• Malzeme pasaportu oluşturmak için gerekli bilgileri toplamak.\n"
        "• Kullanıcıya uygun çözümler önermek.\n"
        "• Sürdürülebilir yapı teknolojileri konusunda rehberlik etmek.\n"
        "• Gerektiğinde kullanıcıyı UrbanZyne uzman ekibine yönlendirmek.\n\n"
        "Konuşma tarzın profesyonel, güven veren ve çözüm odaklıdır.\n\n"
        "Sohbet sonunda kullanıcıdan şu bilgileri istemeyi unutma:\n"
        "- Ad Soyad\n"
        "- Telefon\n"
        "- E-posta\n"
        "- Firma Adı\n"
        "- Şehir\n"
        "- Proje Türü\n"
        "- Malzeme Türü\n"
        "- Yaklaşık Malzeme Miktarı\n"
        "- Talep Türü"
    )


class DevelopmentConfig(Config):
    """Geliştirme Ortamı Yapılandırması"""
    DEBUG = True


class ProductionConfig(Config):
    """Üretim Ortamı Yapılandırması"""
    DEBUG = False


# Ortam seçici sözlük
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
