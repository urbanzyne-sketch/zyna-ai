"""
Modül D: Rotalar (app/routes.py)
--------------------------------
HTTP isteklerini karşılayan, doğrulayan ve doğru katmana (database.py / ai_service.py) yönlendiren kontrolcü.
MİMARİ ZORUNLULUK: Bu dosyada HİÇBİR SQL veya doğrudan AI API kodu BULUNMAZ.
NOT: Frontend Wix Velo üzerinden sunulduğu için bu backend sadece RESTful API'dir; HTML sayfa rotası yoktur.
"""

from flask import Blueprint, request, jsonify
from app import database
from app.services.ai_service import ai_service, AIServiceError

api_bp = Blueprint('api', __name__, url_prefix='/api')


# ==============================================================================
# RESTFUL API ROTALARI (JSON Endpoints)
# ==============================================================================

@api_bp.route('/sohbet', methods=['POST'])
def sohbet_api():
    """
    POST /api/sohbet
    Kullanıcı mesajını Yapay Zekâ servisine iletir ve yanıtı döndürür.
    Beklenen JSON: {"mesaj": "...", "gecmis": [...]}
    """
    veri = request.get_json(silent=True) or {}
    mesaj = veri.get('mesaj', '')
    gecmis = veri.get('gecmis', [])

    if not mesaj or not str(mesaj).strip():
        return jsonify({
            "basari": False,
            "hata": "Mesaj alanı boş bırakılamaz."
        }), 400

    try:
        yanit = ai_service.yanit_uret(mesaj=mesaj, gecmis=gecmis)
        return jsonify({
            "basari": True,
            "yanit": yanit
        }), 200

    except AIServiceError as e:
        return jsonify({
            "basari": False,
            "hata": f"Yapay zekâ yanıt veremedi: {str(e)}"
        }), 503

    except Exception as e:
        return jsonify({
            "basari": False,
            "hata": f"Sunucu hatası oluştu: {str(e)}"
        }), 500


@api_bp.route('/leads', methods=['POST'])
def lead_ekle_api():
    """
    POST /api/leads
    Yeni müşteri adayı (lead) kaydeder.
    Beklenen JSON: {"isim", "telefon", "eposta", "sehir", "proje_turu", "talep_turu",
                     "malzeme_turu", "miktar" (zorunlu), "firma_adi" (opsiyonel)}
    """
    veri = request.get_json(silent=True) or {}

    zorunlu_alanlar = ['isim', 'telefon', 'eposta', 'sehir', 'proje_turu', 'talep_turu', 'malzeme_turu', 'miktar']
    eksikler = [alan for alan in zorunlu_alanlar if not str(veri.get(alan, '')).strip()]

    if eksikler:
        return jsonify({
            "basari": False,
            "hata": f"Eksik veri: {', '.join(eksikler)} alanları zorunludur."
        }), 400

    try:
        yeni_id = database.lead_ekle(
            isim=veri.get('isim', '').strip(),
            telefon=veri.get('telefon', '').strip(),
            eposta=veri.get('eposta', '').strip(),
            sehir=veri.get('sehir', '').strip(),
            proje_turu=veri.get('proje_turu', '').strip(),
            talep_turu=veri.get('talep_turu', '').strip(),
            malzeme_turu=veri.get('malzeme_turu', '').strip(),
            miktar=veri.get('miktar', '').strip(),
            firma_adi=veri.get('firma_adi', '').strip() if veri.get('firma_adi') else None
        )
        return jsonify({
            "basari": True,
            "mesaj": "Talebiniz başarıyla oluşturuldu.",
            "id": yeni_id,
            "_id": str(yeni_id)  # Wix Velo uyumluluğu için
        }), 201

    except ValueError as e:
        return jsonify({
            "basari": False,
            "hata": str(e)
        }), 400

    except Exception as e:
        return jsonify({
            "basari": False,
            "hata": f"Veritabanı kayıt hatası: {str(e)}"
        }), 500


@api_bp.route('/leads', methods=['GET'])
def lead_listele_api():
    """
    GET /api/leads
    Tüm lead kayıtlarını JSON dizisi olarak döndürür.
    """
    try:
        lead_listesi = database.tum_leadler()
        return jsonify({
            "basari": True,
            "leadler": lead_listesi,
            "toplam": len(lead_listesi)
        }), 200

    except Exception as e:
        return jsonify({
            "basari": False,
            "hata": f"Kayıtlar listelenirken hata oluştu: {str(e)}"
        }), 500
