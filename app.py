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

# CSS CUSTOM PREMIUM - Tema médico claro e profissional
st.markdown("""
<style>
    /* ===== IMPORTAR FONTES ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ===== RESET E BASE ===== */
    *, *::before, *::after { box-sizing: border-box; }

    /* Fundo Principal */
    html, body, .stApp, .stApp > header, [data-testid="stAppViewContainer"], .main {
        background: #f0fdfa !important; 
        background-color: #f0fdfa !important;
        font-family: 'Inter', sans-serif !important;
        min-height: 100vh !important;
    }

    /* ===== HEADER / TITULO ===== */
    .custom-header {
        text-align: center;
        padding: 1.8rem 1rem 1rem 1rem;
        margin-bottom: 0.5rem;
    }
    .custom-header h1 {
        background: linear-gradient(135deg, #0d9488 0%, #0ea5e9 50%, #0d9488 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 0.2rem;
        animation: shimmer 4s ease-in-out infinite;
        text-shadow: 0 0 20px rgba(13, 148, 136, 0.2);
    }
    @keyframes shimmer {
        0%, 100% { background-position: 0% center; }
        50% { background-position: 200% center; }
    }
    .custom-header .subtitle {
        color: #475569;
        font-size: 0.95rem;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    .pulse-dot {
        display: inline-block;
        width: 10px; height: 10px;
        background: #0ea5e9;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s ease-in-out infinite;
        vertical-align: middle;
        box-shadow: 0 0 12px rgba(14, 165, 233, 0.6);
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.6; transform: scale(1.2); }
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
        padding-bottom: 120px !important;
    }

    /* ===== BALOES DE MENSAGEM ===== */
    div[data-testid="stChatMessage"] {
        background: #ffffff !important;
        border: 1px solid rgba(13, 148, 136, 0.1) !important;
        border-radius: 20px !important;
        padding: 1.2rem 1.5rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.03) !important;
        transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
    }
    div[data-testid="stChatMessage"]:hover {
        border-color: rgba(13, 148, 136, 0.3) !important;
        box-shadow: 0 10px 30px rgba(13, 148, 136, 0.08) !important;
        transform: translateY(-2px);
    }

    div[data-testid="stChatMessage"]:has(img[alt="assistant"]),
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        border-left: 5px solid #0d9488 !important;
    }

    div[data-testid="stChatMessage"]:has(img[alt="user"]),
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        border-left: 5px solid #0ea5e9 !important;
    }

    div[data-testid="stChatMessage"] p,
    div[data-testid="stChatMessage"] li,
    div[data-testid="stChatMessage"] span {
        color: #1e293b !important;
        font-size: 0.95rem !important;
        line-height: 1.7 !important;
        letter-spacing: 0.2px !important;
    }
    div[data-testid="stChatMessage"] strong {
        color: #0f766e !important;
    }
    div[data-testid="stChatMessage"] hr {
        border-color: rgba(13, 148, 136, 0.1) !important;
        margin: 1rem 0 !important;
    }

    /* ===== CAIXA DE INPUT ===== */
    [data-testid="stBottom"], 
    [data-testid="stBottomBlockContainer"],
    .stChatFloatingInputContainer,
    .stApp > div > div > div > div > div:last-child {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    .stApp:has(button[id*="-tab-1"][aria-selected="true"]) [data-testid="stBottom"],
    .stApp:has(div[data-testid="stTabs"] button:nth-of-type(2)[aria-selected="true"]) [data-testid="stBottom"] {
        display: none !important;
    }

    div[data-testid="stChatInput"] {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        padding: 0 2rem 2rem 2rem !important;
    }
    
    div[data-testid="stChatInput"] > div {
        background: #ffffff !important;
        border: 1px solid rgba(13, 148, 136, 0.2) !important;
        border-radius: 30px !important;
        padding: 0.4rem 0.6rem !important;
        box-shadow: 0 10px 30px rgba(13, 148, 136, 0.08) !important;
    }
    div[data-testid="stChatInput"] > div:focus-within {
        border-color: #0d9488 !important;
        box-shadow: 0 10px 40px rgba(13, 148, 136, 0.15) !important;
    }
    
    div[data-testid="stChatInput"] textarea {
        background: #ffffff !important;
        background-color: #ffffff !important;
        border: none !important;
        color: #1e293b !important;
        -webkit-text-fill-color: #1e293b !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        padding: 0.7rem 1.2rem !important;
        resize: none !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    div[data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #0d9488, #0ea5e9) !important;
        border: none !important;
        border-radius: 50% !important;
        width: 42px !important;
        height: 42px !important;
        min-width: 42px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 15px rgba(13, 148, 136, 0.3) !important;
        margin-right: 4px !important;
    }
    div[data-testid="stChatInput"] button svg { fill: #ffffff !important; }

    /* ===== SIDEBAR ===== */
    /* Títulos da Sidebar (Ficha do Doente) */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #0f766e !important;
        font-weight: 600 !important;
    }
    /* Layout da Sidebar */
    section[data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid rgba(13, 148, 136, 0.08) !important;
        box-shadow: 2px 0 20px rgba(0,0,0,0.03) !important;
    }
    .sidebar-card {
        background: #ffffff;
        border: 1px solid rgba(13, 148, 136, 0.15);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
    }
    .sidebar-card h4 {
        color: #0d9488 !important;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    .sidebar-card p {
        color: #475569 !important;
        font-size: 0.85rem;
        margin: 0.2rem 0;
        line-height: 1.6;
    }

    /* ===== STATUS BADGE ===== */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    .status-triagem { background: #fffbeb; color: #d97706; border: 1px solid #fde68a; }
    .status-consulta { background: #f0fdfa; color: #0d9488; border: 1px solid #99f6e4; }
    .status-verde { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
    .status-amarelo { background: #fef9c3; color: #854d0e; border: 1px solid #fef08a; }
    .status-vermelho { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }

    /* CAIXA QUE ENVOLVE OS BADGES */
    .status-box {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
    }

    /* ===== BOTÕES SIDEBAR ===== */
    section[data-testid="stSidebar"] button {
        background: #ffffff !important;
        border: 1px solid #5eead4 !important;
        border-radius: 12px !important;
        color: #0d9488 !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.3s ease !important;
    }
    section[data-testid="stSidebar"] button:hover {
        background: #f0fdfa !important;
        border-color: #0d9488 !important;
        box-shadow: 0 4px 12px rgba(13, 148, 136, 0.15) !important;
        transform: translateY(-2px);
    }

    /* ===== METRICAS DASHBOARD ===== */
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
        border-top: 4px solid #1abc9c;
        height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-value {
        font-size: 32px;
        font-weight: 800;
        color: #006666;
    }
    .metric-label {
        font-size: 14px;
        color: #7f8c8d;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

</style>
""", unsafe_allow_html=True)

