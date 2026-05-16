import streamlit as st
import ollama
import rag_engine
import agent_validator

# ============================================================
# 1. CONFIGURAÇÃO DA PÁGINA E TEMA VISUAL PREMIUM
# ============================================================
st.set_page_config(
    page_title="Saúde 24 - Triagem IA",
    page_icon="https://www.sns24.gov.pt/wp-content/uploads/2019/08/sns-24-logo.png",
    layout="centered",
    initial_sidebar_state="expanded"
)

# CSS CUSTOM PREMIUM - Tema médico escuro com glassmorphism
st.markdown("""
<style>
    /* ===== IMPORTAR FONTES ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ===== RESET E BASE ===== */
    *, *::before, *::after { box-sizing: border-box; }

    .stApp {
        background: linear-gradient(160deg, #0a0f1a 0%, #0d1b2a 35%, #1b2838 70%, #0a1628 100%);
        font-family: 'Inter', sans-serif;
    }

    /* ===== HEADER / TITULO ===== */
    .custom-header {
        text-align: center;
        padding: 1.8rem 1rem 1rem 1rem;
        margin-bottom: 0.5rem;
    }
    .custom-header h1 {
        background: linear-gradient(135deg, #38bdf8 0%, #06d6a0 50%, #38bdf8 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 0.2rem;
        animation: shimmer 4s ease-in-out infinite;
    }
    @keyframes shimmer {
        0%, 100% { background-position: 0% center; }
        50% { background-position: 200% center; }
    }
    .custom-header .subtitle {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 400;
        letter-spacing: 0.3px;
    }
    .pulse-dot {
        display: inline-block;
        width: 8px; height: 8px;
        background: #06d6a0;
        border-radius: 50%;
        margin-right: 6px;
        animation: pulse 2s ease-in-out infinite;
        vertical-align: middle;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(6, 214, 160, 0.5); }
        50% { opacity: 0.7; box-shadow: 0 0 0 8px rgba(6, 214, 160, 0); }
    }

    /* ===== ESCONDER ELEMENTOS PADRAO DO STREAMLIT ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent !important; }
    .stApp > header { display: none; }
    h1[data-testid="stHeading"] { display: none; }
    .stChatMessage + div > p:first-child { display: none; }
    div[data-testid="stCaption"] { display: none; }

    /* ===== AREA DO CHAT ===== */
    section[data-testid="stChatMessageContainer"],
    .stChatMessageContainer {
        padding-bottom: 80px !important;
    }

    /* ===== BALOES DE MENSAGEM ===== */
    div[data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        padding: 1rem 1.2rem !important;
        margin-bottom: 0.7rem !important;
        transition: border-color 0.3s ease, background 0.3s ease;
    }
    div[data-testid="stChatMessage"]:hover {
        border-color: rgba(56, 189, 248, 0.15) !important;
        background: rgba(255, 255, 255, 0.06) !important;
    }

    /* Mensagens do assistente */
    div[data-testid="stChatMessage"]:has(img[alt="assistant"]),
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        border-left: 3px solid rgba(6, 214, 160, 0.5) !important;
    }

    /* Mensagens do utilizador */
    div[data-testid="stChatMessage"]:has(img[alt="user"]),
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        border-left: 3px solid rgba(56, 189, 248, 0.5) !important;
    }

    /* Texto dentro das mensagens */
    div[data-testid="stChatMessage"] p,
    div[data-testid="stChatMessage"] li,
    div[data-testid="stChatMessage"] span {
        color: #e2e8f0 !important;
        font-size: 0.92rem !important;
        line-height: 1.7 !important;
    }
    div[data-testid="stChatMessage"] strong {
        color: #38bdf8 !important;
    }
    div[data-testid="stChatMessage"] em {
        color: #94a3b8 !important;
    }
    div[data-testid="stChatMessage"] hr {
        border-color: rgba(255,255,255,0.08) !important;
        margin: 0.8rem 0 !important;
    }

    /* ===== CAIXA DE INPUT (FLUTUANTE) ===== */
    div[data-testid="stChatInput"] {
        background: transparent !important;
        border-top: none !important;
        padding: 0.6rem 2rem 1rem 2rem !important;
    }
    /* O container interno do input */
    div[data-testid="stChatInput"] > div {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(56, 189, 248, 0.15) !important;
        border-radius: 24px !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        padding: 0.3rem 0.4rem !important;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3) !important;
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
    div[data-testid="stChatInput"] > div:focus-within {
        border-color: rgba(56, 189, 248, 0.35) !important;
        box-shadow: 0 4px 32px rgba(56, 189, 248, 0.1) !important;
    }
    div[data-testid="stChatInput"] textarea {
        background: transparent !important;
        border: none !important;
        border-radius: 20px !important;
        color: #e2e8f0 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important;
        padding: 0.6rem 0.8rem !important;
        resize: none !important;
    }
    div[data-testid="stChatInput"] textarea:focus {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #64748b !important;
    }
    div[data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #06d6a0, #38bdf8) !important;
        border: none !important;
        border-radius: 50% !important;
        width: 36px !important;
        height: 36px !important;
        min-width: 36px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: opacity 0.2s ease, transform 0.2s ease;
    }
    div[data-testid="stChatInput"] button:hover {
        opacity: 0.85 !important;
        transform: scale(1.1);
    }
    div[data-testid="stChatInput"] button svg {
        fill: #0a0f1a !important;
    }

    /* ===== SPINNER ===== */
    .stSpinner > div {
        border-top-color: #06d6a0 !important;
    }
    .stSpinner > div > span {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
    }

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1b2a 0%, #0a1628 100%) !important;
        border-right: 1px solid rgba(56, 189, 248, 0.08) !important;
    }
    section[data-testid="stSidebar"] * {
        color: #cbd5e1 !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #38bdf8 !important;
        font-weight: 600 !important;
    }

    .sidebar-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(56, 189, 248, 0.12);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }
    .sidebar-card h4 {
        color: #06d6a0 !important;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    .sidebar-card p {
        color: #e2e8f0 !important;
        font-size: 0.85rem;
        margin: 0.2rem 0;
        line-height: 1.5;
    }
    .sidebar-card .label {
        color: #64748b !important;
        font-size: 0.75rem;
    }

    /* ===== STATUS BADGE ===== */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        letter-spacing: 0.3px;
    }
    .status-triagem {
        background: rgba(251, 191, 36, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(251, 191, 36, 0.3);
    }
    .status-consulta {
        background: rgba(6, 214, 160, 0.15);
        color: #06d6a0;
        border: 1px solid rgba(6, 214, 160, 0.3);
    }

    /* ===== ALERTAS STREAMLIT ===== */
    div[data-testid="stAlert"] {
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        border-radius: 12px !important;
        color: #fca5a5 !important;
    }

    /* ===== BOTÕES SIDEBAR ===== */
    section[data-testid="stSidebar"] button {
        background: rgba(56, 189, 248, 0.08) !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        border-radius: 12px !important;
        color: #38bdf8 !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease !important;
    }
    section[data-testid="stSidebar"] button:hover {
        background: rgba(56, 189, 248, 0.15) !important;
        border-color: rgba(56, 189, 248, 0.4) !important;
        box-shadow: 0 0 16px rgba(56, 189, 248, 0.15) !important;
        transform: translateY(-1px);
    }
    section[data-testid="stSidebar"] button:active {
        transform: translateY(0);
    }</style>
""", unsafe_allow_html=True)

