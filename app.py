# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from google import genai
from google.genai import types

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA E DESIGN SYSTEM
# ==========================================
st.set_page_config(
    page_title="Corretor de Redação - IA Pro",
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

# Arquivo local para salvar histórico de redações
HISTORICO_FILE = "historico_redacoes.json"

def carregar_historico():
    if os.path.exists(HISTORICO_FILE):
        try:
            with open(HISTORICO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def salvar_historico(novo_registro):
    historico = carregar_historico()
    historico.insert(0, novo_registro)
    with open(HISTORICO_FILE, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=4)

# ==========================================
# 3. SIDEBAR DE CONFIGURAÇÃO E PARÂMETROS
# ==========================================
with st.sidebar:
    st.markdown("### 📝 Corretor Pro - IA")
    st.caption("Powered by Gemini 3.6 Flash")
    st.markdown("---")
    
    tipo_exame = st.selectbox(
        "Padrão Principal:",
        ["ENEM (Competências 1 a 5)", "Dissertativo-Argumentativo Padrão", "Concurso Público (Personalizado)"]
    )
    
    st.markdown("### 🏛️ Parâmetros da Banca")
    banca_nome = st.selectbox("Banca Organizadora:", ["Geral / Outra", "CESPE / Cebraspe", "FGV", "FCC", "Vunesp", "IBFC"])
    nota_maxima = st.number_input("Nota Máxima:", min_value=10, max_value=1000, value=100, step=10)
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        linhas_min = st.number_input("Mín. Linhas:", min_value=0, max_value=50, value=20)
    with col_l2:
        linhas_max = st.number_input("Máx. Linhas:", min_value=0, max_value=60, value=30)
        
    st.markdown("---")
    st.markdown("### 🚀 Recursos Exclusivos Pro")
    ativar_comparador = st.checkbox("🔄 Habilitar Simulador Cruzado de 2 Bancas", value=True, help="Avalia o texto simultaneamente em dois padrões diferentes.")
    banca_secundaria = st.selectbox("Segunda Banca para Comparação:", ["ENEM", "CESPE / Cebraspe", "FGV", "FCC"]) if ativar_comparador else None

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
# 4. INTERFACE PRINCIPAL (ABAS DO SISTEMA)
# ==========================================
st.markdown("<h1 style='margin:0;'>📝 Plataforma Inteligente de Correção de Redações Pro</h1>", unsafe_allow_html=True)
st.markdown("Sistema avançado com análise de espelhos visuais, reescrita interativa, raio-x de repertórios e histórico analítico.")
st.markdown("---")

aba_corretor, aba_reescrita, aba_historico = st.tabs(["🚀 Corretor & Relatório", "✍️ Reescrita Interativa (Nota 10)", "📈 Dashboard & Histórico de Erros"])

with aba_corretor:
    col_input, col_output = st.columns([1, 1], gap="large")

    with col_input:
        st.subheader("✍️ Envio do Texto ou Foto")
        tema_redacao = st.text_input("🎯 Tema da Redação:", placeholder="Ex: Os desafios da valorização da água no Brasil")
        
        sub_aba_texto, sub_aba_foto = st.tabs(["⌨️ Digitar Texto", "📸 Enviar Foto da Redação"])
        
        with sub_aba_texto:
            texto_usuario = st.text_area("Digite ou cole sua redação:", height=320, placeholder="Insira o texto completo...")
        
        with sub_aba_foto:
            foto_redacao_files = st.file_uploader(
                "Envie foto(s) da folha manuscrita:",
                type=["png", "jpg", "jpeg"],
                accept_multiple_files=True,
                key="foto_redacao_upload"
            )
            if foto_redacao_files:
                st.success(f"✅ {len(foto_redacao_files)} imagem(ns) da redação anexada(s)!")
        
        botao_analisar = st.button("🚀 Executar Análise Cirúrgica", use_container_width=True)

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
                with st.spinner("A IA está processando o espelho visual, cruzando com a banca e gerando o diagnóstico..."):
                    
                    contents_payload = []
                    
                    if imagens_criterios:
                        contents_payload.append("--- IMAGENS COM OS CRITÉRIOS E ESPELHO DE PONTUAÇÃO DA BANCA ---")
                        for img in imagens_criterios:
                            contents_payload.append(types.Part.from_bytes(data=img.getvalue(), mime_type=img.type or "image/jpeg"))

                    if foto_redacao_files:
                        contents_payload.append("--- FOTO(S) DA REDAÇÃO ESCRITA PELO ALUNO ---")
                        for foto in foto_redacao_files:
                            contents_payload.append(types.Part.from_bytes(data=foto.getvalue(), mime_type=foto.type or "image/jpeg"))

                    info_texto_digitado = f"\nTexto Digitado pelo Aluno:\n{texto_usuario}" if texto_usuario.strip() else "\n(O aluno enviou a redação em formato de imagem/foto)."

                    comparativo_texto = f"\n- Simulador Cruzado Ativo: Compare também como essa redação pontuaria sob o olhar da banca secundária: {banca_secundaria}." if ativar_comparador and banca_secundaria else ""

                    texto_prompt_final = f"""
INSTRUÇÕES DE AVALIAÇÃO:
- Padrão de Exame Base: {tipo_exame}
- Banca Organizadora Principal: {banca_nome}
- Nota Máxima Permitida: {nota_maxima} pontos
- Limite de Linhas: de {linhas_min} a {linhas_max} linhas
{comparativo_texto}

DIRETRIZES:
1. Utilize obrigatoriamente as imagens de critérios/espelhos para pontuar quesito por quesito de forma exata.
2. Faça um "Raio-X de Repertórios e Clichês", avaliando se o aluno utilizou argumentos "coringas" repetitivos ou repertórios produtivos originais.
{info_texto_digitado}

Tema da Redação: {tema_redacao}
"""
                    contents_payload.append(texto_prompt_final)

                    prompt_sistema = f"""Você é o corretor mais técnico, rigoroso e avançado do mercado para bancas de redação e concursos.
Sua tarefa é analisar as imagens enviadas (espelho/critérios e/ou foto da redação), transcrever o texto manuscrito se necessário, e entregar uma avaliação estruturada e cirúrgica.

Estruture sua resposta obrigatoriamente usando Markdown com as seguintes seções:
1. **Nota Global Atribuída** (Proporcional a {nota_maxima} pontos).
2. **Resumo do Espelho e Gride de Pontuação** (Tabela ou tópicos detalhando quanto tirou em cada quesito visualizado).
3. **Transcrição Detectada** (Caso tenha enviado foto, traga o texto transcrito).
4. **Raio-X de Repertórios e Clichês** (Análise crítica sobre a originalidade e o uso de argumentos coringas).
5. **Desvios Gramaticais e Estruturais** (Erros ortográficos e sintáticos apontados).
6. **Caminho para a Nota Máxima** (Orientações exatas de reescrita).
{("(7. Comparativo Cruzado com " + str(banca_secundaria) + ")") if ativar_comparador and banca_secundaria else ""}
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
                        resultado_final = response.text
                        st.markdown(resultado_final)
                        
                        # Salva automaticamente no histórico local
                        salvar_historico({
                            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "tema": tema_redacao,
                            "banca": banca_nome,
                            "resultado": resultado_final
                        })
                        
                    except Exception as e:
                        st.error(f"Erro ao processar a solicitação com a API do Gemini: {e}")
        else:
            st.info("Configure os critérios na barra lateral, envie o texto ou foto da redação e clique em **Executar Análise Cirúrgica**.")

with aba_reescrita:
    st.subheader("✍️ Módulo de Reescrita Interativa (Nota 10)")
    st.markdown("Cole abaixo um parágrafo específico ou sua redação fraca para que a IA reescreva mantendo o seu estilo original, mas elevando-o ao gabarito da banca.")
    
    paragrafo_alvo = st.text_area("Trecho ou Parágrafo Original:", height=150, placeholder="Cole aqui o parágrafo que tirou nota baixa...")
    instrucao_melhoria = st.text_input("Foco da Reescrita:", value="Elevar o nível argumentativo, corrigir desvios e garantir pontuação máxima na coesão.")
    
    if st.button("✨ Gerar Versão Nota Máxima"):
        if not st.session_state.active_gemini_key:
            st.error("Chave de API não configurada.")
        elif not paragrafo_alvo.strip():
            st.warning("Insira o trecho original.")
        else:
            with st.spinner("Reescrevendo o texto com padrão de excelência..."):
                prompt_reescrita = f"""Atue como um redator gabaritado em concursos e vestibulares.
Reescreva o trecho abaixo com base no padrão {tipo_exame} e banca {banca_nome}.
Instruções: {instrucao_melhoria}

Trecho Original:
{paragrafo_alvo}

Apresente:
1. **Versão Reescrita (Nota Máxima)**
2. **O que foi melhorado em relação ao original**
"""
                try:
                    resp_re = gemini_client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=prompt_reescrita,
                        config=types.GenerateContentConfig(temperature=0.3)
                    )
                    st.markdown(resp_re.text)
                except Exception as e:
                    st.error(f"Erro: {e}")

with aba_historico:
    st.subheader("📈 Dashboard & Histórico de Redações")
    st.markdown("Acompanhe o seu progresso e os temas já corrigidos na plataforma.")
    
    historico = carregar_historico()
    if not historico:
        st.info("Nenhuma redação salva no histórico ainda. Faça sua primeira correção na aba ao lado!")
    else:
        st.metric("Total de Redações Corrigidas", len(historico))
        st.markdown("---")
        for i, item in enumerate(historico):
            with st.expander(f"📌 {item['tema']} ({item['banca']}) - {item['data']}"):
                st.markdown(item['resultado'])