import streamlit as st
import openai
import pandas as pd
import base64
import requests
from streamlit_lottie import st_lottie  # Yeni eklediğimiz premium animasyon kütüphanesi

# 1. SAYFA AYARLARI (Geniş Ekran Modu)
st.set_page_config(page_title="N-Tech Analytics", page_icon="🏗️", layout="wide")

# LOTTIE ANİMASYONLARINI İNTERNETTEN ÇEKEN YARDIMCI FONKSİYON
@st.cache_data
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Premium Lottie Animasyon Linkleri (Teal / Cyber Mavi Tonlarında)
lottie_lock = load_lottie_url("https://lottie.host/80489953-d083-49fb-8778-dbe3bc04b3cf/7Xb7aT7Eof.json") # Giriş için siber kilit
lottie_loading = load_lottie_url("https://lottie.host/d1c071d0-b2cc-4592-80ea-379659a85966/MshA8mUHe9.json") # Analiz için veri küpü

# 2. SAĞLI SOLLU SOHBET VE SABİT INPUT İÇİN GELİŞMİŞ CSS
st.markdown("""
    <style>
    /* Ana Arka Plan */
    .stApp {
        background-color: #071014;
        color: #e2e8f0;
    }
    
    /* Başlıklar */
    h1, h2, h3 {
        color: #B8F2E6 !important;
        font-family: 'Poppins', sans-serif;
        text-align: center;
    }

    /* KUTULARI SIFIRLAMA & GENEL CHAT AYARI */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
        padding: 10px 0px !important;
        margin-bottom: 5px !important;
        display: flex !important;
        width: 100% !important;
    }

    /* KULLANICI MESAJLARINI SAĞA YASLAMA */
    .stChatMessage[data-testid="stChatMessageUser"] {
        flex-direction: row-reverse !important;
        text-align: right !important;
    }

    /* Kullanıcı Mesaj Metninin Arkasını Hafifçe Belirgin Yapma */
    .stChatMessage[data-testid="stChatMessageUser"] .stMarkdown {
        background-color: rgba(28, 107, 106, 0.15) !important;
        padding: 10px 15px !important;
        border-radius: 15px 15px 0px 15px !important;
        display: inline-block !important;
    }

    /* ASİSTAN MESAJLARINI SOLDA TUTMA VE YUMUŞATMA */
    .stChatMessage[data-testid="stChatMessageAssistant"] .stMarkdown {
        background-color: rgba(255, 255, 255, 0.02) !important;
        padding: 10px 15px !important;
        border-radius: 15px 15px 15px 0px !important;
        display: inline-block !important;
    }

    /* Soft Geçiş Çizgisi */
    .stChatMessage {
        border-bottom: 1px solid rgba(184, 242, 230, 0.03) !important;
    }

    /* Giriş Şifresi Kutusu Tasarımı */
    .password-container {
        max-width: 400px;
        margin: 30px auto;
        padding: 40px;
        background-color: rgba(28, 107, 106, 0.03);
        border-radius: 15px;
        border: 1px solid rgba(184, 242, 230, 0.08);
    }

    /* Premium Butonlar */
    .stButton>button {
        background-color: rgba(28, 107, 106, 0.2);
        color: #B8F2E6;
        border: 1px solid #1c6b6a;
        border-radius: 20px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #1c6b6a;
        color: white;
        border-color: #B8F2E6;
    }
    
    .block-container {
        padding-bottom: 150px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. ŞİFRE KONTROLÜ (GÜVENLİK DUVARI + GİRİŞ ANİMASYONU)
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if not st.session_state.password_correct:
        _, col_mid, _ = st.columns([1, 2, 1])
        with col_mid:
            # Giriş ekranının üstüne premium siber güvenlik animasyonunu yerleştiriyoruz
            if lottie_lock:
                st_lottie(lottie_lock, height=200, key="lock_animation")
                
            st.markdown('<div class="password-container">', unsafe_allow_html=True)
            st.markdown("### 🏗️ N-Tech Analytics")
            password = st.text_input("Analiz paneli şifresini girin:", type="password")
            if st.button("Sistem Girişi", use_container_width=True):
                if password == st.secrets["APP_PASSWORD"]:
                    st.session_state.password_correct = True
                    st.rerun()
                else:
                    st.error("❌ Hatalı şifre!")
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

if check_password():
    # 4. API İSTEMCİSİ
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    # 5. SOHBET HAFIZASI
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending_query" not in st.session_state:
        st.session_state.pending_query = None

    # Sol taraftaki gizlenebilir Çekmece Menüsü
    with st.sidebar:
        st.markdown("### ⚙️ Yönetim Paneli")
        st.write("Uygulama ayarlarını buradan değiştirebilirsiniz.")
        if st.button("🗑️ Sohbeti Sıfırla", use_container_width=True):
            st.session_state.messages = []
            st.session_state.password_correct = False
            st.rerun()

    # Ana Sayfa Düzeni
    _, header_col, _ = st.columns([1, 4, 1])
    with header_col:
        st.markdown("<h1>🏗️ N-Tech Analytics 2.1</h1>", unsafe_allow_html=True)
        st.write("<p style='text-align: center;'>Gelecek Nesil Endüstriyel Veri Analiz Platformu.</p>", unsafe_allow_html=True)

        # HIZLI ANALİZ SORU BUTONLARI
        st.write("🔍 **Hızlı Analiz Soruları:**")
        b_col1, b_col2, b_col3 = st.columns(3)
        
        quick_questions = [
            "📊 Bu ayın toplam hakediş dökümünü çıkar.",
            "🛢️ Giderleri (Yakıt, Bakım, Personel) analiz et.",
            "📍 En karlı çalıştığımız bölgeleri listele."
        ]

        with b_col1:
            if st.button("💰 Hakediş Özeti", use_container_width=True):
                st.session_state.pending_query = quick_questions[0]
        with b_col2:
            if st.button("📉 Gider Analizi", use_container_width=True):
                st.session_state.pending_query = quick_questions[1]
        with b_col3:
            if st.button("🌍 Bölge Analizi", use_container_width=True):
                st.session_state.pending_query = quick_questions[2]

        st.markdown("<br>", unsafe_allow_html=True)

        # SOHBET AKIŞINI GÖSTERME (Sağlı Söllü Düzen)
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    # 6. EN ALTA SABİTLENMİŞ INPUT ALANI
    chat_data = st.chat_input("Mesajınızı yazın veya dosyanızı ekleyin...", accept_file=True, file_type=["xlsx", "xls", "png", "jpg", "jpeg"])

    if chat_data or st.session_state.pending_query:
        user_text = st.session_state.pending_query if st.session_state.pending_query else chat_data["text"]
        uploaded_files = chat_data["files"] if chat_data else []
        st.session_state.pending_query = None

        # Mesajı hafızaya ekle
        st.session_state.messages.append({"role": "user", "content": user_text if user_text else "Dosya yüklendi."})

        content_list = []
        if user_text:
            content_list.append({"type": "text", "text": user_text})

        for file in uploaded_files:
            if file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)
                with header_col:
                    st.write(f"📁 **Yüklenen Dosya:** {file.name}")
                    st.dataframe(df.head(), use_container_width=True)
                content_list.append({"type": "text", "text": f"Dosya Adı: {file.name}\nİçerik:\n{df.to_markdown(index=False)}"})
            elif file.name.endswith(('.png', '.jpg', '.jpeg')):
                img_str = base64.b64encode(file.getvalue()).decode("utf-8")
                content_list.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}})

        # PREMİUM ANİMASYONLU CEVAP SÜRECİ
        try:
            system_prompt = (
                "Sen N-Tech Analytics'in profesyonel iş analistisin. Verileri titizlikle analiz et. "
                "Üslubun kibar, net ve profesyonel olsun. Teknik terimleri esnafın anlayacağı şekilde açıkla."
            )
            
            api_messages = [{"role": "system", "content": system_prompt}]
            for m in st.session_state.messages[:-1]:
                api_messages.append({"role": m["role"], "content": m["content"]})
            api_messages.append({"role": "user", "content": content_list})

            # Yapay zeka düşünürken o eski statik yazı yerine dönen neon küp animasyonunu tetikliyoruz
            with header_col:
                with st.spinner(""):
                    if lottie_loading:
                        st_lottie(lottie_loading, height=120, key="loading_animation")

                    response = client.chat.completions.create(model="gpt-4o", messages=api_messages)
                    ai_reply = response.choices[0].message.content
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            
            st.rerun()
        except Exception as e:
            with header_col:
                st.error(f"Bir hata oluştu: {str(e)}")
