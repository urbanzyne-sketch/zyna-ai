/**
 * UrbanZyne / ZYNE AI — Wix Velo Frontend Entegrasyon Kodu
 * =========================================================
 * Bu kod Wix Velo ortamında çalışır ve Wix sitenizdeki arayüz bileşenlerini
 * Render / Python Flask backend API'nize bağlar.
 */

import { fetch } from 'wix-fetch';

// Render üzerindeki canlı API adresi:
const BACKEND_URL = "https://zyna-ai.onrender.com";

// Sohbet geçmişi (ZYNE AI'ya bağlam sağlamak için)
let chatHistory = [];

$w.onReady(function () {
    console.log("UrbanZyne / ZYNE AI Wix Velo Entegrasyonu Hazır.");

    // 1. Karşılama Sayfası: "Sor" Buton Tıklaması
    $w("#btnSor").onClick(async () => {
        const mesaj = $w("#inputMesaj").value;
        if (!mesaj) return;

        $w("#textYanit").text = "ZYNE AI yanıt hazırlıyor...";

        try {
            const response = await fetch(`${BACKEND_URL}/api/sohbet`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mesaj: mesaj, gecmis: chatHistory.slice(-6) })
            });

            const data = await response.json();
            if (data.basari) {
                $w("#textYanit").text = data.yanit;
                chatHistory.push({ role: 'user', content: mesaj });
                chatHistory.push({ role: 'assistant', content: data.yanit });
            } else {
                $w("#textYanit").text = "Hata: " + data.hata;
            }
        } catch (err) {
            $w("#textYanit").text = "Sunucu bağlantı hatası oluştu.";
        }
    });

    // 2. Karşılama Sayfası: "Talebi Gönder" Buton Tıklaması (Lead Kaydı)
    $w("#btnKaydet").onClick(async () => {
        const isim = $w("#inputIsim").value;
        const telefon = $w("#inputTelefon").value;
        const eposta = $w("#inputEposta").value;
        const firma_adi = $w("#inputFirma").value;
        const sehir = $w("#inputSehir").value;
        const proje_turu = $w("#dropdownProjeTuru").value;
        const talep_turu = $w("#dropdownTalepTuru").value;
        const malzeme_turu = $w("#dropdownMalzemeTuru").value;
        const miktar = $w("#inputMiktar").value;

        if (!isim || !telefon || !eposta || !sehir || !proje_turu || !talep_turu || !malzeme_turu || !miktar) {
            $w("#textDurum").text = "Lütfen zorunlu (*) alanları doldurunuz.";
            return;
        }

        try {
            const response = await fetch(`${BACKEND_URL}/api/leads`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ isim, telefon, eposta, firma_adi, sehir, proje_turu, talep_turu, malzeme_turu, miktar })
            });

            const data = await response.json();
            if (data.basari) {
                $w("#textDurum").text = "Talebiniz başarıyla iletildi!";
                $w("#inputIsim").value = "";
                $w("#inputTelefon").value = "";
                $w("#inputEposta").value = "";
            } else {
                $w("#textDurum").text = "Hata: " + data.hata;
            }
        } catch (err) {
            $w("#textDurum").text = "Sunucuya bağlanılamadı.";
        }
    });

    // 3. Yönetim Paneli: Repeater Bileşenini Lead Verisi ile Doldurma
    if ($w("#repeaterLeads").length > 0) {
        yükleLeadler();
    }
});

async function yükleLeadler() {
    try {
        const response = await fetch(`${BACKEND_URL}/api/leads`);
        const data = await response.json();

        if (data.basari) {
            // Wix Repeater her nesnede zorunlu _id alanına ihtiyaç duyar
            $w("#repeaterLeads").data = data.leadler;

            $w("#repeaterLeads").onItemReady(($item, itemData) => {
                $item("#textIsim").text = itemData.isim;
                $item("#textTelefon").text = itemData.telefon;
                $item("#textEposta").text = itemData.eposta || "-";
                $item("#textFirma").text = itemData.firma_adi || "-";
                $item("#textSehir").text = itemData.sehir || "-";
                $item("#textProjeTuru").text = itemData.proje_turu || "-";
                $item("#textTalepTuru").text = itemData.talep_turu || "-";
                $item("#textMalzemeTuru").text = itemData.malzeme_turu || "-";
                $item("#textMiktar").text = itemData.miktar || "-";
                $item("#textTarih").text = itemData.tarih;
            });
        }
    } catch (err) {
        console.error("Repeater yükleme hatası:", err);
    }
}
