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
# 3. SIDEBAR DE CONFIGURAÇÃO E PARÂMETROS
# ==========================================
with st.sidebar:
    st.markdown("### 📝 Corretor de Redação")
    st.caption("Powered by Gemini 3.6 Flash")
    st.markdown("---")
    
    tipo_exame = st.selectbox(
        "Padrão de Correção:",
        ["ENEM (Competências 1 a 5)", "Dissertativo-Argumentativo Padrão", "Concurso Público (Personalizado)"]
    )
    
    st.markdown("### 🏛️ Parâmetros da Banca")
    banca_nome = st.selectbox("Banca Organizadora:", ["Geral / Outra", "CESPE / Cebraspe", "FGV", "FCC", "Vunesp", "IBFC"])
    nota_maxima = st.number_input("Nota Máxima da Redação:", min_value=10, max_value=1000, value=100, step=10)
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        linhas_min = st.number_input("Mín. Linhas:", min_value=0, max_value=50, value=20)
    with col_l2:
        linhas_max = st.number_input("Máx. Linhas:", min_value=0, max_value=60, value=30)
        
    st.markdown("---")
    st.markdown("### 🖼️ Espelho / Critérios da Banca (Imagens)")
    st.markdown("Envie fotos ou prints do edital, espelho de correção ou tabela de pontos da banca:")
    
    imagens_criterios = st.file_uploader(
        "Carregar imagens de critérios:",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True
    )
    
    st.markdown("---")
    if not st.session_state.active_gemini_key:
        st.warning("⚠️ Chave `GEMINI_API_KEY` não encontrada nos secrets.")
    else:
        st.success("✅ IA Conectada com Sucesso")

# ==========================================
# 4. INTERFACE PRINCIPAL
# ==========================================
st.markdown("<h1 style='margin:0;'>📝 Plataforma Inteligente de Correção de Redações</h1>", unsafe_allow_html=True)
st.markdown("Envie as imagens com os critérios da banca na barra lateral, preencha o tema e a sua redação abaixo para uma correção milimétrica.")
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
            st.error("⚠️ Chave de API do Gemini não configurada.")
        elif not tema_redacao.strip():
            st.warning("⚠️ Por favor, informe o tema da redação.")
        elif not texto_usuario.strip():
            st.warning("⚠️ O campo de texto da redação está vazio.")
        else:
            with st.spinner("A IA está analisando as imagens de critérios da banca e avaliando o texto rigorosamente..."):
                
                # Prepara a lista de conteúdos para o Gemini (aceita texto e imagens simultaneamente)
                contents_payload = []
                
                # Se o usuário enviou imagens de critérios, faz o append delas primeiro
                if imagens_criterios:
                    contents_payload.append("--- IMAGENS COM OS CRITÉRIOS, ESPELHO E PONTUAÇÃO DA BANCA ---")
                    for img in imagens_criterios:
                        img_bytes = img.getvalue()
                        # Identifica o tipo mime correto da imagem enviada
                        mime_type = img.type if img.type else "image/jpeg"
                        contents_payload.append(
                            types.Part.from_bytes(
                                data=img_bytes,
                                mime_type=mime_type,
                            )
                        )

                # Adiciona o texto da redação e o tema
                texto_prompt_final = f"""
INSTRUÇÕES DE AVALIAÇÃO:
- Padrão de Exame Base: {tipo_exame}
- Banca Organizadora: {banca_nome}
- Nota Máxima Permitida: {nota_maxima} pontos
- Limite de Linhas: de {linhas_min} a {linhas_max} linhas

{("IMPORTANTE: Utilize obrigatoriamente as imagens de critérios acima fornecidas para extrair detalhadamente o valor de cada tópico, o que pontua e o que retira pontos, aplicando rigorosamente essa tabela na correção." if imagens_criterios else "Avalie com base estrita nos critérios padrão da banca informada.")}

--- DADOS DA REDAÇÃO ---
Tema: {tema_redacao}

Texto do Aluno:
{texto_usuario}
"""
                contents_payload.append(texto_prompt_final)

                prompt_sistema = f"""Você é um corretor oficial, altamente técnico e especialista em bancas de redação e concursos.
Seu trabalho é ler com máxima atenção as imagens com os critérios/espelhos da banca enviadas pelo usuário, mapear exatamente o valor de cada ponto, penalidades e exigências, e em seguida avaliar o texto do aluno de forma cirúrgica com base exclusiva nelas.

Estruture sua resposta de forma clara utilizando Markdown contendo obrigatoriamente:
1. **Nota Global Atribuída** (Proporcional à nota máxima de {nota_maxima} pontos, fundamentada no espelho da banca).
2. **Análise por Tópicos / Critérios do Espelho** (Demonstre o quanto o aluno tirou em cada quesito visualizado nas imagens).
3. **Desvios Gramaticais e Estruturais** (Apontamento detalhado de falhas).
4. **Caminho para a Nota Máxima** (Orientações exatas de como ajustar o texto com base nas regras da banca).
"""

                try:
                    response = gemini_client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=contents_payload,
                        config=types.GenerateContentConfig(
                            system_instruction=prompt_sistema,
                            temperature=0.1, # Temperatura bem baixa para seguir estritamente o espelho visual
                        )
                    )
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Erro ao processar a solicitação com a API do Gemini: {e}")
    else:
        st.info("Envie as imagens dos critérios da banca na barra lateral (se houver), preencha a redação e clique em **Analisar e Corrigir Redação**.")