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
    st.markdown("### 🖼️ Espelho / Critérios da Banca")
    imagens_criterios = st.file_uploader(
        "Fotos do edital ou espelho de pontos:",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="critarios_upload"
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
st.markdown("Envie os critérios na barra lateral, defina o tema e forneça o texto **digitando** ou enviando a **foto da sua folha de redação**.")
st.markdown("---")

col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.subheader("✍️ Envio do Texto ou Foto")
    tema_redacao = st.text_input("🎯 Tema da Redação:", placeholder="Ex: Os desafios da valorização da água no Brasil")
    
    # Abas para escolher entre Digitar ou Enviar Foto da Redação
    aba_texto, aba_foto = st.tabs(["⌨️ Digitar Texto", "📸 Enviar Foto da Redação"])
    
    with aba_texto:
        texto_usuario = st.text_area("Digite ou cole sua redação:", height=320, placeholder="Insira o texto completo...")
    
    with aba_foto:
        foto_redacao_files = st.file_uploader(
            "Envie foto(s) da sua folha de redação manuscrita:",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key="foto_redacao_upload"
        )
        if foto_redacao_files:
            st.success(f"✅ {len(foto_redacao_files)} imagem(ns) da redação anexada(s)!")
    
    botao_analisar = st.button("🚀 Analisar e Corrigir Redação", use_container_width=True)

with col_output:
    st.subheader("📊 Relatório Analítico de Correção")
    
    if botao_analisar:
        if not st.session_state.active_gemini_key:
            st.error("⚠️ Chave de API do Gemini não configurada.")
        elif not tema_redacao.strip():
            st.warning("⚠️ Por favor, informe o tema da redação.")
        elif not texto_usuario.strip() and not foto_redacao_files:
            st.warning("⚠️ Você precisa digitar o texto ou enviar a foto da sua redação.")
        else:
            with st.spinner("A IA está lendo as imagens (critérios e/ou redação manuscrita) e realizando a correção rigorosa..."):
                
                contents_payload = []
                
                # 1. Anexa imagens de critérios/espelho da banca, se houver
                if imagens_criterios:
                    contents_payload.append("--- IMAGENS COM OS CRITÉRIOS E ESPELHO DE PONTUAÇÃO DA BANCA ---")
                    for img in imagens_criterios:
                        contents_payload.append(types.Part.from_bytes(data=img.getvalue(), mime_type=img.type or "image/jpeg"))

                # 2. Anexa fotos da redação do aluno, se houver
                if foto_redacao_files:
                    contents_payload.append("--- FOTO(S) DA REDAÇÃO ESCRITA PELO ALUNO ---")
                    for foto in foto_redacao_files:
                        contents_payload.append(types.Part.from_bytes(data=foto.getvalue(), mime_type=foto.type or "image/jpeg"))

                # 3. Monta o prompt de instruções
                info_texto_digitado = f"\nTexto Digitado pelo Aluno:\n{texto_usuario}" if texto_usuario.strip() else "\n(O aluno enviou a redação em formato de imagem/foto)."

                texto_prompt_final = f"""
INSTRUÇÕES DE AVALIAÇÃO:
- Padrão de Exame Base: {tipo_exame}
- Banca Organizadora: {banca_nome}
- Nota Máxima Permitida: {nota_maxima} pontos
- Limite de Linhas: de {linhas_min} a {linhas_max} linhas

DIRETRIZES:
1. Se houver imagens de critérios da banca fornecidas acima, utilize-as obrigatoriamente para pontuar cada tópico, ver penalidades e exigências.
2. Se houver foto(s) da redação fornecida(s) acima, faça a transcrição visual e leitura detalhada da caligrafia do aluno para avaliá-la.
{info_texto_digitado}

Tema da Redação: {tema_redacao}
"""
                contents_payload.append(texto_prompt_final)

                prompt_sistema = f"""Você é um corretor oficial, altamente técnico e especialista em bancas de redação e concursos.
Sua tarefa é ler as imagens enviadas (espelho/critérios da banca e/ou foto da redação manuscrita do aluno), transcrever o texto caso necessário, e aplicar uma correção impecável e rigorosa.

Estruture sua resposta de forma clara utilizando Markdown contendo obrigatoriamente:
1. **Nota Global Atribuída** (Proporcional à nota máxima de {nota_maxima} pontos, embasada no espelho).
2. **Transcrição Detectada** (Se o aluno enviou foto, traga brevemente o texto transcrito para validação).
3. **Análise por Tópicos / Critérios do Espelho** (Pontuação detalhada quesito por quesito com base nas imagens da banca).
4. **Desvios Gramaticais e Estruturais** (Apontamento de desvios e erros).
5. **Caminho para a Nota Máxima** (Orientações exatas de como reescrever para gabaritar).
"""

                try:
                    response = gemini_client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=contents_payload,
                        config=types.GenerateContentConfig(
                            system_instruction=prompt_sistema,
                            temperature=0.1,
                        )
                    )
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Erro ao processar a solicitação com a API do Gemini: {e}")
    else:
        st.info("Configure os critérios na barra lateral, envie o texto ou a foto da redação e clique em **Analizar e Corrigir Redação**.")