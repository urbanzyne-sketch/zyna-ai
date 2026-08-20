"""
Modül B: Veritabanı (app/database.py)
-------------------------------------
SQLite ile çalışan, müşteri adaylarını (lead) kaydeden ve listeleyen veri katmanı.
GÜVENLİK: SQL Injection'a karşı tüm sorgularda ? yer tutucuları kullanılmıştır.
"""

import sqlite3
import os
from flask import current_app


def get_db():
    """
    Veritabanına bağlanır ve sütun adlarıyla erişim sağlayan row_factory ayarlar.
    """
    db_path = current_app.config.get('DATABASE_URL', 'smartlead.db')
    
    # Göreli yol kullanılıyorsa uygulama kök dizinine bağla
    if not os.path.isabs(db_path):
        db_path = os.path.join(current_app.root_path, '..', db_path)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Satırlara sözlük gibi erişim sağlar (row['isim'])
    return conn


def init_db(app=None):
    """
    Veritabanı tablosunu (leads) oluşturur.
    """
    if app:
        with app.app_context():
            _create_tables()
    else:
        _create_tables()


def _create_tables():
    """Tablo oluşturma yardımcı fonksiyonu"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT NOT NULL,
            telefon TEXT NOT NULL,
            eposta TEXT NOT NULL,
            firma_adi TEXT,
            sehir TEXT NOT NULL,
            proje_turu TEXT NOT NULL,
            talep_turu TEXT NOT NULL,
            malzeme_turu TEXT NOT NULL,
            miktar TEXT NOT NULL,
            tarih DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


def lead_ekle(isim, telefon, eposta, sehir, proje_turu, talep_turu, malzeme_turu, miktar, firma_adi=None):
    """
    Yeni bir müşteri adayı (lead) ekler.
    GÜVENLİK ZORUNLULUĞU: Değerler doğrudan SQL metnine eklenmez, ? yer tutucusu kullanılır.
    """
    zorunlu_alanlar = {
        "isim": isim, "telefon": telefon, "eposta": eposta, "sehir": sehir,
        "proje_turu": proje_turu, "talep_turu": talep_turu,
        "malzeme_turu": malzeme_turu, "miktar": miktar
    }
    eksikler = [ad for ad, deger in zorunlu_alanlar.items() if not deger or not str(deger).strip()]
    if eksikler:
        raise ValueError(f"Zorunlu alanlar eksik: {', '.join(eksikler)}")

    conn = get_db()
    cursor = conn.cursor()

    # SQL Injection koruması: ? parametreleri kullanımı
    cursor.execute('''
        INSERT INTO leads (isim, telefon, eposta, firma_adi, sehir, proje_turu, talep_turu, malzeme_turu, miktar)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        isim.strip(), telefon.strip(), eposta.strip(),
        firma_adi.strip() if firma_adi else None,
        sehir.strip(), proje_turu.strip(), talep_turu.strip(),
        malzeme_turu.strip(), miktar.strip()
    ))

    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return new_id


def tum_leadler():
    """
    Tüm kayıtları en yeniden eskiye sıralı olarak getirir ve liste (dict) olarak döndürür.
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, isim, telefon, eposta, firma_adi, sehir, proje_turu, talep_turu, malzeme_turu, miktar, tarih
        FROM leads
        ORDER BY tarih DESC
    ''')

    rows = cursor.fetchall()
    conn.close()

    # sqlite3.Row nesnelerini standart Python dict yapılarına dönüştür
    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "_id": str(row["id"]),  # Wix Velo uyumluluğu için _id alanı
            "isim": row["isim"],
            "telefon": row["telefon"],
            "eposta": row["eposta"],
            "firma_adi": row["firma_adi"] or "",
            "sehir": row["sehir"],
            "proje_turu": row["proje_turu"],
            "talep_turu": row["talep_turu"],
            "malzeme_turu": row["malzeme_turu"],
            "miktar": row["miktar"],
            "tarih": row["tarih"]
        })

    return result
