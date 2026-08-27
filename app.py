# -*- coding: utf-8 -*-
import os
import streamlit as st
from google import genai
from google.genai import types

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Corretor de Redação IA",
    page_icon="??",
    layout="wide",
)

st.markdown("""
<style>
    .stApp { 
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%) !important; 
        color: #c9d1d9 !important;
    }
    .stApp p, .stApp label, .stApp span, h1, h2, h3, h4, h5, h6 {
        color: #e6edf3 !important;
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
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. INICIALIZAÇÃO DA API DO GEMINI
# ==========================================
# Pega a chave dos secrets do Streamlit ou de variável de ambiente
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

@st.cache_resource
def init_gemini(api_key: str):
    if api_key:
        return genai.Client(api_key=api_key)
    return None

gemini_client = init_gemini(GEMINI_API_KEY)

# ==========================================
# 3. INTERFACE DO APLICATIVO
# ==========================================
st.title("?? Corretor Inteligente de Redações")
st.markdown("Cole seu texto abaixo, informe o tema e receba uma análise detalhada baseada em critérios de grandes exames.")

with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/artificial-intelligence.png", width=120)
    st.markdown("### Configurações")
    tipo_exame = st.selectbox(
        "Padrão de Correção:",
        ["ENEM (Competências 1 a 5)", "Dissertativo-Argumentativo Padrão", "Concurso Público"]
    )
    st.markdown("---")
    st.info("Dica: Certifique-se de configurar sua `GEMINI_API_KEY` nos segredos do Streamlit (`.streamlit/secrets.toml`).")

# Área de entrada de dados
col1, col2 = st.columns([1, 1])

with col1:
    tema_redacao = st.text_input("?? Tema da Redação:", placeholder="Ex: Os desafios da mobilidade urbana no Brasil")
    texto_usuario = st.text_area("?? Digite ou cole sua redação aqui:", height=400, placeholder="Insira o texto completo do seu texto dissertativo...")
    
    botao_corrigir = st.button("?? Analisar e Corrigir Redação", use_container_width=True)

with col2:
    st.markdown("### ?? Relatório de Correção")
    
    if botao_corrigir:
        if not GEMINI_API_KEY:
            st.error("?? Chave de API do Gemini não configurada. Adicione a `GEMINI_API_KEY` no arquivo secrets.")
        elif not texto_usuario.strip():
            st.warning("?? Por favor, insira o texto da redação para realizar a análise.")
        elif not tema_redacao.strip():
            st.warning("?? Informe o tema da redação.")
        else:
            with st.spinner("A IA está analisando a gramática, coesão, argumento e estrutura..."):
                
                # Prompt estruturado para guiar a IA
                prompt_sistema = f"""Você é um corretor especialista e rigoroso em redações com foco no padrão {tipo_exame}.
Seu objetivo é avaliar o texto enviado pelo usuário considerando o tema: "{tema_redacao}".

Estruture sua resposta de forma clara utilizando Markdown com as seguintes seções:
1. **Nota Estimada Geral** (Atribua uma nota de 0 a 1000 ou proporcional ao padrão).
2. **Análise por Competências / Critérios** (Pontos fortes e o que faltou em cada aspecto).
3. **Desvios Gramaticais e Estruturais Encontrados** (Aponte trechos específicos que podem melhorar).
4. **Sugestão de Reescrita / Caminho Ideal** (Como o texto poderia ser aprimorado para alcançar a nota máxima).
"""

                conteudo_prompt = f"Tema: {tema_redacao}\n\nTexto do Aluno:\n{texto_usuario}"

                try:
                    response = gemini_client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=conteudo_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=prompt_sistema,
                            temperature=0.3, # Temperatura baixa para manter maior rigor técnico e consistência
                        )
                    )
                    
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Erro ao comunicar com a API do Gemini: {e}")
    else:
        st.info("Preencha os campos ao lado e clique em **Analisar e Corrigir Redação** para ver o feedback detalhado da IA.")