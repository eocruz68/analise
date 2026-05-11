import streamlit as st
import pandas as pd
import requests
import os
import base64
import pytz
from datetime import datetime
from PIL import Image
import io

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Blaze Double Pro", layout="wide")

# Estilos
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .titulo-vibrante { color: #FF4500; font-size: 40px; font-weight: bold; text-align: center; }
    .numero-grande {
        font-size: 20px; font-weight: bold; color: white;
        border-radius: 8px; width: 45px; height: 45px;
        display: flex; align-items: center; justify-content: center; border: 1px solid #444;
    }
    .custom-time { font-size: 11px; color: #aaa; text-align: center; display: block; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="titulo-vibrante">🚥 ANALISES BLAZE DOUBLE</p>', unsafe_allow_html=True)

if "historico" not in st.session_state:
    st.session_state.historico = []

# --- FUNÇÃO DE BUSCA (COM DIAGNÓSTICO) ---
def fetch_data():
    url = "https://blaze.bet.br/api/singleplayer-originals/originals/roulette_games/recent/1"
    # Headers muito mais detalhados para parecer um humano
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept": "application/json",
        "Referer": "https://blaze.bet.br/pt/games/double",
        "Origin": "https://blaze.bet.br"
    }
    try:
        # Adicionamos o 'verify=False' para ignorar travas de SSL simples
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro da Blaze: Status {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Erro de Conexão: {e}")
        return []

@st.cache_data(show_spinner=False)
def get_image_base64(roll_value):
    try:
        path = os.path.join("imagens_numeros", f"{roll_value}.png")
        if os.path.exists(path):
            with Image.open(path) as img:
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"
    except: pass
    return None

# --- EXIBIÇÃO ---
@st.fragment(run_every=5)
def container_principal():
    status_placeholder = st.empty()
    status_placeholder.caption("🔄 Atualizando dados...")
    
    novos_dados = fetch_data()
    
    if novos_dados:
        # Atualiza histórico
        ids_atuais = {j['id'] for j in st.session_state.historico if 'id' in j}
        for jogo in reversed(novos_dados):
            if jogo['id'] not in ids_atuais:
                st.session_state.historico.append(jogo)
        
        # Mostra os resultados
        if st.session_state.historico:
            resultados = list(reversed(st.session_state.historico))
            num_cols = 12
            
            for i in range(0, len(resultados), num_cols):
                cols = st.columns(num_cols)
                batch = resultados[i:i+num_cols]
                for idx, jogo in enumerate(batch):
                    img = get_image_base64(jogo['roll'])
                    if img:
                        content = f'<img src="{img}" width="45">'
                    else:
                        cor = "#f12c4c" if jogo['color'] == 1 else "#1a1d20" if jogo['color'] == 2 else "#ffffff"
                        txt = "white" if jogo['color'] != 0 else "black"
                        content = f'<div class="numero-grande" style="background-color:{cor};color:{txt}">{jogo["roll"]}</div>'
                    
                    cols[idx].markdown(f'{content}', unsafe_allow_html=True)
        
        status_placeholder.success(f"✅ Conectado - {len(st.session_state.historico)} giros registrados")
    else:
        status_placeholder.warning("⚠️ Aguardando dados da Blaze... (Pode ser bloqueio de IP)")

container_principal()
