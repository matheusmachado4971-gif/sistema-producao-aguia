import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import pytz

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Sistema Águia - Produção", page_icon="🦅", layout="centered")

# Estilização Personalizada para Identidade Visual Águia Sistemas
st.markdown("""
<style>
    /* Fundo da página */
    .main { background-color: #f4f7f9; }
    
    /* Borda principal que envolve cabeçalho e formulário JUNTOS */
    .borda-principal {
        border: 2px solid #24247D !important;
        border-radius: 12px !important;
        background-color: #FFFFFF !important;
        overflow: hidden !important;
        margin-bottom: 20px !important;
    }

    
    /* Forçar cores nas bordas */
    div[data-testid="stVerticalBlock"] {
        border: none !important;
    }
    
    .st-emotion-cache-1r6slb0 {
        border: none !important;
        padding: 0 !important;
        border-radius: 0 !important;
        background-color: transparent !important;
        box-shadow: none !important;
        margin-bottom: 0 !important;
    }

    .stButton>button { 
        background-color: #004a99; 
        color: white; 
        font-weight: bold; 
        width: 100%; 
        border-radius: 4px;
        height: 3em;
    }
    
    /* Cor dos títulos em azul */
    h2 { 
        color: #24247D !important; 
        margin-top: 0; 
    }
    
    .stSubheader {
        color: #24247D !important;
    }
    
    /* Labels dos inputs em azul */
    .stTextInput label, 
    .stNumberInput label, 
    .stSelectbox label,
    .stTextArea label {
        color: #24247D !important;
        font-weight: 500 !important;
    }
    
    /* Remover bordas padrão do Streamlit */
    .stForm {
        border: none !important;
        padding: 0 !important;
    }
    
    .st-emotion-cache-16idsys {
        border: none !important;
    }
    
    /* Manter o layout padrão (fino, centralizado) */
    .block-container {
        max-width: 750px !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE CONEXÃO (VIA SECRETS) ---
def conectar_google_sheets():
    try:
        # Puxa apenas as credenciais da conta de serviço
        creds_info = st.secrets["gcp_service_account"]
        
        # ID da sua planilha da Águia Sistemas
        id_planilha = "11LPXBE0bg5VXZbiHpXKiQmw9wASJFg-NhhU4cI5K40U"
        
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        
        # Abre a planilha pelo ID
        spreadsheet = client.open_by_key(id_planilha)
        return spreadsheet.get_worksheet(0) 
    except Exception as e:
        st.error(f"Erro na conexão com Google Sheets: {e}")
        return None

# --- BORDA PRINCIPAL (envolve cabeçalho E formulário juntos) ---
st.markdown('<div class="borda-principal">', unsafe_allow_html=True)

# --- CABEÇALHO (sem borda extra, normal) ---
col1, col2 = st.columns([1, 3]) 

with col1:
    st.markdown("<br>", unsafe_allow_html=True)
    # Verifica se o arquivo logo.jpeg existe e o exibe
    if os.path.exists("logo.jpeg"):
        st.image("logo.jpeg", width=120)
    else:
        st.image("https://aguiasistemas.com/wp-content/uploads/logo-aguia-sistemas.svg", width=120)

with col2:
    st.markdown("", unsafe_allow_html=True) 
    st.markdown("<h2>Gestão de Produção - Longarinas</h2>", unsafe_allow_html=True)
    st.markdown("<p>Desenvolvido pelo operador web: Matheus Machado</p>", unsafe_allow_html=True)

st.divider()

# --- BORDA DO FORMULÁRIO ---
st.markdown('<div class="borda-formulario">', unsafe_allow_html=True)

# --- FORMULÁRIO DE ENTRADA ---
with st.form("form_producao", clear_on_submit=True):
    st.subheader("Lançamento de Dados")
    
    c1, c2 = st.columns(2)
    with c1:
        mes = st.selectbox("Mês", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])
        dia = st.number_input("Dia", min_value=1, max_value=31, step=1)
        tipo_longarina = st.selectbox("Tipo de Longarina", ["Padrão", "Especial", "Reforçada"])
        
    with c2:
        total_prod = st.number_input("Total Prod.", min_value=0, step=1)
        falha_voadora = st.number_input("Falha Voadora", min_value=0, step=1)
        falha_garra = st.number_input("Falha Garra (GME)", min_value=0, step=1)

    observacoes = st.text_area("Observações")
    inspetor = st.text_input("Nome do Inspetor")
    
    btn_salvar = st.form_submit_button("REGISTRAR NA PLANILHA")

st.markdown('</div>', unsafe_allow_html=True)  # Fecha borda-formulario

st.markdown('</div>', unsafe_allow_html=True)  # Fecha borda-principal

# --- LÓGICA DE SALVAMENTO ---
if btn_salvar:
    if total_prod == 0:
        st.warning("⚠️ Por favor, informe o total de produção.")
    elif (falha_voadora + falha_garra) > total_prod:
        st.error("❌ A soma das falhas não pode ser maior que o total produzido.")
    else:
        with st.spinner("Enviando dados..."):
            aba = conectar_google_sheets()
            if aba:
                # Dados organizados conforme as colunas A até H da sua planilha
                fuso_brasilia = pytz.timezone('America/Sao_Paulo')
                agora_brasilia = datetime.now(fuso_brasilia)
                
                nova_linha = [
                    mes, dia, total_prod, falha_voadora, 
                    falha_garra, tipo_longarina, observacoes, inspetor,
                    agora_brasilia.strftime("%d/%m/%Y %H:%M:%S"), # Agora com fuso correto
                ]
                
                try:
                    # Envia os dados para a planilha
                    aba.append_row(nova_linha, value_input_option="USER_ENTERED")
                    st.success(f"✅ Registro do dia {dia} enviado com sucesso!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Erro ao salvar na planilha: {e}")
# atualização fuso