# ============================================================
# 2. HEADER CUSTOM (substitui o título padrão do Streamlit)
# ============================================================
st.markdown("""
<div class="custom-header">
    <h1>Assistente de Triagem Médica</h1>
    <p class="subtitle"><span class="pulse-dot"></span>Apoio e aconselhamento inspirado na Linha Saúde 24</p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# 3. CACHE DO RAG (evita recarregar FAISS do disco a cada mensagem)
# ============================================================
@st.cache_resource(show_spinner=False)
def carregar_rag():
    """Carrega o índice FAISS e os documentos para memória uma única vez."""
    import json
    import faiss
    try:
        index = faiss.read_index(rag_engine.FAISS_INDEX_FILE)
        with open(rag_engine.CHUNKS_JSON_FILE, "r", encoding="utf-8") as f:
            documentos = json.load(f)
        return index, documentos
    except Exception:
        return None, None

# Pré-carregar o RAG ao iniciar
_rag_index, _rag_docs = carregar_rag()


def pesquisar_rag_rapido(pergunta, k=3):
    """Pesquisa no RAG usando o índice já em memória (muito mais rápido)."""
    import numpy as np
    if _rag_index is None or _rag_docs is None or _rag_index.ntotal == 0:
        return ""

    resposta = ollama.embeddings(model=rag_engine.MODELO_EMBEDDINGS, prompt=pergunta)
    embedding = np.array([resposta['embedding']], dtype='float32')

    k_real = min(k, _rag_index.ntotal)
    distancias, indices = _rag_index.search(embedding, k_real)

    contexto = ""
    for idx, i in enumerate(indices[0]):
        if i != -1 and i < len(_rag_docs):
            contexto += f"--- Protocolo {idx+1} ---\n"
            contexto += _rag_docs[i]["texto"] + "\n\n"
    return contexto


# ============================================================
# 4. ESTADO DA SESSÃO
# ============================================================
import time as _time
def _saudacao():
    h = _time.localtime().tm_hour
    if h < 13: return "Bom dia"
    elif h < 20: return "Boa tarde"
    else: return "Boa noite"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": (
            f"{_saudacao()}! Bem-vindo(a) ao serviço de triagem virtual.\n\n"
            "Sou a assistente da Linha Saúde 24 e estou aqui para o/a ajudar a perceber "
            "melhor os seus sintomas e orientá-lo(a) nos próximos passos.\n\n"
            "Para começarmos, podia dizer-me **o seu nome e a sua idade**, por favor?"
        )}
    ]
    # Fases: "identificacao" -> "consulta"
    # O utilizador diz o nome/idade, depois fala diretamente com o LLM
    # O LLM recebe SEMPRE o histórico completo e nunca repete perguntas
    st.session_state.fase = "identificacao"
    st.session_state.dados = {}

if "triagem_resumo" not in st.session_state:
    st.session_state.triagem_resumo = None


# ============================================================
# 5. SIDEBAR COM INFORMAÇÃO DO DOENTE
# ============================================================
with st.sidebar:
    st.markdown("### Ficha do Doente")

    dados = st.session_state.dados
    fase = st.session_state.fase

    if fase == "identificacao":
        st.markdown("""
        <div class="sidebar-card">
            <h4>Estado</h4>
            <span class="status-badge status-triagem">Triagem Inicial</span>
            <p style="margin-top: 0.6rem;">A aguardar identificação do doente...</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Mostrar dados já recolhidos
        nome_idade = dados.get("nome_idade", "---")
        st.markdown(f"""
        <div class="sidebar-card">
            <h4>Identificação</h4>
            <p>{nome_idade}</p>
        </div>
        """, unsafe_allow_html=True)

        if dados.get("queixa"):
            st.markdown(f"""
            <div class="sidebar-card">
                <h4>Queixa Principal</h4>
                <p>{dados['queixa'][:120]}{'...' if len(dados.get('queixa','')) > 120 else ''}</p>
            </div>
            """, unsafe_allow_html=True)

        if dados.get("condicoes"):
            st.markdown(f"""
            <div class="sidebar-card">
                <h4>Histórico / Alergias</h4>
                <p>{dados['condicoes'][:120]}{'...' if len(dados.get('condicoes','')) > 120 else ''}</p>
            </div>
            """, unsafe_allow_html=True)

        status = "consulta" if fase == "consulta" else "triagem"
        badge_class = "status-consulta" if fase == "consulta" else "status-triagem"
        label = "Em Consulta" if fase == "consulta" else "Triagem em Curso"
        st.markdown(f"""
        <div class="sidebar-card">
            <h4>Estado</h4>
            <span class="status-badge {badge_class}">{label}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")  # Espaço
    if st.button("🔄 Nova Triagem", use_container_width=True, key="nova_triagem"):
        for key in ["messages", "fase", "dados", "triagem_resumo"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.markdown("---")
    st.markdown(
        "<p style='font-size: 0.7rem; color: #475569 !important; text-align: center;'>"
        "Ambientes Inteligentes<br>"
        "Universidade do Minho 2025/26</p>",
        unsafe_allow_html=True
    )


# ============================================================
# 6. MOSTRAR HISTÓRICO DE MENSAGENS
# ============================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ============================================================
# 7. LÓGICA PRINCIPAL — INPUT DO UTILIZADOR
# ============================================================
if prompt := st.chat_input("Descreva o que está a sentir..."):

    # Mostrar mensagem do utilizador
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    fase = st.session_state.fase

    # ----------------------------------------------------------
    # FASE 1: IDENTIFICAÇÃO (nome e idade)
    # ----------------------------------------------------------
    if fase == "identificacao":
        st.session_state.dados["nome_idade"] = prompt

        # ---- DETEÇÃO DE GÉNERO PELO NOME ----
        # Extrai o primeiro nome e infere o género
        # Regra geral do português: nomes acabados em -a = feminino, -o = masculino
        nome_completo = prompt.strip().split(",")[0].strip()  # "Deolinda, 57 anos" -> "Deolinda"
        primeiro_nome = nome_completo.split()[0].strip().capitalize() if nome_completo else ""

        # Nomes masculinos comuns que acabam em -a (exceções)
        nomes_masc_excecao = {"nikita", "josefa", "andrea"}
        # Nomes femininos comuns que não acabam em -a
        nomes_fem_excecao = {"ines", "inês", "raquel", "isabel", "beatriz", "leonor",
                             "alice", "filipa", "carmen", "pilar", "flor", "mercedes"}

        nome_lower = primeiro_nome.lower()
        if nome_lower in nomes_masc_excecao:
            genero = "masculino"
        elif nome_lower in nomes_fem_excecao or nome_lower.endswith("a"):
            genero = "feminino"
        elif nome_lower.endswith(("o", "os")):
            genero = "masculino"
        else:
            genero = "neutro"

        st.session_state.dados["nome"] = primeiro_nome
        st.session_state.dados["genero"] = genero
        st.session_state.fase = "consulta"

        # Adaptar a mensagem ao género
        if genero == "feminino":
            ajuda = "ajudá-la"
            obrigado = "obrigada"
        elif genero == "masculino":
            ajuda = "ajudá-lo"
            obrigado = "obrigado"
        else:
            ajuda = "ajudar"
            obrigado = "obrigado(a)"

        resposta = (
            f"Muito {obrigado}, {primeiro_nome}! Fico contente por poder {ajuda}.\n\n"
            f"Agora preciso de perceber o que se passa consigo. "
            f"**Descreva-me o que está a sentir**, incluindo há quanto tempo "
            f"começou e se tem alguma doença crónica ou alergia a medicamentos.\n\n"
            f"*Pode dizer tudo com calma, numa só mensagem ou aos poucos.*"
        )

        with st.chat_message("assistant"):
            st.markdown(resposta)
        st.session_state.messages.append({"role": "assistant", "content": resposta})

    # ----------------------------------------------------------
    # FASE 2: CONSULTA (conversa com RAG + LLM + Triagem do TXT)
    # O LLM recebe SEMPRE o histórico completo da conversa,
    # por isso NUNCA repete perguntas que o utilizador já respondeu.
    # ----------------------------------------------------------
    elif fase == "consulta":
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("*A consultar protocolos clínicos...*")

            # Guardar a queixa principal (primeira vez que o doente fala dos sintomas)
            if "queixa" not in st.session_state.dados:
                st.session_state.dados["queixa"] = prompt

            # ---- PESQUISA RAG (k=2 para ser mais rápido) ----
            contexto_medico = pesquisar_rag_rapido(prompt, k=2)

            # ---- CONSTRUIR CONTEXTO ----
            dados = st.session_state.dados
            genero = dados.get("genero", "neutro")
            nome = dados.get("nome", "")
            resumo = (
                "DADOS DE TRIAGEM DO DOENTE:\n"
                f"- Identificação: {dados.get('nome_idade', 'Não fornecido')}\n"
                f"- Nome: {nome}\n"
                f"- Género: {genero} (IMPORTANTE: usa terminações {'femininas (-a, -ada)' if genero == 'feminino' else 'masculinas (-o, -ado)' if genero == 'masculino' else 'neutras'} ao referir-te ao doente)\n"
            )
            if dados.get("queixa"):
                resumo += f"- Queixa inicial: {dados['queixa']}\n"

            st.session_state.triagem_resumo = resumo

            prompt_llm = (
                f"{resumo}\n\n"
                f"PROTOCOLOS CLÍNICOS RELEVANTES (RAG):\n{contexto_medico}\n\n"
                f"O QUE O DOENTE DISSE AGORA:\n{prompt}"
            )

            # ---- HISTÓRICO (últimas 10 mensagens para não sobrecarregar) ----
            historico = st.session_state.messages[:-1]
            if len(historico) > 10:
                historico = historico[-10:]

            mensagens_llm = [
                {"role": m["role"], "content": m["content"]} for m in historico
            ]
            mensagens_llm.append({"role": "user", "content": prompt_llm})

            # ---- STREAMING COM INDICADOR ANIMADO ----
            # O LLM demora a processar o contexto antes de emitir o 1º token.
            # Usamos uma thread para que o UI possa mostrar uma animação
            # enquanto espera, e o utilizador saiba que está a funcionar.
            import threading, queue, itertools

            fases_espera = itertools.cycle([
                "A analisar os seus sintomas",
                "A analisar os seus sintomas.",
                "A analisar os seus sintomas..",
                "A analisar os seus sintomas...",
                "A consultar protocolos clínicos",
                "A consultar protocolos clínicos.",
                "A consultar protocolos clínicos..",
                "A consultar protocolos clínicos...",
            ])

            token_queue = queue.Queue()

            def gerar_resposta():
                """Thread que chama o LLM e coloca tokens na fila."""
                try:
                    stream = ollama.chat(
                        model='triagem_bot',
                        messages=mensagens_llm,
                        stream=True
                    )
                    for chunk in stream:
                        token_queue.put(chunk['message']['content'])
                    token_queue.put(None)  # Fim do stream
                except Exception as e:
                    token_queue.put(e)

            thread = threading.Thread(target=gerar_resposta, daemon=True)
            thread.start()

            # Enquanto não chega o 1º token, anima o indicador
            resposta_llm = ""
            primeiro_token_recebido = False
            try:
                while True:
                    try:
                        item = token_queue.get(timeout=0.3)
                        if item is None:
                            break
                        if isinstance(item, Exception):
                            raise item
                        primeiro_token_recebido = True
                        resposta_llm += item
                        placeholder.markdown(resposta_llm + " ▌")
                        break
                    except queue.Empty:
                        # Ainda sem tokens — mostra animação
                        placeholder.markdown(f"*{next(fases_espera)}*")

                # Continuar o streaming — texto aparece palavra a palavra
                if primeiro_token_recebido:
                    while True:
                        try:
                            item = token_queue.get(timeout=5.0)
                            if item is None:
                                break
                            if isinstance(item, Exception):
                                raise item
                            resposta_llm += item
                            placeholder.markdown(resposta_llm + " ▌")
                        except queue.Empty:
                            break

            except Exception as e:
                placeholder.empty()
                st.error(
                    f"Não foi possível contactar o modelo. "
                    f"Verifique que o Ollama está a correr e que o modelo 'triagem_bot' existe.\n\n"
                    f"Erro: {e}"
                )
                st.stop()

            # ---- VALIDAÇÃO DO AGENTE DE SEGURANÇA ----
            resposta_final = agent_validator.validar_resposta_agente(
                resposta_llm,
                mensagem_utilizador=prompt
            )
            placeholder.markdown(resposta_final)
            st.session_state.messages.append({"role": "assistant", "content": resposta_final})