
import os
from app import create_app


env_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(env_name)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"🚀 UrbanZyne / ZYNE AI API Sunucusu Başlatılıyor... (Port: {port})")
    print(f"💚 Canlılık Testi: http://localhost:{port}/health")
    print(f"📡 API Taban Adresi: http://localhost:{port}/api")
    app.run(host='0.0.0.0', port=port, debug=app.config.get('DEBUG', True))
