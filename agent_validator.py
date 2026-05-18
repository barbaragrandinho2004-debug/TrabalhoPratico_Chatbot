import re

# O disclaimer exato que definimos no Modelfile
DISCLAIMER_OBRIGATORIO = "Isto não substitui uma consulta com um médico ou profissional de saúde. Para orientações clínicas específicas, consulte um especialista ou contacte o SNS 24 (808 24 24 24)."

# Lista de palavras ou expressões que um bot de triagem NUNCA deve usar
PALAVRAS_PROIBIDAS = [
    "receito", "prescrevo", "tome o antibiótico", "você tem definitivamente",
    "o seu diagnóstico é", "com certeza você tem", "tome xanax",
    "tome diazepam", "tome victan", "amoxicilina",
    "receitar", "prescrever", "diagnóstico definitivo",
    "tome alprazolam", "tome lorazepam", "tome clonazepam",
    "tome morfina", "tome tramadol", "tome codeína",
]

# Palavras-chave que indicam urgência médica — o agente verifica se o LLM as reconheceu
TERMOS_URGENCIA = [
    "dor no peito", "dor torácica", "irradiar para o braço",
    "falta de ar", "falta de ar severa", "dificuldade respiratória",
    "dificuldade em respirar", "dificuldade a respirar", "custa a respirar", "custa-me a respirar",
    "não consigo respirar", "não consigo encher os pulmões",
    "perda de consciência", "desmaio", "desmaiei",
    "convulsão", "convulsões", "sangue na tosse", "tossir sangue", "tossi sangue", "cuspi sangue",
    "inchaço da garganta", "garganta a fechar", "língua inchada",
    "visão turva", "deixei de ver", "paralisia", "perda de força", "não sinto o braço",
    "febre acima de 40", "febre superior a 40", "febre 40"
]


def contem_urgencia(texto):
    """
    Deteta urgência ignorando falsos positivos de negação.
    Ex: 'Não tenho dor no peito' não ativa o alerta.
    """
    # Remove qualquer frase que comece por "não", "sem" ou "nega" até à próxima pontuação
    texto_limpo = re.sub(r'\b(não|nao|sem|nega)\b.*?(?=[,.;\n]|$)', '', texto.lower())
    return any(termo in texto_limpo for termo in TERMOS_URGENCIA)

def validar_resposta_agente(resposta_llm, mensagem_utilizador=""):

    resposta_sanitizada = resposta_llm

    # Limpeza Inicial
    resposta_sanitizada = re.sub(r'^(Assistant|Assistente|Bot):\s*', '', resposta_sanitizada, flags=re.IGNORECASE)
    # Corta o disclaimer e TODO o lixo introdutório que esteja na mesma frase ("Lembre-se", "Atenção:")
    # Ele recua até encontrar o ponto final da frase anterior ou o parágrafo anterior e apaga tudo a partir daí.
    resposta_sanitizada = re.sub(r'(?is)(?:(?<=[.!?\n])|^)\s*[^\n.!?]*?isto não substitui uma consulta.*$', '', resposta_sanitizada).strip()

    # 1. Barreira Determinística de Medicamentos
    if any(p in resposta_sanitizada.lower() for p in PALAVRAS_PROIBIDAS):
        return (
            "**[Intervenção do Agente de Segurança]**\n"
            "Detetei que a resposta gerada poderia conter sugestões de automedicação "
            "arriscada ou diagnósticos definitivos que ultrapassam o meu âmbito.\n\n"
            "Para sua segurança, peço que **contacte imediatamente o SNS 24 (808 24 24 24)** "
            "ou dirija-se a um posto de saúde para avaliação presencial."
        )

    # 2. Barreira Determinística de Urgência (Só atua se o Python detetar perigo real)
    if mensagem_utilizador and contem_urgencia(mensagem_utilizador):
        bot_encaminhou = any(r in resposta_sanitizada.lower() for r in ["112", "urgência", "emergência", "hospital", "socorro"])
        # Se o doente tem emergência e o bot não avisou, o Python corrige!
        if not bot_encaminhou:
            resposta_sanitizada += (
                "\n\n**[Nota de Segurança]**\n"
                "Os sintomas que descreveu podem indicar uma situação que requer "
                "avaliação médica urgente. Por favor, considere contactar o **112** "
                "ou dirigir-se ao **Serviço de Urgência** mais próximo."
            )
            

    # 3. Formatação Final e Limpeza Profunda
    
    # 1. Limpar linhas que SÓ têm lixo (ex: asteriscos ou hífens sozinhos numa linha)
    resposta_sanitizada = re.sub(r'(?m)^\s*[-•*]+\s*$', '', resposta_sanitizada)
    
    # 2. A tua ideia: Limpar "**" perdidos no final absoluto do texto, 
    # MAS apenas se estiverem isolados (ou seja, têm um espaço antes, não estragando o negrito de uma palavra)
    resposta_sanitizada = re.sub(r'(\s|^)[-•*]+\s*$', '', resposta_sanitizada)
    
    # Remove as linhas separadoras longas geradas pelo bot
    resposta_sanitizada = re.sub(r'(?m)^-{3,}$', '', resposta_sanitizada)
    
    # Adiciona a NOSSA única linha separadora e o Disclaimer
    resposta_sanitizada = resposta_sanitizada.strip()
    resposta_sanitizada += f"\n\n---\n*{DISCLAIMER_OBRIGATORIO}*"

    return resposta_sanitizada