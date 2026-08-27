# -*- coding: utf-8 -*-
import os
import streamlit as st
from google import genai
from google.genai import types

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA E DESIGN SYSTEM
# ==========================================
st.set_page_config(
    page_title="Corretor de Redação - IA",
    page_icon="📝",
    layout="wide",
)

st.markdown(
    """
<style>
    .stApp { 
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%) !important; 
        color: #c9d1d9 !important;
    }
    .stApp p, .stApp label, .stApp span, h1, h2, h3, h4, h5, h6 {
        color: #e6edf3 !important;
    }
    div[data-baseweb="input"],
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] * {
        background-color: #161b22 !important;
        color: #f0f6fc !important;
    }
    .stApp input, 
    .stApp textarea, 
    .stApp select,
    div[role="combobox"] {
        background-color: #161b22 !important;
        color: #f0f6fc !important;
        border-color: #30363d !important;
    }
    div[data-baseweb="input"], div[data-baseweb="select"] {
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="select"]:focus-within,
    textarea:focus {
        border-color: #58a6ff !important;
        box-shadow: 0 0 0 1px #58a6ff !important;
    }
    ::placeholder, input::placeholder, textarea::placeholder {
        color: #8b949e !important;
        opacity: 1 !important;
    }
    .stButton>button {
        border-radius: 8px !important;
        border: 1px solid #30363d !important;
        background-color: #21262d !important;
        color: #c9d1d9 !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }
    .stButton>button:hover {
        border-color: #58a6ff !important;
        color: #58a6ff !important;
        background-color: #30363d !important;
        box-shadow: 0 0 10px rgba(88, 166, 255, 0.2) !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #30363d;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #161b22 !important;
        border-radius: 8px 8px 0px 0px !important;
        border: 1px solid #30363d !important;
        border-bottom: none !important;
        padding: 8px 16px !important;
        color: #8b949e !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #21262d !important;
        color: #58a6ff !important;
        border-top: 2px solid #58a6ff !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 2. INICIALIZAÇÃO DA API DO GEMINI
# ==========================================
INIT_GEMINI = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

if "active_gemini_key" not in st.session_state:
    st.session_state.active_gemini_key = INIT_GEMINI

@st.cache_resource
def init_gemini(api_key: str):
    if api_key:
        return genai.Client(api_key=api_key)
    return None

gemini_client = init_gemini(st.session_state.active_gemini_key)

# ==========================================
# 3. SIDEBAR DE CONFIGURAÇÃO E CRITÉRIOS DA BANCA
# ==========================================
with st.sidebar:
    st.markdown("### 📝 Corretor de Redação")
    st.caption("Powered by Gemini 3.6 Flash")
    st.markdown("---")
    
    tipo_exame = st.selectbox(
        "Padrão de Correção:",
        ["ENEM (Competências 1 a 5)", "Dissertativo-Argumentativo Padrão", "Concurso Público (Personalizado)"]
    )
    
    st.markdown("### 🏛️ Requisitos e Parâmetros da Banca")
    st.markdown("Organize abaixo as regras específicas exigidas pela banca organizadora:")
    
    # Campos estruturados para evitar bloco de texto confuso
    banca_nome = st.selectbox("Banca Organizadora:", ["Geral / Outra", "CESPE / Cebraspe", "FGV", "FCC", "Vunesp", "IBFC"])
    nota_maxima = st.number_input("Nota Máxima da Redação:", min_value=10, max_value=1000, value=100, step=10)
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        linhas_min = st.number_input("Mín. de Linhas:", min_value=0, max_value=50, value=20)
    with col_l2:
        linhas_max = st.number_input("Máx. de Linhas:", min_value=0, max_value=60, value=30)
        
    criterios_extras = st.text_area(
        "Instruções ou Foco Específico da Banca:",
        placeholder="Ex: Rigor excessivo com gramática, obrigatoriedade de título, penalização por desrespeito à estrutura dissertativa...",
        height=100
    )
    
    st.markdown("---")
    if not st.session_state.active_gemini_key:
        st.warning("⚠️ Chave `GEMINI_API_KEY` não encontrada nos secrets do Streamlit.")
    else:
        st.success("✅ IA Conectada com Sucesso")

# ==========================================
# 4. INTERFACE PRINCIPAL
# ==========================================
st.markdown("<h1 style='margin:0;'>📝 Plataforma Inteligente de Correção de Redações</h1>", unsafe_allow_html=True)
st.markdown("Insira o tema e o texto da sua redação para receber uma análise técnica detalhada baseada nos parâmetros e na banca definidos.")
st.markdown("---")

col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.subheader("✍️ Envio do Texto")
    tema_redacao = st.text_input("🎯 Tema da Redação:", placeholder="Ex: Os desafios da valorização da água no Brasil")
    texto_usuario = st.text_area("📄 Digite ou cole sua redação completa aqui:", height=420, placeholder="Insira o texto dissertativo-argumentativo...")
    
    botao_analisar = st.button("🚀 Analisar e Corrigir Redação", use_container_width=True)

with col_output:
    st.subheader("📊 Relatório Analítico de Correção")
    
    if botao_analisar:
        if not st.session_state.active_gemini_key:
            st.error("⚠️ Chave de API do Gemini não configurada. Adicione-a nos secrets do Streamlit.")
        elif not tema_redacao.strip():
            st.warning("⚠️ Por favor, informe o tema da redação.")
        elif not texto_usuario.strip():
            st.warning("⚠️ O campo de texto da redação está vazio.")
        else:
            with st.spinner("A IA está avaliando rigorosamente o texto com base nos critérios organizados da banca..."):
                
                # Consolida os parâmetros organizados de forma limpa para a IA
                parametros_banca_formatados = f"""
- Banca Organizadora: {banca_nome}
- Nota Máxima Permitida: {nota_maxima} pontos
- Limite de Linhas: de {linhas_min} a {linhas_max} linhas
- Observações / Foco Específico: {criterios_extras if criterios_extras.strip() else 'Nenhum adicional'}
"""

                prompt_sistema = f"""Você é um corretor oficial, altamente técnico e rigoroso em redações.
Padrão de Correção Base: {tipo_exame}

PARÂMETROS E REQUISITOS DA BANCA DEFINIDOS PELO USUÁRIO:
{parametros_banca_formatados}

Seu objetivo é analisar o texto enviado pelo aluno considerando rigorosamente estes parâmetros, a escala de nota máxima informada e as exigências da banca.

Estruture sua resposta de forma clara utilizando Markdown contendo obrigatoriamente:
1. **Nota Global Atribuída** (Proporcional à nota máxima de {nota_maxima} pontos).
2. **Avaliação por Critérios / Competências** (Análise técnica detalhada de acordo com as regras da banca).
3. **Desvios Gramaticais e Estruturais** (Aponte falhas ortográficas, sintáticas ou de formatação).
4. **Caminho para a Nota Máxima** (Orientações práticas de reescrita para alcançar o gabarito).
"""

                conteudo_prompt = f"Tema da Redação: {tema_redacao}\n\nTexto do Aluno:\n{texto_usuario}"

                try:
                    response = gemini_client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=conteudo_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=prompt_sistema,
                            temperature=0.2,
                        )
                    )
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Erro ao processar a solicitação com a API do Gemini: {e}")
    else:
        st.info("Ajuste os parâmetros da banca na barra lateral, insira sua redação e clique em **Analisar e Corrigir Redação**.")