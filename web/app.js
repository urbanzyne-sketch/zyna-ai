/**
 * UrbanZyne / ZYNE AI — Statik Site Entegrasyonu
 * index.html ve dashboard.html için ortak API bağlantı katmanı.
 */

const BACKEND_URL = "https://zyna-ai.onrender.com";

let chatHistory = [];

document.addEventListener("DOMContentLoaded", () => {
  initChat();
  initLeadForm();
  initDashboard();
});

/* ---------------- Arayüz 1: Sohbet ---------------- */

function initChat() {
  const btnSor = document.getElementById("btnSor");
  const inputMesaj = document.getElementById("inputMesaj");
  const chatBody = document.getElementById("chatBody");
  const textYanit = document.getElementById("textYanit");
  if (!btnSor || !inputMesaj || !chatBody) return;

  const gonder = async () => {
    const mesaj = inputMesaj.value.trim();
    if (!mesaj) return;

    appendMessage(chatBody, "user", mesaj);
    inputMesaj.value = "";
    inputMesaj.focus();
    btnSor.disabled = true;

    const typingEl = appendMessage(chatBody, "bot typing", "ZYNE AI yazıyor...");

    try {
      const response = await fetch(`${BACKEND_URL}/api/sohbet`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mesaj: mesaj, gecmis: chatHistory.slice(-6) })
      });

      const data = await response.json();
      typingEl.remove();

      if (data.basari) {
        appendMessage(chatBody, "bot", data.yanit);
        chatHistory.push({ role: "user", content: mesaj });
        chatHistory.push({ role: "assistant", content: data.yanit });
      } else {
        appendMessage(chatBody, "bot", "Hata: " + data.hata);
        if (textYanit) {
          textYanit.textContent = "Hata: " + data.hata;
          textYanit.className = "status-msg err";
          textYanit.style.display = "block";
        }
      }
    } catch (err) {
      typingEl.remove();
      appendMessage(chatBody, "bot", "Sunucu bağlantı hatası oluştu.");
    } finally {
      btnSor.disabled = false;
    }
  };

  btnSor.addEventListener("click", gonder);
  inputMesaj.addEventListener("keydown", (e) => {
    if (e.key === "Enter") gonder();
  });
}

function appendMessage(chatBody, cls, text) {
  const el = document.createElement("div");
  el.className = "msg " + cls;
  el.textContent = text;
  chatBody.appendChild(el);
  chatBody.scrollTop = chatBody.scrollHeight;
  return el;
}

/* ---------------- Arayüz 1: Lead Formu ---------------- */