# ============================================================
# 2. HEADER CUSTOM
# ============================================================
st.markdown("""
<div class="custom-header">
    <h1>Assistente de Triagem Médica</h1>
    <p class="subtitle"><span class="pulse-dot"></span>Apoio e aconselhamento inspirado na Linha Saúde 24</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 3. CACHE DO RAG E ESTADO
# ============================================================
@st.cache_resource(show_spinner=False)
def carregar_rag():
    import json, faiss
    try:
        index = faiss.read_index(rag_engine.FAISS_INDEX_FILE)
        with open(rag_engine.CHUNKS_JSON_FILE, "r", encoding="utf-8") as f:
            return index, json.load(f)
    except:
        return None, None

_rag_index, _rag_docs = carregar_rag()

def pesquisar_rag_rapido(pergunta, k=3):
    import numpy as np
    if not _rag_index or not _rag_docs or _rag_index.ntotal == 0: return ""
    resposta = ollama.embed(model=rag_engine.MODELO_EMBEDDINGS, input=pergunta)
    embedding = np.array([resposta['embeddings'][0]], dtype='float32')
    distancias, indices = _rag_index.search(embedding, min(k, _rag_index.ntotal))
    contexto = ""
    for idx, i in enumerate(indices[0]):
        if i != -1 and i < len(_rag_docs):
            contexto += f"--- Protocolo {idx+1} ---\n{_rag_docs[i]['texto']}\n\n"
    return contexto

import time as _time
def _saudacao():
    h = _time.localtime().tm_hour
    return "Bom dia" if h < 13 else "Boa tarde" if h < 20 else "Boa noite"

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": f"{_saudacao()}! Bem-vindo(a) ao serviço de triagem virtual.\n\nSou a assistente da Linha Saúde 24 e estou aqui para o/a ajudar a perceber melhor os seus sintomas e orientá-lo(a) nos próximos passos.\n\nPara começarmos, podia dizer-me **o seu nome, idade e com que género se identifica**, por favor?"}]
    st.session_state.fase = "identificacao"
    st.session_state.dados = {}

def calcular_urgencia_atual():
    if len(st.session_state.messages) <= 1:
        return "Verde"

    # Encontrar a última mensagem do bot
    ultima_msg_bot = ""
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "assistant":
            ultima_msg_bot = msg["content"].lower()
            break

    # 1. VERMELHO: Notas de Segurança ou encaminhamento hospitalar imediato
    if "[nota de segurança]" in ultima_msg_bot or "[intervenção do agente" in ultima_msg_bot:
        st.session_state.nivel_urgencia = "Vermelho"
        return "Vermelho"
        
    if any(w in ultima_msg_bot for w in ["urgência", "emergência", "112", "hospital", "pronto-socorro"]):
        st.session_state.nivel_urgencia = "Vermelho"
        return "Vermelho"

    # 2. AMARELO (Em Avaliação): O Bot está à espera de resposta ou a fazer perguntas
    if st.session_state.messages[-1]["role"] == "user":
        st.session_state.nivel_urgencia = "Amarelo"
        return "Amarelo"

    if "?" in ultima_msg_bot or "perguntas" in ultima_msg_bot:
        st.session_state.nivel_urgencia = "Amarelo"
        return "Amarelo"

    # 3. VERDE: Triagem Concluída com conselhos de autocuidado (e sem ser emergência)
    if any(w in ultima_msg_bot for w in ["repouso", "hidratação", "paracetamol", "ibuprofeno", "analgésico"]):
        st.session_state.nivel_urgencia = "Verde"
        return "Verde"
        
    # 4. AMARELO (Default Final): Se não for emergência (Vermelho) nem autocuidado óbvio (Verde)
    st.session_state.nivel_urgencia = "Amarelo"
    return "Amarelo"

# ============================================================
# 4. SIDEBAR E PLACEHOLDERS
# ============================================================
with st.sidebar:
    st.markdown("### Ficha do Doente")
    dados_placeholder = st.empty()
    st.markdown("<br>", unsafe_allow_html=True)
    botoes_placeholder = st.empty()
    st.markdown("---")
    st.markdown("<p style='font-size: 0.7rem; color: #475569 !important; text-align: center;'>Ambientes Inteligentes<br>Universidade do Minho 2025/26</p>", unsafe_allow_html=True)

def atualizar_sidebar():
    """Desenha a ficha IMEDIATAMENTE quando chamada, evitando clarões brancos."""
    with dados_placeholder.container():
        dados = st.session_state.dados
        fase = st.session_state.fase
        if fase == "identificacao":
            st.markdown("""<div class="sidebar-card"><h4>Estado</h4><span class="status-badge status-triagem">Triagem Inicial</span><p style="margin-top: 0.6rem;">A aguardar identificação do doente...</p></div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="sidebar-card"><h4>Identificação</h4><p>{dados.get("nome_idade", "---")}</p></div>""", unsafe_allow_html=True)
            if dados.get("queixa"):
                st.markdown(f"""<div class="sidebar-card"><h4>Queixa Principal</h4><p>{dados['queixa'][:120]}{'...' if len(dados.get('queixa','')) > 120 else ''}</p></div>""", unsafe_allow_html=True)
            if dados.get("condicoes"):
                st.markdown(f"""<div class="sidebar-card"><h4>Histórico / Alergias</h4><p>{dados['condicoes'][:120]}{'...' if len(dados.get('condicoes','')) > 120 else ''}</p></div>""", unsafe_allow_html=True)

            status = "consulta" if fase == "consulta" else "triagem"
            badge_class = "status-consulta" if fase == "consulta" else "status-triagem"
            label = "Em Consulta" if fase == "consulta" else "Triagem em Curso"
            
            urgencia = calcular_urgencia_atual()
            urg_class = "status-verde" if urgencia == "Verde" else "status-amarelo" if urgencia == "Amarelo" else "status-vermelho"
            urg_label = "🟢 Risco Baixo" if urgencia == "Verde" else "🟡 Avaliação" if urgencia == "Amarelo" else "🔴 EMERGÊNCIA"

            st.markdown(f"""<div class="sidebar-card"><h4>Estado & Risco</h4><div class="status-box"><span class="status-badge {badge_class}">{label}</span><span class="status-badge {urg_class}">{urg_label}</span></div></div>""", unsafe_allow_html=True)

# Chamada inicial para a ficha não estar em branco ao abrir a app
atualizar_sidebar()

# ============================================================
# 5. DASHBOARD E CHAT
# ============================================================
tab_chat, tab_dashboard = st.tabs(['💬 Chat Triagem', '📊 Dashboard Métricas'])

with tab_dashboard:
    import json, os, pandas as pd
    try:
        import plotly.express as px
    except ImportError:
        pass
    st.markdown('Bem-vindo ao painel de controlo. Aqui pode monitorizar em tempo real o volume e as características das triagens realizadas pelo Chatbot.')
    LOG_FILE = 'logs_triagem.json'
    if not os.path.exists(LOG_FILE):
        st.info('Ainda não existem registos suficientes.')
    else:
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                df = pd.DataFrame(json.load(f))
            if df.empty:
                st.info('Ainda não existem registos suficientes.')
            else:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['Data'] = df['timestamp'].dt.date
                df['Genero'] = df['doente'].apply(lambda x: x.get('genero', 'N/A').capitalize() if isinstance(x, dict) else 'N/A')
                col1, col2, col3, col4 = st.columns(4)
                total = len(df)
                emergencias = len(df[df['urgencia'] == 'Vermelho'])
                avaliacoes = len(df[df['urgencia'] == 'Amarelo'])
                risco_baixo = len(df[df['urgencia'] == 'Verde'])
                
                with col1:
                    st.markdown(f'<div class="metric-card"><div class="metric-value">{total}</div><div class="metric-label">Total de Triagens</div></div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div class="metric-card" style="border-top-color: #e74c3c;"><div class="metric-value" style="color: #c0392b;">{emergencias}</div><div class="metric-label">Emergências (112)</div></div>', unsafe_allow_html=True)
                with col3:
                    st.markdown(f'<div class="metric-card" style="border-top-color: #f1c40f;"><div class="metric-value" style="color: #f39c12;">{avaliacoes}</div><div class="metric-label">Em Avaliação</div></div>', unsafe_allow_html=True)
                with col4:
                    st.markdown(f'<div class="metric-card" style="border-top-color: #2ecc71;"><div class="metric-value" style="color: #27ae60;">{risco_baixo}</div><div class="metric-label">Risco Baixo</div></div>', unsafe_allow_html=True)
                
                st.markdown('<hr>', unsafe_allow_html=True)
                
                import re
                def get_age(x):
                    if isinstance(x, dict) and 'nome_idade' in x:
                        m = re.search(r'\d+', x['nome_idade'])
                        return int(m.group(0)) if m else 0
                    return 0
                
                df['Idade'] = df['doente'].apply(get_age)
                def cat_age(a):
                    if a == 0: return 'N/A'
                    if a < 18: return '< 18'
                    if a <= 35: return '18-35'
                    if a <= 50: return '36-50'
                    if a <= 65: return '51-65'
                    return '> 65'
                df['Faixa Etária'] = df['Idade'].apply(cat_age)
                df['Género'] = df['Genero']
                
                c1, c2 = st.columns(2)
                cores = {'Vermelho': '#e74c3c', 'Amarelo': '#f1c40f', 'Verde': '#2ecc71'}
                
                c1.markdown('**Nível de Gravidade**')
                fig1 = px.pie(df, names='urgencia', color='urgencia', color_discrete_map=cores, hole=0.4)
                fig1.update_layout(margin=dict(t=10, b=10, l=10, r=10))
                c1.plotly_chart(fig1, use_container_width=True)
                
                c2.markdown('**Evolução Diária**')
                vol = df.groupby('Data').size().reset_index(name='Triagens')
                fig2 = px.bar(vol, x='Data', y='Triagens', color_discrete_sequence=['#1abc9c'])
                fig2.update_layout(margin=dict(t=10, b=10, l=10, r=10))
                c2.plotly_chart(fig2, use_container_width=True)
                
                c3, c4 = st.columns(2)
                
                c3.markdown('**Casos por Género**')
                fig3 = px.histogram(df, x='Género', color='Género', color_discrete_sequence=['#3498db', '#e84393', '#95a5a6'])
                fig3.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
                c3.plotly_chart(fig3, use_container_width=True)
                
                c4.markdown('**Casos por Faixa Etária**')
                ordem_idades = ['< 18', '18-35', '36-50', '51-65', '> 65', 'N/A']
                fig4 = px.histogram(df, x='Faixa Etária', color_discrete_sequence=['#9b59b6'], category_orders={'Faixa Etária': ordem_idades})
                fig4.update_layout(margin=dict(t=10, b=10, l=10, r=10))
                c4.plotly_chart(fig4, use_container_width=True)
                
                st.markdown('<hr>', unsafe_allow_html=True)
                st.markdown('**Últimos Registos Clínicos**')
                df_tab = df.copy()
                df_tab['Paciente'] = df_tab['doente'].apply(lambda x: x.get('nome_idade', '') if isinstance(x, dict) else '')
                df_tab['Queixa'] = df_tab['doente'].apply(lambda x: x.get('queixa', '')[:50]+'...' if isinstance(x, dict) else '')
                df_tab['Data'] = df_tab['timestamp'].dt.strftime('%d/%m %H:%M')
                df_tab['Urgência'] = df_tab['urgencia']
                st.dataframe(df_tab[['Data', 'Paciente', 'Queixa', 'Urgência']].tail(10).iloc[::-1], hide_index=True, use_container_width=True)
        except Exception as e:
            st.error(f'Erro ao carregar dashboard: {e}')

prompt = st.chat_input("Descreva o que está a sentir...")

with tab_chat:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        fase = st.session_state.fase

        if fase == "identificacao":
            import re
            
            # Definimos o texto limpo logo aqui para não dar erro no género mais abaixo!
            texto_limpo = re.sub(r'[^\w\s]', ' ', prompt.lower())
            
            # --- NOVA LÓGICA DE NOME (APANHA ATÉ 2 PALAVRAS) ---
            match_nome = re.search(r"(?:chamo-me|sou o|sou a|sou|meu nome é|chamo me)\s+([A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+)?)", prompt, re.IGNORECASE)
            
            if match_nome:
                nome_capturado = match_nome.group(1).strip()
                palavras = nome_capturado.split()
                # Se a segunda palavra for lixo (ex: "tenho", "anos"), corta e usa só a primeira
                if len(palavras) > 1 and palavras[1].lower() in ["tenho", "e", "sou", "um", "uma", "mas", "anos"]:
                    primeiro_nome = palavras[0].capitalize()
                else:
                    primeiro_nome = nome_capturado.title()
            else:
                # Sistema de segurança antigo caso não apanhe a frase
                stop_words = {"eu","sou","o","a","chamo","me","meu","nome","é","e","tenho","anos","de","idade","olá","ola","bom","dia","boa","tarde","noite","genero","género","sexo","como"}
                palavras = texto_limpo.split()
                palavras_nome = [p for p in palavras if p not in stop_words and not p.isdigit() and p not in ["mulher","homem","feminino","masculino","rapariga","rapaz"]]
                primeiro_nome = palavras_nome[0].capitalize() if palavras_nome else "Utente"
            
            
            idade_match = re.search(r'\d+', prompt)
            idade_str = idade_match.group(0) if idade_match else "?"
            
            if any(w in texto_limpo for w in ["mulher","feminino","rapariga","menina","senhora","ela"]): genero = "feminino"
            elif any(w in texto_limpo for w in ["homem","masculino","rapaz","menino","senhor","ele"]): genero = "masculino"
            else: genero = "neutro"

            st.session_state.dados.update({"nome_idade": f"{primeiro_nome}, {idade_str} anos", "nome": primeiro_nome, "genero": genero, "idade": idade_str})
            st.session_state.fase = "consulta"
            
            atualizar_sidebar()

            ajuda, obrigado = ("ajudá-la", "obrigada") if genero == "feminino" else ("ajudá-lo", "obrigado") if genero == "masculino" else ("ajudá-lo(a)", "obrigado(a)")
            resposta = f"Muito {obrigado}, {primeiro_nome}! Fico contente por poder {ajuda}.\n\nAgora preciso de perceber o que se passa consigo. **Descreva-me o que está a sentir**, incluindo há quanto tempo começou e se tem alguma doença crónica ou alergia.\n\n*Pode dizer tudo com calma, numa só mensagem ou aos poucos.*"
            with st.chat_message("assistant"): st.markdown(resposta)
            st.session_state.messages.append({"role": "assistant", "content": resposta})

        elif fase == "consulta":
            with st.chat_message("assistant"):
                placeholder = st.empty()
                placeholder.markdown("*A consultar protocolos clínicos...*")

                if "queixa" not in st.session_state.dados:
                    st.session_state.dados["queixa"] = prompt

                _ = calcular_urgencia_atual()
                atualizar_sidebar()

                contexto_medico = pesquisar_rag_rapido(prompt, k=2)
                resumo = f"DADOS DE TRIAGEM:\n- Nome: {st.session_state.dados.get('nome')}\n- Idade: {st.session_state.dados.get('idade', '?')} anos\n- Género: {st.session_state.dados.get('genero')}\n- Queixa: {st.session_state.dados.get('queixa')}"
                prompt_llm = f"{resumo}\n\nPROTOCOLOS (RAG):\n{contexto_medico}\n\nO QUE O DOENTE DISSE AGORA:\n{prompt}"

                mensagens_llm = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1][-10:]]
                mensagens_llm.append({"role": "user", "content": prompt_llm})

                import threading, queue, itertools
                fases_espera = itertools.cycle(["A analisar sintomas.", "A analisar sintomas..", "A analisar sintomas..."])
                token_queue = queue.Queue()

                def gerar_resposta():
                    try:
                        for chunk in ollama.chat(model='triagem_bot', messages=mensagens_llm, stream=True):
                            token_queue.put(chunk['message']['content'])
                        token_queue.put(None) 
                    except Exception as e: token_queue.put(e)

                threading.Thread(target=gerar_resposta, daemon=True).start()

                resposta_llm = ""
                recebido = False
                try:
                    while True:
                        try:
                            item = token_queue.get(timeout=0.3)
                            if item is None: break
                            if isinstance(item, Exception): raise item
                            recebido = True
                            resposta_llm += item
                            placeholder.markdown(resposta_llm + " ▌")
                            break
                        except queue.Empty: placeholder.markdown(f"*{next(fases_espera)}*")

                    if recebido:
                        while True:
                            try:
                                item = token_queue.get(timeout=5.0)
                                if item is None: break
                                if isinstance(item, Exception): raise item
                                resposta_llm += item
                                placeholder.markdown(resposta_llm + " ▌")
                            except queue.Empty: break
                except Exception as e:
                    placeholder.empty()
                    st.error(f"Erro: {e}")
                    st.stop()

                try: resposta_final = agent_validator.validar_resposta_agente(resposta_llm, mensagem_utilizador=prompt)
                except: resposta_final = agent_validator.validar_resposta_agente(resposta_llm)

                placeholder.markdown(resposta_final)
                st.session_state.messages.append({"role": "assistant", "content": resposta_final})

                _ = calcular_urgencia_atual()
                atualizar_sidebar()

# ============================================================
# 6. INJEÇÃO DOS BOTÕES NO PLACEHOLDER
# ============================================================
with botoes_placeholder.container():
    if st.session_state.fase == "consulta" and len(st.session_state.messages) > 1:
        try:
            import pdf_generator
            import os  # Biblioteca para lidar com pastas e ficheiros
            # 1. Gera os bytes do PDF
            pdf_bytes = pdf_generator.gerar_pdf_triagem(st.session_state.dados, st.session_state.messages, st.session_state.get("nivel_urgencia", "Indeterminada"))
            nome_ficheiro = f"Relatorio_{st.session_state.dados.get('nome', 'Utente')}.pdf"
            
            # --- Salvar na pasta relatorios_triagem ---
            pasta_destino = "relatorios_triagem"
            os.makedirs(pasta_destino, exist_ok=True)  # Se a pasta não existir, o Python cria-a automaticamente
            caminho_completo = os.path.join(pasta_destino, nome_ficheiro)
            
            # Escreve o PDF diretamente na pasta local
            with open(caminho_completo, "wb") as f:
                f.write(pdf_bytes)
            # -----------------------------------------------------------
            
            # 2. Mantém o botão para tu fazeres o download se quiseres
            st.download_button("📄 Exportar Triagem em PDF", data=bytes(pdf_bytes), file_name=nome_ficheiro, mime="application/pdf", use_container_width=True)
            
        except Exception as e: st.error(f"Erro PDF: {e}")

    st.markdown("")
    if st.button("🔄 Nova Triagem", use_container_width=True):
        if len(st.session_state.messages) > 1:
            import json, os
            from datetime import datetime
            logs = []
            if os.path.exists("logs_triagem.json"):
                try:
                    with open("logs_triagem.json", "r", encoding="utf-8") as f: logs = json.load(f)
                except: pass
            logs.append({"timestamp": datetime.now().isoformat(), "doente": st.session_state.dados, "urgencia": st.session_state.get("nivel_urgencia", "Indeterminada"), "mensagens": st.session_state.messages})
            with open("logs_triagem.json", "w", encoding="utf-8") as f: json.dump(logs, f, indent=4, ensure_ascii=False)
                
        for key in ["messages", "fase", "dados", "triagem_resumo", "nivel_urgencia"]:
            if key in st.session_state: del st.session_state[key]
        st.session_state.switch_to_chat_tab = True
        st.rerun()

if st.session_state.get("switch_to_chat_tab"): 
    st.session_state.switch_to_chat_tab = False
    import streamlit.components.v1 as components
    components.html("""<script>setTimeout(function() { const tabs = window.parent.document.querySelectorAll('div[data-testid="stTabs"] button'); if (tabs.length > 0) { tabs[0].click(); } }, 100);</script>""", height=0)