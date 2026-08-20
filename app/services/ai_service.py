"""
Modül C: Yapay Zekâ Servisi (app/services/ai_service.py)
---------------------------------------------------------
Kullanıcı mesajını alıp seçilen Yapay Zekâ servisine (Groq veya Grok/xAI) gönderen ve yanıtı
döndüren servis katmanı. Sağlayıcı, config.py'deki AI_PROVIDER ayarıyla seçilir.
MİMARİ IZOLASYON: Bu dosya Flask, HTTP rotaları veya veritabanı kavramlarını BİLMEZ. Sadece AI ile konuşur.
"""

import requests
from flask import current_app


class AIServiceError(Exception):
    """Yapay zekâ servisine özel hata sınıfı"""
    pass


class AIService:
    """Groq veya Grok (xAI) API'leri ile iletişim kuran Yapay Zekâ Servis Sınıfı"""

    def _get_system_context(self):
        """Sistem talimatını (BUSINESS_CONTEXT) yapılandırmadan okur"""
        try:
            return current_app.config.get(
                'BUSINESS_CONTEXT',
                "Sen samimi bir işletme asistanısın. Müşterilere yardımcı ol ve iletişim bilgilerini iste."
            )
        except RuntimeError:
            # Flask uygulama bağlamı dışında çağrılırsa varsayılan metni kullan
            return "Sen samimi bir işletme asistanısın. Müşterilere yardımcı ol."

    def _get_provider(self):
        """Aktif AI sağlayıcısını yapılandırmadan okur (groq / grok)"""
        try:
            return (current_app.config.get('AI_PROVIDER', 'groq') or 'groq').strip().lower()
        except RuntimeError:
            return 'groq'

    def _get_api_key(self, provider):
        """Seçilen sağlayıcıya ait API anahtarını yapılandırmadan okur"""
        try:
            if provider == 'grok':
                return current_app.config.get('GROK_API_KEY', '')
            return current_app.config.get('GROQ_API_KEY', '')
        except RuntimeError:
            return ''

    def _mesajlari_olustur(self, mesaj, gecmis):
        """Sistem talimatı + geçmiş + yeni mesajdan oluşan standart mesaj dizisini üretir"""
        messages = [{"role": "system", "content": self._get_system_context()}]

        if gecmis and isinstance(gecmis, list):
            for entry in gecmis:
                if isinstance(entry, dict) and "role" in entry and "content" in entry:
                    messages.append({
                        "role": entry["role"],
                        "content": entry["content"]
                    })

        messages.append({"role": "user", "content": mesaj.strip()})
        return messages

    def yanit_uret(self, mesaj, gecmis=None):
        """
        Kullanıcı mesajı ve sohbet geçmişini alarak yapılandırmada seçilen AI sağlayıcısına
        (Groq veya Grok/xAI) istek atar.
        """
        if not mesaj or not mesaj.strip():
            raise AIServiceError("Mesaj boş olamaz.")

        provider = self._get_provider()
        api_key = self._get_api_key(provider)

        # Anahtar yoksa veya placeholder ise demo modunda çalış
        if not api_key or api_key.startswith('gsk_demo') or api_key == 'xai_demo_key_placeholder':
            return self._demo_modu_yaniti(mesaj)

        try:
            if provider == 'grok':
                return self._grok_istek(mesaj, gecmis, api_key)
            return self._groq_istek(mesaj, gecmis, api_key)
        except requests.RequestException:
            # Ağ/bağlantı hatasıı durumunda demo yanıtına düş
            return self._demo_modu_yaniti(mesaj, network_error=True)

    def _groq_istek(self, mesaj, gecmis, api_key):
        """Groq (OpenAI uyumlu Chat Completions) API'sine istek atar. Model: llama-3.1-8b-instant"""
        headers = {"Authorization": "Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "openai/gpt-oss-120b",
            "messages": self._mesajlari_olustur(mesaj, gecmis),
            "temperature": 0.7,
            "max_tokens": 500
        }

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers, json=payload, timeout=12
        )

        if response.status_code == 200:
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"].strip()
            raise AIServiceError("Yapay zekâ servisinden geçerli yanıt alınamadı.")
        elif response.status_code == 401:
            return self._demo_modu_yaniti(mesaj)
        else:
            raise AIServiceError(f"Yapay zekâ servisi hata döndürdü (HTTP {response.status_code}): {response.text}")

    def _grok_istek(self, mesaj, gecmis, api_key):
        """Grok (xAI) Responses API'sine istek atar. Model: grok-4.5"""
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "grok-4.5",
            "input": self._mesajlari_olustur(mesaj, gecmis)
        }

        response = requests.post(
            "https://api.x.ai/v1/responses",
            headers=headers, json=payload, timeout=20
        )

        if response.status_code == 200:
            data = response.json()
            metin = self._grok_yanitini_ayikla(data)
            if metin:
                return metin.strip()
            raise AIServiceError("Yapay zekâ servisinden geçerli yanıt alınamadı.")
        elif response.status_code == 401:
            return self._demo_modu_yaniti(mesaj)
        else:
            raise AIServiceError(f"Yapay zekâ servisi hata döndürdü (HTTP {response.status_code}): {response.text}")

    def _grok_yanitini_ayikla(self, data):
        """xAI Responses API yanıtından metni çıkarır (SDK'sız, ham JSON üzerinden)"""
        if isinstance(data.get("output_text"), str):
            return data["output_text"]

        for item in data.get("output", []):
            if item.get("type") == "message":
                for parca in item.get("content", []):
                    if parca.get("type") in ("output_text", "text") and parca.get("text"):
                        return parca["text"]
        return None

    def _demo_modu_yaniti(self, mesaj, network_error=False):
        """
        Groq API anahtarı girilmediğinde veya demo ortamında çalışan akıllı simülasyon yanıtı.
        """
        msg_lower = mesaj.lower()

        if "traverten" in msg_lower or "parke" in msg_lower or "çelik" in msg_lower or "seramik" in msg_lower or "ahşap" in msg_lower:
            return ("Belirttiğiniz malzeme büyük ölçüde yeniden kullanılabilir görünüyor. Ortalama geri kazanım "
                    "oranı, söküm/taşıma/depolama önerileri ve tahmini piyasa değeri için ekibimizin size özel bir "
                    "malzeme değerlendirmesi yapabilmesi adına Ad Soyad, Telefon, E-posta ve Şehir bilgilerinizi "
                    "formdan iletebilir misiniz?")

        if "pasaport" in msg_lower or "sertifika" in msg_lower or "belge" in msg_lower:
            return ("Malzemeniz için dijital malzeme pasaportu oluşturabiliriz. Bunun için marka, ölçü, yangın "
                    "sınıfı, durum ve üretim yılı gibi teknik bilgilere ihtiyacımız var. Detaylı değerlendirme "
                    "için lütfen iletişim bilgilerinizi ve malzeme türünü formdan paylaşın.")

        if "karbon" in msg_lower or "tasarruf" in msg_lower or "sürdürülebilir" in msg_lower or "leed" in msg_lower:
            return ("Yeniden kullanım yoluyla karbon tasarrufu, atık azaltımı ve döngüsel ekonomiye katkı "
                    "hesaplayabiliriz. LEED veya benzeri sertifikasyon hedefleriniz varsa uygun geri kazanılmış "
                    "malzemeleri de önerebiliriz. Proje türünüzü ve şehrinizi formdan iletirseniz size özel bir "
                    "rapor hazırlayalım.")

        if "söküm" in msg_lower or "sokum" in msg_lower or "bina" in msg_lower or "planlama" in msg_lower:
            return ("Söküm planlaması için bina kat sayısı, lokasyon ve malzeme türü bilgilerine ihtiyacımız var. "
                    "Uzman ekibimizin sizinle iletişime geçmesi için lütfen Ad Soyad, Telefon ve Şehir "
                    "bilgilerinizi formdan bırakın.")

        if "değer" in msg_lower or "deger" in msg_lower or "fiyat" in msg_lower or "m2" in msg_lower or "m²" in msg_lower:
            return ("Yaklaşık piyasa değeri tahmini için malzeme türü ve miktar bilgisine ihtiyacımız var. "
                    "Detaylı bir fiyatlandırma raporu için lütfen formdan iletişim bilgilerinizi ve talep "
                    "türünüzü (satış / satın alma / danışmanlık) belirtin.")

        return (f"Merhaba! UrbanZyne'in yapay zekâ asistanı ZYNE AI'yım. Sorduğunuz '{mesaj}' sorusuyla ilgili "
                f"size yardımcı olmaktan mutluluk duyarım. Malzeme analizi, yeniden kullanım danışmanlığı veya "
                f"proje desteği için lütfen aşağıdaki formdan iletişim bilgilerinizi ve proje detaylarınızı "
                f"iletebilirsiniz!")


# Modül düzeyinde tekil nesne örneği
ai_service = AIService()
