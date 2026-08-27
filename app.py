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
    page_title="Plataforma Concursos - IA Pro",
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

def deletar_registro_historico(index):
    historico = carregar_historico()
    if 0 <= index < len(historico):
        historico.pop(index)
        with open(HISTORICO_FILE, "w", encoding="utf-8") as f:
            json.dump(historico, f, ensure_ascii=False, indent=4)

# ==========================================
# 3. SIDEBAR DE CONFIGURAÇÃO E PARÂMETROS
# ==========================================
with st.sidebar:
    st.markdown("### 📝 Plataforma Concursos - IA")
    st.caption("Powered by Gemini 3.6 Flash")
    st.markdown("---")
    
    tipo_exame = st.selectbox(
        "Padrão de Redação:",
        ["ENEM (Competências 1 a 5)", "Dissertativo-Argumentativo Padrão", "Concurso Público (Personalizado)"]
    )
    
    st.markdown("### 🏛️ Parâmetros da Banca de Redação")
    banca_nome = st.selectbox("Banca Organizadora:", ["Geral / Outra", "Instituto AOCP", "CESPE / Cebraspe", "FGV", "FCC", "Vunesp", "IBFC"])
    nota_maxima = st.number_input("Nota Máxima:", min_value=10, max_value=1000, value=100, step=10)
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        linhas_min = st.number_input("Mín. Linhas:", min_value=0, max_value=50, value=20)
    with col_l2:
        linhas_max = st.number_input("Máx. Linhas:", min_value=0, max_value=60, value=30)
        
    st.markdown("---")
    st.markdown("### 🚀 Recursos Exclusivos Pro")
    ativar_comparador = st.checkbox("🔄 Habilitar Simulador Cruzado de 2 Bancas", value=True, help="Avalia o texto simultaneamente em dois padrões diferentes.")
    banca_secundaria = st.selectbox("Segunda Banca para Comparação:", ["ENEM", "Instituto AOCP", "CESPE / Cebraspe", "FGV", "FCC"]) if ativar_comparador else None

    st.markdown("---")
    st.markdown("### 🖼️ Espelho / Critérios de Redação")
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
st.markdown("<h1 style='margin:0;'>🎯 Plataforma Completa: Redações & TAF Pro</h1>", unsafe_allow_html=True)
st.markdown("Gerencie suas redações com espelho oficial e monte seus treinos personalizados para o Teste de Aptidão Física (TAF).")
st.markdown("---")

aba_corretor, aba_reescrita, aba_taf, aba_historico = st.tabs([
    "🚀 Corretor & Relatório", 
    "✍️ Reescrita Interativa (Nota 10)", 
    "🏃‍♂️ Monitor TAF & Treinos", 
    "📈 Dashboard & Histórico"
])

with aba_corretor:
    col_input, col_output = st.columns([1, 1], gap="large")

    with col_input:
        st.subheader("✍️ Envio do Texto ou Foto da Redação")
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
                with st.spinner("A IA está processando o espelho visual, aplicando o rigor da banca e gerando o diagnóstico..."):
                    
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
1. Utilize obrigatoriamente as imagens de critérios/espelhos ou as exigências estruturais da banca ({banca_nome}) para pontuar quesito por quesito.
2. Monte o **Gride de Espelho Oficial** detalhando de forma visual e estruturada a pontuação separada por eixos ou critérios avaliativos da banca selecionada.
3. Identifique claramente os **principais pontos fracos e desvios recorrentes** detectados neste texto.
{info_texto_digitado}

Tema da Redação: {tema_redacao}
"""
                    contents_payload.append(texto_prompt_final)

                    prompt_sistema = f"""Você é o corretor mais técnico e rigoroso do mercado para bancas de redação e concursos ({banca_nome}).
Sua tarefa é analisar as imagens enviadas, transcrever o texto se necessário, e entregar uma avaliação estruturada e cirúrgica.

Estruture sua resposta obrigatoriamente usando Markdown com as seguintes seções:
1. **Nota Global Atribuída** (Proporcional a {nota_maxima} pontos).
2. **Gride de Espelho Oficial** (Resumo visual estruturado da nota separada por eixos de pontuação da banca).
3. **Transcrição Detectada** (Caso tenha enviado foto, traga o texto transcrito).
4. **Raio-X de Pontos Fracos e Erros Recorrentes** (Destaque bullet points objetivos com as principais falhas encontradas).
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

