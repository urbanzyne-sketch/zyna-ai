"""
Modül E: Uygulama Fabrikası (app/__init__.py)
---------------------------------------------
Ayarları, CORS'u, veritabanını ve rotaları bir araya getiren uygulama fabrikası.
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import config_by_name
from app import database


def create_app(config_name=None):
    """
    Flask Uygulama Fabrikası
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    
    # Yapılandırmayı yükle
    config_class = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(config_class)

    # CORS (Cross-Origin Resource Sharing) etkinleştir
    CORS(app, resources={r"/*": {"origins": app.config.get('CORS_ORIGINS', '*')}})

    # Veritabanını uygulama bağlamı içinde ilklendir
    with app.app_context():
        database.init_db(app)

    # Rotaları (Blueprint) kaydet — sadece RESTful API, frontend Wix Velo üzerinden sunulur
    from app.routes import api_bp
    app.register_blueprint(api_bp)

    # Sunucu Canlılık Kontrolü (Healthcheck Endpoint)
    @app.route('/health')
    def healthcheck():
        return jsonify({
            "status": "healthy",
            "message": "UrbanZyne / ZYNE AI Backend Ortamı Aktif ve Çalışıyor!",
            "ai_provider": app.config.get('AI_PROVIDER', 'groq')
        }), 200

    return app


# Modül seviyesinde hazır bir uygulama nesnesi: bazı WSGI sunucuları (örn. Render'da
# yanlışlıkla "gunicorn app:app" olarak ayarlanmış bir başlatma komutu) doğrudan bu
# paketin içinde "app" adlı bir nesne arar. run.py ile aynı fabrikayı kullanarak
# üretildiği için davranış birebir aynıdır; asıl önerilen komut hâlâ "gunicorn run:app"tır.
app = create_app()
