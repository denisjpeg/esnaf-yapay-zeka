import streamlit as st
import openai
import pandas as pd
import base64
import requests
from streamlit_lottie import st_lottie

# 1. SAYFA AYARLARI (Geniş Ekran Modu)
st.set_page_config(page_title="N-Tech Analytics", page_icon="🏗️", layout="wide")

# LOTTIE ANİMASYONLARINI İNTERNETTEN ÇEKEN YARDIMCI FONKSİYON
@st.cache_data
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Premium Lottie Animasyon Linkleri
lottie_lock = load_lottie_url("https://lottie.host/80489953-d083-49fb-8778-dbe3bc04b3cf/7Xb7aT7Eof.json")
lottie_loading = load_lottie_url("https://lottie.host/d1c071d0-b2cc-4592-80ea-379659a85966/MshA8mUHe9.json")

# 2. ULTRA DETAYLI AÇIK TEMA CSS (Siyah Kutuları Beyaz Yapan Kesin Çözüm)
st.markdown("""
    <style>
    /* Ana Arka Planı Bembeyaz Yap ve Yazıları Koyu Füme Yap */
    .stApp {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
    }
    
    /* Üst Menü ve Sidebar Alanlarını Düzenle */
    header, [data-testid="stHeader"] {
        background-color: #F8FAFC !important;
    }
    
    /* Sohbet Mesaj Alanları ve Kutuları */
    [data-testid="stChatMessage"] {
        background-color: #F1F5F9 !important;
        border-radius: 15px !important;
        padding: 15px !important;
        margin-bottom: 10px !important;
        color: #1E293B !important;
    }
    
    /* Kullanıcı Mesajı Ayrımı */
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #E2E8F0 !important;
    }
    
    /* Başlıklar ve Yazı Etiketleri */
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #0F172A !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Input Kutuları ve Şifre Alanı */
    .stTextInput input {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 10px !important;
    }
    
    /* Hızlı Analiz Butonları Tasarımı */
    .stButton>button {
        background-color: #2563EB !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 10px 20px !important;
        font-weight: bold !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1D4ED8 !important;
        transform: scale(1.02);
    }
    
    /* --- SİYAH KALAN CHAT INPUT KUTUSUNU TAMAMEN BEYAZ YAPMA --- */
    [data-testid="stChatInput"] {
        background-color: #F8FAFC !important;
        border: 2px solid #CBD5E1 !important;
        border-radius: 20px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }
    
    /* Chat Input İçindeki Metin Alanını ve Yazılan Siyah Yazıyı Zorlama */
    [data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: #0F172A !important;
        font-size: 16px !important;
    }
    
    /* --- SİYAH KALAN DOSYA YÜKLEME (FILE UPLOADER) KUTUSUNU BEYAZ YAPMA --- */
    [data-testid="stFileUploader"] section {
        background-color: #F8FAFC !important;
        border: 2px dashed #CBD5E1 !important;
        border-radius: 15px !important;
        color: #0F172A !important;
    }
    
    /* Dosya yükleme kutusunun içindeki küçük yazılar */
    [data-testid="stFileUploader"] section div, [data-testid="stFileUploader"] p {
        color: #475569 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. GİRİŞ KONTROLÜ (ŞİFRE KORUMASI)
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def check_password():
    if st.session_state["authenticated"]:
        return True

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if lottie_lock:
            st_lottie(lottie_lock, height=200, key="lock")
        st.markdown("<h2 style='text-align: center;'>N-Tech Analytics</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Güvenli giriş için lütfen şifrenizi giriniz.</p>", unsafe_allow_html=True)
        
        password = st.text_input("Şifre", type="password", label_visibility="collapsed")
        if st.button("Sistem Girişi", use_container_width=True):
            if password == st.secrets["APP_PASSWORD"]:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("❌ Hatalı şifre girdiniz!")
    return False

if not check_password():
    st.stop()

# 4. DEPOLAMA ALANLARINI BAŞLATMA (SESSION STATE)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "client" not in st.session_state:
    st.session_state.client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 5. ANA PANEL VE ARAYÜZ
st.markdown("<h1 style='text-align: center; margin-bottom: 20px;'>🏗️ N-Tech Analytics Kontrol Paneli</h1>", unsafe_allow_html=True)

# SAĞLI SOLLU DÜZEN
sidebar_col, chat_col = st.columns([1, 2], gap="large")

with sidebar_col:
    st.markdown("### 📊 Veri ve Dosya Yükleme")
    uploaded_file = st.file_uploader("Excel veya Görsel Dosyası Yükleyin", type=["xlsx", "xls", "png", "jpg", "jpeg"])
    
    if uploaded_file:
        st.success(f"📁 {uploaded_file.name} başarıyla sisteme yüklendi.")
    
    st.markdown("---")
    st.markdown("### ⚡ Hızlı Analiz Butonları")
    
    if st.button("📈 Aylık Ciro Analizi Yap", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Aylık ciro analizi yap."})
        st.rerun()
            
    if st.button("🚛 Araç Doluluk / Lojistik Raporu", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Araç doluluk ve lojistik raporunu çıkar."})
        st.rerun()

with chat_col:
    st.markdown("### 💬 Yapay Zeka Danışmanı")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    if user_input := st.chat_input("İşletmeniz hakkında bir soru sorun veya analiz isteyin..."):
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("assistant"):
            with st.spinner(""):
                if lottie_loading:
                    st_lottie(lottie_loading, height=80, key="loading")
                try:
                    response = st.session_state.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "system", "content": "Sen endüstriyel vinç kiralama ve ağır sanayi lojistiği alanında uzman bir SaaS yapay zeka analistisin. İsmin N-Tech Analytics. Profesyonel, kibar ve net cevaplar ver."}, *st.session_state.messages]
                    )
                    answer = response.choices[0].message.content
                    st.write(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Bir hata oluştu: {e}")
                    