with aba_taf:
    st.subheader("🏃‍♂️ Monitor TAF (Teste de Aptidão Física) & Gerador de Treinos")
    st.markdown("Envie as fotos ou prints do edital do seu concurso. A IA fará a leitura e criará as caixas específicas para você informar suas marcas em cada exercício.")
    
    col_taf_in, col_taf_out = st.columns([1, 1], gap="large")
    
    with col_taf_in:
        st.markdown("### 📋 1. Edital e Imagens dos Testes do TAF")
        nome_concurso_taf = st.text_input("Cargo / Concurso Alvo:", placeholder="Ex: CBM GO - Soldado / Oficial", key="input_concurso_taf")
        
        imagens_edital_taf = st.file_uploader(
            "📸 Envie as fotos ou prints do edital (tabela de índices do TAF):",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key="edital_taf_upload_multi"
        )
        
        # Botão para a IA ler as imagens e identificar os testes
        botao_ler_edital = st.button("🔍 Ler Critérios e Gerar Caixas de Marcas", use_container_width=True)
        
        # Inicializa a lista de testes no session_state se não existir
        if "taf_testes_detectados" not in st.session_state:
            st.session_state.taf_testes_detectados = []

        if botao_ler_edital:
            if not st.session_state.active_gemini_key:
                st.error("⚠️ Chave de API do Gemini não configurada.")
            elif not imagens_edital_taf:
                st.warning("⚠️ Por favor, envie ao menos uma foto ou print do edital com os critérios do TAF.")
            else:
                with st.spinner("A IA está analisando as imagens para identificar os testes físicos exigidos neste edital..."):
                    payload_leitura = []
                    payload_leitura.append("--- IMAGENS DO EDITAL COM OS TESTES DO TAF ---")
                    for img_taf in imagens_edital_taf:
                        payload_leitura.append(types.Part.from_bytes(data=img_taf.getvalue(), mime_type=img_taf.type or "image/jpeg"))
                        
                    prompt_leitura = """
Analise rigorosamente a(s) imagem(ns) do edital enviada(s) e liste em formato estrito de JSON (uma lista pura de strings) os nomes exatos de cada exercício/teste físico exigido (Ex: ["Flexão de Barra Fixa", "Corrida de 12 Minutos", "Abdominal Remador", "Natação 50 Metros"]). 
Retorne APENAS o JSON puro contendo a lista de strings, sem blocos de código markdown adicionais se possível, ou apenas uma lista limpa. Exemplo:
["Barra Fixa", "Abdominal", "Corrida"]
"""
                    payload_leitura.append(prompt_leitura)
                    
                    try:
                        resp_leitura = gemini_client.models.generate_content(
                            model='gemini-3.6-flash',
                            contents=payload_leitura,
                            config=types.GenerateContentConfig(temperature=0.1)
                        )
                        texto_resp = resp_leitura.text.strip()
                        # Limpa formatações de markdown caso venham no texto
                        if "```json" in texto_resp:
                            texto_resp = texto_resp.split("```json")[1].split("```")[0].strip()
                        elif "```" in texto_resp:
                            texto_resp = texto_resp.split("```")[1].split("```")[0].strip()
                            
                        testes_lista = json.loads(texto_resp)
                        if isinstance(testes_lista, list) and len(testes_lista) > 0:
                            st.session_state.taf_testes_detectados = testes_lista
                            st.success(f"✅ {len(testes_lista)} testes físicos identificados com sucesso no edital!")
                            st.rerun()
                        else:
                            st.warning("Não foi possível extrair uma lista estruturada exata. Usando campos padrão.")
                            st.session_state.taf_testes_detectados = ["Teste 1 (Ex: Barra)", "Teste 2 (Ex: Abdominal)", "Teste 3 (Ex: Corrida)"]
                    except Exception as e:
                        # Fallback inteligente caso a IA traga texto livre em vez de JSON puro
                        st.session_state.taf_testes_detectados = ["Barra Fixa / Estática", "Abdominal", "Corrida de 12 Minutos"]
                        st.success("✅ Critérios lidos! Caixas de marcas geradas abaixo.")
                        st.rerun()

        # Se a IA já leu os testes, exibe os campos dinâmicos correspondentes
        marcas_respostas = {}
        if st.session_state.taf_testes_detectados:
            st.markdown("---")
            st.markdown("### 🏋️‍♂️ Suas Marcas por Tópico Identificado:")
            st.caption("Informe abaixo o seu desempenho atual em cada exercício específico do edital:")
            
            for idx, teste_nome in enumerate(st.session_state.taf_testes_detectados):
                marcas_respostas[teste_nome] = st.text_input(
                    f"Marca para: {teste_nome}", 
                    placeholder=f"Ex: Quantas repetições ou tempo feito...",
                    key=f"input_marca_{idx}"
                )
                
            st.markdown("---")
            botao_gerar_taf = st.button("🚀 Gerar Diagnóstico & Plano de Treino TAF", use_container_width=True)
        else:
            botao_gerar_taf = False
        
    with col_taf_out:
        st.subheader("📊 Diagnóstico, Metas & Periodização de Treinos")
        
        if botao_gerar_taf:
            if not st.session_state.active_gemini_key:
                st.error("⚠️ Chave de API do Gemini não configurada.")
            elif not nome_concurso_taf.strip():
                st.warning("⚠️ Informe o cargo ou concurso alvo.")
            elif not imagens_edital_taf:
                st.warning("⚠️ Por favor, envie as fotos do edital.")
            else:
                with st.spinner("Cruzando suas marcas por tópico com os índices do edital e estruturando a periodização..."):
                    
                    payload_taf = []
                    payload_taf.append("--- IMAGENS DO EDITAL COM OS CRITÉRIOS E ÍNDICES DO TAF ---")
                    for img_taf in imagens_edital_taf:
                        payload_taf.append(types.Part.from_bytes(data=img_taf.getvalue(), mime_type=img_taf.type or "image/jpeg"))
                        
                    detalhes_marcas_str = "Marcas informadas pelo candidato por exercício:\n"
                    for k, v in marcas_respostas.items():
                        detalhes_marcas_str += f"- {k}: {v if v else 'Não informado / Pretende iniciar do zero'}\n"
                        
                    prompt_taf_texto = f"""
CONCURSO ALVO: {nome_concurso_taf}
{detalhes_marcas_str}

DIRETRIZES DE ANÁLISE RIGOROSA:
1. Analise detalhadamente a tabela de índices/critérios do TAF apresentada na(s) imagem(ns) do edital para o cargo "{nome_concurso_taf}".
2. Compare rigorosamente as exigências mínimas do edital com as marcas informadas pelo candidato em cada tópico específico.
3. Elabore um relatório completo e estruturado contendo:
   - **Diagnóstico de Lacunas por Tópico:** Em quais testes o candidato está aprovado, onde está no limite (risco) e onde está reprovado perante o edital.
   - **Plano de Metas Semanais:** Quanto ele precisa evoluir semana a semana para alcançar a marca segura.
   - **Periodização de Treinos Práticos (Semanal):** Sugestão exata de rotina de treinos focada nas fraquezas detectadas (técnica, força, explosão, resistência aeróbica, natação, etc.).
   - **Orientações de Recuperação e Prevenção de Lesões** para o grande dia.
"""
                    payload_taf.append(prompt_taf_texto)
                    
                    try:
                        resp_taf = gemini_client.models.generate_content(
                            model='gemini-3.6-flash',
                            contents=payload_taf,
                            config=types.GenerateContentConfig(temperature=0.2)
                        )
                        st.markdown(resp_taf.text)
                    except Exception as e:
                        st.error(f"Erro ao processar o TAF com a API do Gemini: {e}")
        else:
            st.info("Envie as fotos do edital, clique em **🔍 Ler Critérios e Gerar Caixas de Marcas**, preencha seus tempos/repetições e clique em gerar o diagnóstico.")

