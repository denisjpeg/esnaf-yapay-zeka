import streamlit as st
import openai
import requests
from streamlit_lottie import st_lottie
import sqlite3
import os

# 1. SAYFA AYARLARI
st.set_page_config(page_title="N-Tech Analytics", page_icon="🏗️", layout="wide")

# VERİTABANI BAĞLANTISI VE TABLO OLUŞTURMA
DB_FILE = "chat_history.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Mesajları rol (user/assistant) ve içerik olarak saklayan tablo
    c.execute('''CREATE TABLE IF NOT EXISTS messages 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, content TEXT)''')
    conn.commit()
    conn.close()

def load_messages_from_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in rows]

def save_message_to_db(role, content):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO messages (role, content) VALUES (?, ?)", (role, content))
    conn.commit()
    conn.close()

def clear_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM messages")
    conn.commit()
    conn.close()

# Veritabanını tetikle
init_db()

# LOTTIE FONKSİYONU
@st.cache_data
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

lottie_lock = load_lottie_url("https://lottie.host/80489953-d083-49fb-8778-dbe3bc04b3cf/7Xb7aT7Eof.json")
lottie_loading = load_lottie_url("https://lottie.host/d1c071d0-b2cc-4592-80ea-379659a85966/MshA8mUHe9.json")

# HAFİF CSS
st.markdown("""
    <style>
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
    </style>
""", unsafe_allow_html=True)

# GİRİŞ KONTROLÜ
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def check_password():
    if st.session_state["authenticated"]:
        return True
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if lottie_lock: st_lottie(lottie_lock, height=200, key="lock")
        st.markdown("<h2 style='text-align: center;'>N-Tech Analytics</h2>", unsafe_allow_html=True)
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

# DEPOLAMA ALANLARINI BAŞLATMA (Veritabanından yükle)
if "messages" not in st.session_state:
    st.session_state.messages = load_messages_from_db()

if "client" not in st.session_state:
    st.session_state.client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ANA PANEL
st.markdown("<h1 style='text-align: center; margin-bottom: 20px;'>🏗️ N-Tech Analytics Kontrol Paneli</h1>", unsafe_allow_html=True)

sidebar_col, chat_col = st.columns([1, 2], gap="large")

with sidebar_col:
    st.markdown("### 📊 Veri ve Dosya Yükleme")
    uploaded_file = st.file_uploader("Excel veya Görsel Dosyası Yükleyin", type=["xlsx", "xls", "png", "jpg", "jpeg"])
    if uploaded_file:
        st.success(f"📁 {uploaded_file.name} başarıyla sisteme yüklendi.")
    
    st.markdown("---")
    st.markdown("### ⚡ Hızlı Analiz Butonları")
    
    if st.button("📈 Aylık Ciro Analizi Yap", use_container_width=True):
        save_message_to_db("user", "Aylık ciro analizi yap.")
        st.session_state.messages = load_messages_from_db()
        st.rerun()
            
    if st.button("🚛 Araç Doluluk / Lojistik Raporu", use_container_width=True):
        save_message_to_db("user", "Araç doluluk ve lojistik raporunu çıkar.")
        st.session_state.messages = load_messages_from_db()
        st.rerun()
        
    st.markdown("---")
    if st.button("🗑️ Sohbet Geçmişini Temizle", use_container_width=True):
        clear_db()
        st.session_state.messages = []
        st.success("Sohbet geçmişi silindi!")
        st.rerun()

with chat_col:
    st.markdown("### 💬 Yapay Zeka Danışmanı")
    
    # Geçmiş mesajları ekrana bas
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    if user_input := st.chat_input("İşletmeniz hakkında bir soru sorun..."):
        with st.chat_message("user"):
            st.write(user_input)
        
        # Kullanıcı mesajını veritabanına kaydet
        save_message_to_db("user", user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("assistant"):
            with st.spinner(""):
                if lottie_loading: st_lottie(lottie_loading, height=80, key="loading")
                try:
                    response = st.session_state.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "system", "content": "Sen endüstriyel vinç kiralama ve ağır sanayi lojistiği alanında uzman bir SaaS yapay zeka analistisin. İsmin N-Tech Analytics. Profesyonel, kibar ve net cevaplar ver."}, *st.session_state.messages]
                    )
                    answer = response.choices[0].message.content
                    st.write(answer)
                    
                    # Asistan yanıtını veritabanına kaydet
                    save_message_to_db("assistant", answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Bir hata oluştu: {e}")
