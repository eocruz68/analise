import streamlit as st
import pandas as pd
import requests
import os
import base64
import pytz
import time
from datetime import datetime
from PIL import Image
import io

# --- CONFIGURAÇÃO DA PÁGINA (Deve ser o primeiro comando Streamlit) ---
st.set_page_config(page_title="Blaze Double Pro", layout="wide")

if "historico" not in st.session_state:
    st.session_state.historico = [] 

# --- ESTILIZAÇÃO ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .titulo-vibrante {
        color: #FF4500; font-size: 45px !important; font-weight: bold;
        text-align: center; text-shadow: 2px 2px 10px rgba(255, 69, 0, 0.3);
        margin-bottom: 30px;
    }
    .custom-time {
        text-align: center; font-size: 12px; color: white; font-weight: bold;
        background-color: #333; border-radius: 4px; padding: 2px 5px;
        margin-top: 4px; display: block; width: fit-content;
        margin-left: auto; margin-right: auto;
    }
    .numero-grande {
        font-size: 20px; font-weight: bold; color: white;
        border-radius: 8px; width: 45px; height: 45px;
        display: flex; align-items: center; justify-content: center; border: 1px solid #444;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="titulo-vibrante">🚥 ANALISES BLAZE DOUBLE</p>', unsafe_allow_html=True)

# --- FUNÇÕES DE SUPORTE ---
#ARQUIVO_LOG = "historico_resultados.csv"

def fetch_data():
    try:
        url = "https://blaze.bet.br/api/singleplayer-originals/originals/roulette_games/recent/1"
        # User-Agent mais completo para evitar bloqueios da API
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            dados = response.json()
            # Garante que o retorno é de fato uma lista válida
            return dados if isinstance(dados, list) else []
        return []
    except:
        return []

@st.cache_data(show_spinner=False)
def get_image_base64(roll_value):
    try:
        img_path = os.path.join("imagens_numeros", f"{roll_value}.png")
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                return f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}"
    except:
        return None
    return None

# --- FRAGMENTO PARA ATUALIZAÇÃO SEM PISCAR ---
@st.fragment(run_every=5) 
def mostrar_resultados():
    novos_dados = fetch_data()
    houve_novo_branco = False
    
    # 1. Filtra IDs locais ignorando entradas inválidas ou None
    ids_locais = {
        j.get('id') for j in st.session_state.historico 
        if isinstance(j, dict) and j.get('id') is not None
    }
    
    # 2. Processa novos dados de forma segura
    for jogo in reversed(novos_dados):
        # Garante que 'jogo' é um dicionário e possui a chave 'id'
        if isinstance(jogo, dict) and 'id' in jogo and jogo['id'] is not None:
            if jogo['id'] not in ids_locais:
                st.session_state.historico.append(jogo)
                if jogo.get('color') == 0: 
                    houve_novo_branco = True

    # Renderiza
    if st.session_state.historico:
        resultados = st.session_state.historico
        num_cols = 20
        rows = [resultados[i:i + num_cols] for i in range(0, len(resultados), num_cols)]
        
        for row in reversed(rows):
            cols = st.columns(num_cols)
            for i, jogo in enumerate(row):
                # Proteção extra caso o item na linha não seja um dicionário válido
                if i < num_cols and isinstance(jogo, dict) and 'roll' in jogo:
                    roll_value = jogo.get('roll', '?')
                    cor_id = jogo.get('color', 1)
                    
                    try:
                        utc_time = datetime.strptime(jogo['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc)
                        time_str = utc_time.astimezone(pytz.timezone("America/Sao_Paulo")).strftime("%H:%M")
                    except:
                        time_str = "--:--"

                    img_base64 = get_image_base64(roll_value)
                    
                    if img_base64:
                        content = f'<img src="{img_base64}" style="width: 45px; height: 45px; border-radius: 8px;">'
                    else:
                        cor_hex = "#f12c4c" if cor_id == 1 else "#1a1d20" if cor_id == 2 else "#ffffff"
                        txt_color = "black" if cor_id == 0 else "white"
                        content = f'<div class="numero-grande" style="background-color: {cor_hex}; color: {txt_color};">{roll_value}</div>'

                    cols[i].markdown(f"""
                        <div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 15px;">
                            {content}
                            <span class="custom-time">{time_str}</span>
                        </div>
                        """, unsafe_allow_html=True)
    
    if houve_novo_branco:
        st.toast("O BRANCO SAIU! ⚪", icon="🔥")

# Chama o fragmento
mostrar_resultados()
