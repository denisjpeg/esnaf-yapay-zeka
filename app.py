import streamlit as st
import openai
import requests
from streamlit_lottie import st_lottie
import sqlite3

# 1. SAYFA AYARLARI
st.set_page_config(page_title="N-Tech Analytics", page_icon="🏗️", layout="wide")

# ESKİ CHAT_HISTORY.DB DOSYASINI ZORLA SİLME KODU (GEÇİCİ)
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

# VERİTABANI BAĞLANTISI VE TABLO OLUŞTURMA
DB_FILE = "chat_history.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Threads tablosu
    c.execute('''CREATE TABLE IF NOT EXISTS threads 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT)''')
    # Messages tablosu
    c.execute('''CREATE TABLE IF NOT EXISTS messages 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, thread_id INTEGER, role TEXT, content TEXT)''')
    conn.commit()
    conn.close()

def get_all_threads():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, title FROM threads ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def create_new_thread():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO threads (title) VALUES (?)", ("Yeni Sohbet...",))
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id

def update_thread_title(thread_id, new_title):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE threads SET title = ? WHERE id = ?", (new_title, thread_id))
    conn.commit()
    conn.close()

def is_thread_empty(thread_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM messages WHERE thread_id = ?", (thread_id,))
    count = c.fetchone()[0]
    conn.close()
    return count == 0

def load_messages_from_db(thread_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE thread_id = ? ORDER BY id ASC", (thread_id,))
    rows = c.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in rows]

def save_message_to_db(thread_id, role, content):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO messages (thread_id, role, content) VALUES (?, ?, ?)", (thread_id, role, content))
    conn.commit()
    conn.close()

def delete_thread(thread_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM threads WHERE id = ?", (thread_id,))
    c.execute("DELETE FROM messages WHERE thread_id = ?", (thread_id,))
    conn.commit()
    conn.close()

# Veritabanını ilklendir
init_db()

# LOTTIE FONKSİYONLARI
@st.cache_data
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

lottie_lock = load_lottie_url("https://lottie.host/80489953-d083-49fb-8778-dbe3bc04b3cf/7Xb7aT7Eof.json")
lottie_loading = load_lottie_url("https://lottie.host/d1c071d0-b2cc-4592-80ea-379659a85966/MshA8mUHe9.json")

# GİRİŞ KONTROLÜ (ŞİFRE)
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

# AKTİF SOHBET KONTROLÜ
threads = get_all_threads()
if not threads:
    default_id = create_new_thread()
    st.session_state["active_thread_id"] = default_id
    threads = get_all_threads()

if "active_thread_id" not in st.session_state:
    st.session_state["active_thread_id"] = threads[0][0]

# OpenAI API İstemcisi
if "client" not in st.session_state:
    st.session_state.client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ANA PANEL
st.markdown("<h1 style='text-align: center; margin-bottom: 20px;'>🏗️ N-Tech Analytics Kontrol Paneli</h1>", unsafe_allow_html=True)

sidebar_col, chat_col = st.columns([1, 2], gap="large")

with sidebar_col:
    st.markdown("### 💬 Sohbet Odaları")
    
    if st.button("➕ Yeni Sohbet Başlat", use_container_width=True):
        new_id = create_new_thread()
        st.session_state["active_thread_id"] = new_id
        st.rerun()
    
    st.markdown("---")
    
    # Odaların Listelenmesi
    for t_id, t_title in threads:
        is_active = t_id == st.session_state["active_thread_id"]
        button_label = f"💬 {t_title}" if is_active else f"📁 {t_title}"
        
        col_b, col_d = st.columns([4, 1])
        with col_b:
            if st.button(button_label, key=f"thread_{t_id}", use_container_width=True):
                st.session_state["active_thread_id"] = t_id
                st.rerun()
        with col_d:
            if st.button("🗑️", key=f"del_{t_id}"):
                delete_thread(t_id)
                if st.session_state["active_thread_id"] == t_id:
                    remaining = get_all_threads()
                    if remaining:
                        st.session_state["active_thread_id"] = remaining[0][0]
                    else:
                        st.session_state["active_thread_id"] = create_new_thread()
                st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Dosya Yükleme")
    uploaded_file = st.file_uploader("Excel veya Görsel Dosyası Yükleyin", type=["xlsx", "xls", "png", "jpg", "jpeg"])
    if uploaded_file:
        st.success(f"📁 {uploaded_file.name} yüklendi.")

# SAĞ TARAF - DEĞİŞKEN BAŞLIKLI SOHBET EKRANI
with chat_col:
    current_thread_id = st.session_state["active_thread_id"]
    current_messages = load_messages_from_db(current_thread_id)
    
    # Odanın ismini güncel başlığa göre ekrana bas
    active_title = [t[1] for t in threads if t[0] == current_thread_id]
    display_title = active_title[0] if active_title else "Sohbet"
    st.markdown(f"### 📊 Proje Alanı: {display_title}")
    
    for msg in current_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    if user_input := st.chat_input("İşletmeniz hakkında bir soru sorun..."):
        with st.chat_message("user"):
            st.write(user_input)
        
        # Eğer bu odadaki İLK mesajsa, arka planda başlık üretelim
        is_first_msg = is_thread_empty(current_thread_id)
        
        save_message_to_db(current_thread_id, "user", user_input)
        history_for_api = load_messages_from_db(current_thread_id)
        
        # 1. YAPAY ZEKA BAŞLIĞI OLUŞTURMA (Sadece ilk mesajda tetiklenir)
        if is_first_msg:
            try:
                title_response = st.session_state.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Kullanıcının attığı mesajı özetleyen, maksimum 2-3 kelimelik, emojisiz, net ve profesyonel bir Türkçe başlık üret. Sadece başlığı döndür, tırnak işareti kullanma."},
                        {"role": "user", "content": user_input}
                    ],
                    max_tokens=10
                )
                generated_title = title_response.choices[0].message.content.strip()
                update_thread_title(current_thread_id, generated_title)
            except Exception:
                pass # Başlık üretilemezse eski isim kalır, sistem kilitlenmez

        # 2. ANA CEVAP ÜRETME SÜRECİ
        with st.chat_message("assistant"):
            with st.spinner(""):
                if lottie_loading: st_lottie(lottie_loading, height=80, key="loading_chat")
                try:
                    response = st.session_state.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "system", "content": "Sen endüstriyel vinç kiralama ve ağır sanayi lojistiği alanında uzman bir SaaS yapay zeka analistisin. İsmin N-Tech Analytics."}, *history_for_api]
                    )
                    answer = response.choices[0].message.content
                    st.write(answer)
                    
                    save_message_to_db(current_thread_id, "assistant", answer)
                    st.rerun()
                except Exception as e:
                    st.error(f"Bir hata oluştu: {e}")