function initLeadForm() {
  const btnKaydet = document.getElementById("btnKaydet");
  const textDurum = document.getElementById("textDurum");
  if (!btnKaydet || document.getElementById("repeaterLeads")) return; // dashboard sayfasında çalışmasın

  btnKaydet.addEventListener("click", async () => {
    const isim = val("inputIsim");
    const telefon = val("inputTelefon");
    const eposta = val("inputEposta");
    const firma_adi = val("inputFirma");
    const sehir = val("inputSehir");
    const proje_turu = val("dropdownProjeTuru");
    const talep_turu = val("dropdownTalepTuru");
    const malzeme_turu = val("dropdownMalzemeTuru");
    const miktar = val("inputMiktar");

    if (!isim || !telefon || !eposta || !sehir || !proje_turu || !talep_turu || !malzeme_turu || !miktar) {
      setDurum(textDurum, "Lütfen zorunlu (*) alanları doldurunuz.", "err");
      return;
    }

    btnKaydet.disabled = true;
    setDurum(textDurum, "Gönderiliyor...", "");

    try {
      const response = await fetch(`${BACKEND_URL}/api/leads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ isim, telefon, eposta, firma_adi, sehir, proje_turu, talep_turu, malzeme_turu, miktar })
      });

      const data = await response.json();
      if (data.basari) {
        setDurum(textDurum, "Talebiniz başarıyla iletildi!", "ok");
        ["inputIsim", "inputTelefon", "inputEposta", "inputFirma", "inputSehir", "inputMiktar"].forEach((id) => {
          document.getElementById(id).value = "";
        });
        ["dropdownProjeTuru", "dropdownTalepTuru", "dropdownMalzemeTuru"].forEach((id) => {
          document.getElementById(id).selectedIndex = 0;
        });
      } else {
        setDurum(textDurum, "Hata: " + data.hata, "err");
      }
    } catch (err) {
      setDurum(textDurum, "Sunucuya bağlanılamadı.", "err");
    } finally {
      btnKaydet.disabled = false;
    }
  });
}

function val(id) {
  const el = document.getElementById(id);
  return el ? el.value.trim() : "";
}

function setDurum(el, text, cls) {
  if (!el) return;
  el.textContent = text;
  el.className = "status-msg" + (cls ? " " + cls : "");
}

/* ---------------- Arayüz 2: Yönetim Paneli ---------------- */

function initDashboard() {
  const tbody = document.getElementById("repeaterLeads");
  if (!tbody) return;

  const btnYenile = document.getElementById("btnYenile");
  if (btnYenile) btnYenile.addEventListener("click", yukleLeadler);

  yukleLeadler();
}

async function yukleLeadler() {
  const tbody = document.getElementById("repeaterLeads");
  const stateBox = document.getElementById("stateBox");
  if (!tbody) return;

  tbody.innerHTML = "";
  stateBox.innerHTML = `<div class="loading-state"><div class="spin"></div>Kayıtlar yükleniyor...</div>`;

  try {
    const response = await fetch(`${BACKEND_URL}/api/leads`);
    const data = await response.json();

    if (!data.basari) {
      stateBox.innerHTML = `<div class="empty-state">Kayıtlar alınamadı: ${data.hata || "bilinmeyen hata"}</div>`;
      return;
    }

    const leadler = data.leadler || [];
    doldurIstatistikler(leadler, data.toplam);

    if (leadler.length === 0) {
      stateBox.innerHTML = `<div class="empty-state">Henüz kayıtlı talep yok.</div>`;
      return;
    }

    stateBox.innerHTML = "";
    leadler.forEach((lead) => {
      tbody.appendChild(leadSatiri(lead));
    });
  } catch (err) {
    stateBox.innerHTML = `<div class="empty-state">Sunucuya bağlanılamadı.</div>`;
  }
}

function leadSatiri(lead) {
  const tr = document.createElement("tr");
  tr.innerHTML = `
    <td>${escapeHtml(lead.isim)}</td>
    <td class="cell-dim">${escapeHtml(lead.telefon)}</td>
    <td class="cell-dim">${escapeHtml(lead.eposta || "-")}</td>
    <td class="cell-dim">${escapeHtml(lead.firma_adi || "-")}</td>
    <td class="cell-dim">${escapeHtml(lead.sehir || "-")}</td>
    <td><span class="badge">${escapeHtml(lead.proje_turu || "-")}</span></td>
    <td class="cell-dim">${escapeHtml(lead.talep_turu || "-")}</td>
    <td class="cell-dim">${escapeHtml(lead.malzeme_turu || "-")}</td>
    <td class="cell-dim">${escapeHtml(lead.miktar || "-")}</td>
    <td class="cell-faint">${formatTarih(lead.tarih)}</td>
  `;
  return tr;
}

function doldurIstatistikler(leadler, toplam) {
  const statToplam = document.getElementById("statToplam");
  const statBugun = document.getElementById("statBugun");
  const statHafta = document.getElementById("statHafta");
  const statSehir = document.getElementById("statSehir");

  const now = new Date();
  const bugunBasi = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const haftaBasi = new Date(bugunBasi);
  haftaBasi.setDate(haftaBasi.getDate() - 7);

  let bugunSayisi = 0;
  let haftaSayisi = 0;
  const sehirSeti = new Set();

  leadler.forEach((lead) => {
    const tarih = lead.tarih ? new Date(lead.tarih.replace(" ", "T")) : null;
    if (tarih && !isNaN(tarih)) {
      if (tarih >= bugunBasi) bugunSayisi++;
      if (tarih >= haftaBasi) haftaSayisi++;
    }
    if (lead.sehir) sehirSeti.add(lead.sehir.trim().toLowerCase());
  });

  if (statToplam) statToplam.textContent = (toplam ?? leadler.length).toString();
  if (statBugun) statBugun.textContent = bugunSayisi.toString();
  if (statHafta) statHafta.textContent = haftaSayisi.toString();
  if (statSehir) statSehir.textContent = sehirSeti.size.toString();
}

function formatTarih(tarih) {
  if (!tarih) return "-";
  const d = new Date(tarih.replace(" ", "T"));
  if (isNaN(d)) return escapeHtml(tarih);
  return d.toLocaleDateString("tr-TR", { day: "2-digit", month: "2-digit", year: "numeric" }) +
    " " + d.toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" });
}

function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
