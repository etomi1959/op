import streamlit as st
import requests
import json
import os
from datetime import datetime

# Oldal konfiguráció
st.set_page_config(
    page_title="ET MI Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Egyedi CSS a felület testreszabásához
st.markdown("""
<style>
    .main {
        background-color: #f5f7f9;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
    .stButton>button {
        border-radius: 10px;
        background-color: #4CAF50;
        color: white;
    }
    .chat-container {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .user-message {
        background-color: #0A1F44;
        text-align: right;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .bot-message {
        background-color: #013220;
        text-align: left;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .title-container {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    .title-text {
        margin-left: 20px;
    }
</style>
""", unsafe_allow_html=True)

# OpenRouter API konfiguráció
if "openrouter_api_key" not in st.session_state:
    st.session_state.openrouter_api_key = ""

openrouter_api_url = "https://openrouter.ai/api/v1/chat/completions"

# Elérhető ingyenes vagy alacsony költségű modellek listája
ingyenes_modellek = [
    {"név": "OpenAI GPT-3.5 Turbo", "id": "openai/gpt-3.5-turbo", "leírás": "Gyors és hatékony általános célú modell"},
    {"név": "Mistral 7B Instruct", "id": "mistralai/mistral-7b-instruct", "leírás": "Nyílt forráskódú 7B paraméteres modell"},
    {"név": "Phi-3 Mini", "id": "microsoft/phi-3-mini", "leírás": "Microsoft kompakt méretű modell"},
    {"név": "Gemma 7B", "id": "google/gemma-7b-it", "leírás": "Google által fejlesztett nyílt modell"},
    {"név": "LLaMA 3 8B", "id": "meta-llama/llama-3-8b-instruct", "leírás": "Meta új generációs modellje"},
    {"név": "Nous Hermes 2", "id": "nous-hermes/nous-hermes-2-mixtral-8x7b-dpo", "leírás": "Mixtral alapú, finomhangolt modell"},
    {"név": "Qwen 1.5 Chat", "id": "qwen/qwen1.5-7b-chat", "leírás": "Alibaba fejlesztésű többnyelvű modell"},
    {"név": "Yi 1.5 Chat", "id": "01-ai/yi-1.5-9b-chat", "leírás": "Általános célú ázsiai modell"},
    {"név": "Claude Instant", "id": "anthropic/claude-instant-1", "leírás": "Anthropic gyors és hatékony modellje"},
    {"név": "Vicuna 13B", "id": "lmsys/vicuna-13b-v1.5", "leírás": "Nyílt LLaMA alapú finomhangolt modell"}
]

# Sidebar - API kulcs és modell beállítása
with st.sidebar:
    st.image("logo.png", width=150)
    st.title("Beállítások")
    
    st.session_state.openrouter_api_key = st.text_input(
        "OpenRouter API Kulcs", 
        value=st.session_state.openrouter_api_key,
        type="password",
        help="Add meg az OpenRouter API kulcsodat. Ha nincs, szerezz egyet az openrouter.ai oldalon."
    )
    
    st.subheader("Válassz modellt")
    valasztott_modell = st.selectbox(
        "AI Modell",
        options=[model["név"] for model in ingyenes_modellek],
        index=0,
        format_func=lambda x: x
    )
    
    # A kiválasztott modell adatainak megjelenítése
    selected_index = [model["név"] for model in ingyenes_modellek].index(valasztott_modell)
    st.info(ingyenes_modellek[selected_index]["leírás"])
    
    if st.button("Beszélgetés mentése"):
        if "messages" in st.session_state and st.session_state.messages:
            # Beszélgetés exportálása szöveges formátumban
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_filename = f"chat_export_{timestamp}.txt"
            
            with open(export_filename, "w", encoding="utf-8") as f:
                for msg in st.session_state.messages:
                    role = "Felhasználó" if msg["role"] == "user" else "Asszisztens"
                    f.write(f"{role}: {msg['content']}\n\n")
            
            st.success(f"Beszélgetés elmentve: {export_filename}")
    
    if st.button("Új beszélgetés"):
        st.session_state.messages = []
        st.stop()

# Főoldal
st.markdown('<div class="title-container">', unsafe_allow_html=True)
st.markdown('<h1 class="title-text">🤖 ET saját MI Chatbot</h1>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Session state inicializálása
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat konténer
chat_container = st.container()

# Korábbi üzenetek megjelenítése
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)

# Új üzenet fogadása
prompt = st.chat_input("Írd be az üzeneted...")

if prompt:
    # API kulcs ellenőrzése
    if not st.session_state.openrouter_api_key:
        st.error("Kérlek add meg az OpenRouter API kulcsot a bal oldali menüben!")
        st.stop()
    
    # Felhasználói üzenet hozzáadása
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Az üzenet azonnal megjelenítése
    with chat_container:
        st.markdown(f'<div class="user-message">{prompt}</div>', unsafe_allow_html=True)
    
    # Kiválasztott modell azonosítójának megszerzése
    selected_index = [model["név"] for model in ingyenes_modellek].index(valasztott_modell)
    model_id = ingyenes_modellek[selected_index]["id"]
    
    # API kérés előkészítése
    headers = {
        "Authorization": f"Bearer {st.session_state.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-domain.com",  # Sajátodra cserélheted
        "X-Title": "Saját AI Chatbot"  # Ez megjelenik az OpenRouter statisztikákban
    }
    
    payload = {
        "model": model_id,
        "messages": [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    }
    
    # Kérés küldése
    with st.spinner("Gondolkodik..."):
        try:
            response = requests.post(openrouter_api_url, headers=headers, json=payload)
            response.raise_for_status()  # Hibák ellenőrzése
            response_data = response.json()
            
            # Válasz feldolgozása
            if "choices" in response_data and len(response_data["choices"]) > 0:
                assistant_response = response_data["choices"][0]["message"]["content"]
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                
                # Válasz megjelenítése
                with chat_container:
                    st.markdown(f'<div class="bot-message">{assistant_response}</div>', unsafe_allow_html=True)
            else:
                st.error("A válasz nem tartalmaz válaszlehetőségeket.")
        except requests.exceptions.RequestException as e:
            st.error(f"Hiba történt az API hívás során: {str(e)}")
        except json.JSONDecodeError:
            st.error("Nem sikerült feldolgozni az API választ.")
        except Exception as e:
            st.error(f"Váratlan hiba történt: {str(e)}")

# Információs szekció a lap alján
st.markdown("---")
st.markdown("""
### Hogyan használd:
1. Add meg az OpenRouter API kulcsod a bal oldali menüben
2. Válaszd ki a használni kívánt modellt
3. Kezdj el chattelni a modellel
4. Mentsd el a beszélgetést vagy kezdj újat a gombokkal

Az OpenRouter lehetővé teszi több AI modell használatát egyetlen API kulccsal.
""")