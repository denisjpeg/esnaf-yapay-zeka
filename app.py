import streamlit as st
import openai
import pandas as pd
import base64

# 1. SAYFA AYARLARI (Geniş Ekran Modu)
st.set_page_config(page_title="Deniz GPT 2.1", page_icon="🏗️", layout="wide")

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

    /* KULLANICI MESAJLARINI SAĞA YASLAMA (WhatsApp Tarzı) */
    .stChatMessage[data-testid="stChatMessageUser"] {
        flex-direction: row-reverse !important; /* İkon ve metni ters çevirip sağa atar */
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
        margin: 100px auto;
        padding: 40px;
        background-color: rgba(28, 107, 106, 0.05);
        border-radius: 15px;
        border: 1px solid rgba(184, 242, 230, 0.1);
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
    
    /* Alt Kısımdaki Giriş Alanına Biraz Boşluk Bırakalım */
    .block-container {
        padding-bottom: 150px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. ŞİFRE KONTROLÜ (GÜVENLİK DUVARI)
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if not st.session_state.password_correct:
        _, col_mid, _ = st.columns([1, 2, 1])
        with col_mid:
            st.markdown('<div class="password-container">', unsafe_allow_html=True)
            st.markdown("### 🏗️ Deniz GPT | Güvenli Giriş")
            password = st.text_input("Analiz paneli şifresini girin:", type="password")
            if st.button("Giriş Yap", use_container_width=True):
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

    # Üst Bölüm Sabit Alanı (Başlıklar ve Butonlar)
    _, header_col, _ = st.columns([1, 4, 1])
    with header_col:
        st.markdown("<h1>🏗️ Deniz GPT 2.1</h1>", unsafe_allow_html=True)
        st.write("<p style='text-align: center;'>Analiz paneline hoş geldiniz. Dosyalarınızı yükleyip hızlı butonlarla veya yazarak analiz yapabilirsiniz.</p>", unsafe_allow_html=True)

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
    # Sütun yapısının tamamen dışına aldık, böylece sayfanın tabanına kalıcı olarak yapışacak.
    chat_data = st.chat_input("Mesajınızı yazın veya dosyanızı ekleyin...", accept_file=True, file_type=["xlsx", "xls", "png", "jpg", "jpeg"])

    if chat_data or st.session_state.pending_query:
        user_text = st.session_state.pending_query if st.session_state.pending_query else chat_data["text"]
        uploaded_files = chat_data["files"] if chat_data else []
        st.session_state.pending_query = None

        # Mesajı hafızaya ekle
        st.session_state.messages.append({"role": "user", "content": user_text if user_text else "Dosya yüklendi."})

        # İşlem paketini hazırla
        content_list = []
        if user_text:
            content_list.append({"type": "text", "text": user_text})

        # Dosya önizlemelerini yine orta sütunda şıkça göstermek için ara değişken
        for file in uploaded_files:
            if file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)
                # Tabloyu orta sütunda göstermek için header_col'a yönlendiriyoruz
                with header_col:
                    st.write(f"📁 **Yüklenen Dosya:** {file.name}")
                    st.dataframe(df.head(), use_container_width=True)
                content_list.append({"type": "text", "text": f"Dosya Adı: {file.name}\nİçerik:\n{df.to_markdown(index=False)}"})
            elif file.name.endswith(('.png', '.jpg', '.jpeg')):
                img_str = base64.b64encode(file.getvalue()).decode("utf-8")
                content_list.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}})

        # Yapay Zeka Cevap Süreci
        try:
            system_prompt = (
                "Sen Deniz GPT'nin profesyonel iş analistisin. Verileri titizlikle analiz et. "
                "Üslubun kibar, net ve profesyonel olsun. Teknik terimleri esnafın anlayacağı şekilde açıkla."
            )
            
            api_messages = [{"role": "system", "content": system_prompt}]
            for m in st.session_state.messages[:-1]:
                api_messages.append({"role": m["role"], "content": m["content"]})
            api_messages.append({"role": "user", "content": content_list})

            response = client.chat.completions.create(model="gpt-4o", messages=api_messages)
            ai_reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            
            # Sayfayı tetikleyerek yeni mesajların anında sağlı sollu yerleşmesini sağla
            st.rerun()
        except Exception as e:
            with header_col:
                st.error(f"Bir hata oluştu: {str(e)}")