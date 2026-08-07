# UrbanZyne / ZYNE AI — SmartLead AI Mimarisi

UrbanZyne (yapı ve malzeme teknolojileri) için geliştirilmiş, yapay zekâ destekli lead toplama
sistemi. Ziyaretçiler **ZYNE AI** adlı yapay zekâ asistanıyla yapı malzemelerinin yeniden kullanımı,
malzeme pasaportu, karbon tasarrufu gibi konularda sohbet eder ve iletişim/proje bilgilerini bırakır;
bu kayıtlar backend üzerinden yönetilir.

Backend, **Separation of Concerns** ilkesine göre katmanlara ayrılmış sade bir Flask REST API'sidir.
Frontend tamamen **Wix Velo** üzerinden sunulur (`wix_velo_code.js`); backend'in kendi HTML sayfası yoktur.

## Mimari

```
zyna-ai/
├── run.py                      # Sunucu giriş noktası (app = create_app())
├── config.py                   # Ayarlar ve gizli anahtarlar (.env okur)
├── requirements.txt
├── render.yaml                 # Render deploy ayarları (build/start command, env var listesi)
├── .env                        # Gizli anahtarlar (Git'e eklenmez)
│
└── app/
    ├── __init__.py              # Uygulama fabrikası (create_app) + /health
    ├── database.py               # SQLite işlemleri (SADECE burada SQL var)
    ├── routes.py                  # /api/* rotaları (sadece yönlendirme, SQL/AI kodu yok)
    └── services/
        └── ai_service.py          # Groq / Grok (xAI) çağrıları (SADECE burada AI kodu var)
```

Katmanlar arası kural: `database.py` dışında SQL yazılmaz, `ai_service.py` dışında AI API'sine
istek atılmaz, `routes.py` yalnızca bu iki katmanın fonksiyonlarını çağırır.

## Kurulum (yerel geliştirme)

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # sonra kendi anahtarlarınızı girin
python run.py
```

Sunucu varsayılan olarak `http://localhost:5001` adresinde açılır.

## Ortam Değişkenleri (`.env`)

| Değişken | Açıklama |
|---|---|
| `SECRET_KEY` | Flask oturum/güvenlik anahtarı |
| `DATABASE_URL` | SQLite dosya adı (varsayılan: `smartlead.db`) |
| `AI_PROVIDER` | `groq` veya `grok` — hangi AI sağlayıcısının kullanılacağını seçer |
| `GROQ_API_KEY` | Groq API anahtarı (`AI_PROVIDER=groq` iken kullanılır) |
| `GROK_API_KEY` | Grok / xAI API anahtarı (`AI_PROVIDER=grok` iken kullanılır) |
| `CORS_ORIGINS` | İzin verilen originler (Wix sitenizin adresi veya `*`) |
| `BUSINESS_CONTEXT` | ZYNE AI'nın kişiliğini ve görevini tanımlayan sistem talimatı |

API anahtarı girilmezse veya geçersizse sistem otomatik olarak **demo moduna** düşer; sunucu çökmez,
anlamlı örnek yanıtlar döner.

## API Uç Noktaları

Taban adres (canlı): `https://zyna-ai-1.onrender.com`

| Metod | Yol | Açıklama |
|---|---|---|
| `GET` | `/health` | Sunucu canlılık kontrolü |
| `POST` | `/api/sohbet` | ZYNE AI ile sohbet. Body: `{"mesaj": "...", "gecmis": [...]}` |
| `POST` | `/api/leads` | Yeni lead kaydeder. Zorunlu alanlar: `isim, telefon, eposta, sehir, proje_turu, talep_turu, malzeme_turu, miktar`. Opsiyonel: `firma_adi` |
| `GET` | `/api/leads` | Tüm lead kayıtlarını listeler |

Tüm yanıtlar `{"basari": true/false, ...}` biçiminde JSON döner; hatalar 400/503/500 durum
kodlarıyla birlikte `hata` alanında açıklanır.

## Frontend (Wix Velo)

Arayüz Wix Studio üzerinde kurulur; `wix_velo_code.js` dosyası sayfanın Velo kod paneline
yapıştırılır ve backend'deki `/api/sohbet` ile `/api/leads` uç noktalarına bağlanır. Kodun
çalışması için Wix editöründe ilgili elemanlara (`#inputIsim`, `#btnSor`, `#repeaterLeads` vb.)
dosyadaki ID'lerin birebir atanmış olması gerekir.

## Deploy (Render)

`render.yaml` build/start komutlarını ve gerekli env değişkenlerini tanımlar
(`buildCommand: pip install -r requirements.txt`, `startCommand: gunicorn run:app`). Gizli
değerler (`SECRET_KEY`, `GROQ_API_KEY`, `GROK_API_KEY`, `BUSINESS_CONTEXT`) Render Dashboard'dan
elle girilmelidir; repoya yazılmaz.

## Güvenlik

- SQL sorgularında `?` yer tutucusu kullanılır (SQL Injection koruması).
- `.env` `.gitignore` içinde, hiçbir zaman Git'e eklenmez.
- Dış servis çağrıları (`database.py`, `ai_service.py`) `try/except` ile sarılıdır; hata kullanıcıya
  güvenli bir JSON olarak döner.
