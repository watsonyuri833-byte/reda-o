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
# 3. SIDEBAR DE CONFIGURAÇÃO E REQUISITOS DA BANCA
# ==========================================
with st.sidebar:
    st.markdown("### 📝 Corretor de Redação")
    st.caption("Powered by Gemini 3.6 Flash")
    st.markdown("---")
    
    tipo_exame = st.selectbox(
        "Padrão de Correção:",
        ["ENEM (Competências 1 a 5)", "Dissertativo-Argumentativo Padrão", "Concurso Público (Personalizado)"]
    )
    
    st.markdown("### 🏛️ Requisitos da Banca")
    st.markdown("Cole abaixo as regras, edital ou exigências específicas da banca organizadora (ex: CESPE/Cebraspe, FGV, FCC, Vunesp):")
    
    requisitos_banca = st.text_area(
        "Critérios Extras da Banca:",
        placeholder="Ex: Considerar o limite de 30 linhas, penalizar fuga ao tema em x pontos, exigir coesão interparágrafos rígida, etc.",
        height=150
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
st.markdown("Insira o tema e o texto da sua redação para receber uma análise técnica detalhada baseada no padrão e nos requisitos informados.")
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
            with st.spinner("A IA está avaliando rigorosamente o texto com base no padrão e nos requisitos da banca..."):
                
                # Monta a instrução incluindo os requisitos da banca informados pelo usuário
                instrucao_banca_extra = ""
                if requisitos_banca.strip():
                    instrucao_banca_extra = f"\n\nREQUISITOS ESPECÍFICOS DA BANCA / EDITAL INFORMADOS PELO USUÁRIO:\n{requisitos_banca}\n(Você DEVE seguir rigorosamente estes critérios adicionais na correção)."

                prompt_sistema = f"""Você é um corretor oficial, altamente técnico e rigoroso em redações com foco no padrão {tipo_exame}.{instrucao_banca_extra}
Seu objetivo é analisar o texto enviado pelo aluno tendo em vista o tema especificado e as regras da banca.

Estruture sua resposta de forma clara utilizando Markdown contendo obrigatoriamente:
1. **Nota Global Estimada** (Atribua uma nota final detalhada com base nos critérios).
2. **Avaliação por Critérios / Competências** (Análise aprofundada dos pontos fortes e falhas em cada eixo).
3. **Desvios Gramaticais e Estruturais** (Aponte termos ou trechos que precisam de correção ortográfica ou sintática).
4. **Caminho para a Nota Máxima** (Orientações práticas de como reescrever os trechos para alcançar a excelência segundo a banca).
"""

                conteudo_prompt = f"Tema da Redação: {tema_redacao}\n\nTexto do Aluno:\n{texto_usuario}"

                try:
                    response = gemini_client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=conteudo_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=prompt_sistema,
                            temperature=0.2, # Mantém maior rigor técnico e consistência
                        )
                    )
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Erro ao processar a solicitação com a API do Gemini: {e}")
    else:
        st.info("Preencha o tema, configure os requisitos na barra lateral (se desejar), insira sua redação e clique em **Analisar e Corrigir Redação**.")