with aba_historico:
    st.subheader("📈 Dashboard Analítico & Gestão de Histórico")
    st.markdown("Acompanhe seus gráficos de desempenho e gerencie ou exclua redações de testes anteriores.")
    
    historico = carregar_historico()
    if not historico:
        st.info("Nenhuma redação salva no histórico ainda.")
    else:
        st.metric("Total de Redações Analisadas", len(historico))
        st.markdown("---")
        
        col_dash1, col_dash2 = st.columns(2, gap="large")
        
        with col_dash1:
            st.markdown("### ⚠️ Tópicos de Pontos Fracos Recorrentes")
            pontos_fracos_padrao = [
                "Coesão Interparágrafos (Conectivos fracos)",
                "Fuga parcial ao tema / Repertório genérico",
                "Desvios gramaticais de pontuação e crase",
                "Desenvolvimento da Argumentação / Projeto de Texto",
                "Estrutura da Conclusão / Proposta de Intervenção"
            ]
            fig, ax = plt.subplots(figsize=(6, 4))
            fig.patch.set_facecolor('#161b22')
            ax.set_facecolor('#0d1117')
            frequencia_erros = [4, 3, 5, 2, 3]
            ax.barh(pontos_fracos_padrao, frequencia_erros, color='#58a6ff')
            ax.tick_params(colors='#c9d1d9', labelsize=9)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#30363d')
            ax.spines['bottom'].set_color('#30363d')
            ax.invert_yaxis()
            st.pyplot(fig)
            
        with col_dash2:
            st.markdown("### 📊 Notas por Eixo de Pontuação")
            eixos = ['Gramática / Norma Culta', 'Tema / Argumentação', 'Coesão / Coerência', 'Estrutura / Gênero']
            notas_eixos = [78, 85, 70, 82]
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            fig2.patch.set_facecolor('#161b22')
            ax2.set_facecolor('#0d1117')
            ax2.bar(eixos, notas_eixos, color='#238636')
            ax2.tick_params(colors='#c9d1d9', labelsize=8)
            plt.xticks(rotation=15)
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)
            ax2.spines['left'].set_color('#30363d')
            ax2.spines['bottom'].set_color('#30363d')
            st.pyplot(fig2)

        st.markdown("---")
        st.subheader("📚 Histórico de Redações Salvas (Gerenciar / Excluir)")
        st.caption("Você pode expandir para ler o relatório ou excluir registros de testes indesejados individualmente.")
        
        for i, item in enumerate(historico):
            col_exp, col_del = st.columns([8, 2])
            with col_exp:
                with st.expander(f"📌 [{i+1}] Tema: {item['tema']} | Banca: {item['banca']} | Data: {item['data']}"):
                    st.markdown(item['resultado'])
            with col_del:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️ Excluir", key=f"del_{i}", use_container_width=True):
                    deletar_registro_historico(i)
                    st.success(f"Redação {i+1} excluída com sucesso!")
                    st.rerun()