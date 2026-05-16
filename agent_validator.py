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
    "falta de ar severa", "dificuldade respiratória", "perda de consciência",
    "desmaio", "convulsão", "convulsões", "sangue na tosse",
    "não consigo respirar", "inchaço da garganta", "língua inchada",
    "visão turva súbita", "paralisia", "perda de força",
    "febre acima de 40", "febre superior a 40",
]

# Frases que indicam que o LLM reconheceu a urgência (deve ter pelo menos uma)
RESPOSTAS_URGENCIA = [
    "112", "urgência", "urgencia", "emergência", "emergencia",
    "hospital", "socorro", "imediatamente", "ligar",
    "dirigir-se", "serviço de urgência", "servico de urgencia",
]


def validar_resposta_agente(resposta_llm, mensagem_utilizador=""):
    """
    Camada de Agentic AI: Avalia, sanitiza e corrige a resposta gerada 
    pelo LLM antes de a devolver ao utilizador final.
    
    Regras aplicadas:
    1. Bloqueio de prescrições ilegais (palavras proibidas)
    2. Verificação de coerência em urgências
    3. Obrigatoriedade do disclaimer
    4. Higiene de texto
    """
    resposta_sanitizada = resposta_llm

    # 1. VERIFICAÇÃO DE SEGURANÇA (Prevenção de prescrições ilegais)
    # Se o LLM alucinar e usar vocabulário médico perigoso, o Agente bloqueia a resposta.
    for palavra in PALAVRAS_PROIBIDAS:
        if palavra.lower() in resposta_sanitizada.lower():
            return (
                "**[Intervenção do Agente de Segurança]**\n"
                "Detetei que a resposta gerada poderia conter sugestões de automedicação "
                "arriscada ou diagnósticos definitivos que ultrapassam o meu âmbito.\n\n"
                "Para sua segurança, peço que **contacte imediatamente o SNS 24 (808 24 24 24)** "
                "ou dirija-se a um posto de saúde para avaliação presencial."
            )

    # 2. VERIFICAÇÃO DE COERÊNCIA EM URGÊNCIAS
    # Se o utilizador menciona sintomas de urgência mas o LLM não sugere ir ao hospital
    if mensagem_utilizador:
        utilizador_tem_urgencia = any(
            termo in mensagem_utilizador.lower() for termo in TERMOS_URGENCIA
        )
        llm_reconheceu_urgencia = any(
            resp in resposta_sanitizada.lower() for resp in RESPOSTAS_URGENCIA
        )
        
        if utilizador_tem_urgencia and not llm_reconheceu_urgencia:
            resposta_sanitizada += (
                "\n\n**[Nota de Segurança do Agente]**\n"
                "Os sintomas que descreveu podem indicar uma situação que requer "
                "avaliação médica urgente. Por favor, considere contactar o **112** "
                "ou dirigir-se ao **Serviço de Urgência** mais próximo."
            )

    # 3. VERIFICAÇÃO DE FORMATAÇÃO (Obrigatoriedade do Disclaimer)
    # Mesmo que o LLM se esqueça das regras do Modelfile, o Agente injeta o disclaimer.
    if DISCLAIMER_OBRIGATORIO not in resposta_sanitizada:
        resposta_sanitizada += f"\n\n---\n*{DISCLAIMER_OBRIGATORIO}*"

    # 4. HIGIENE DE TEXTO
    # Se o LLM começar a resposta com "Assistant:" ou "Bot:", limpamos isso para parecer mais natural
    resposta_sanitizada = re.sub(r'^(Assistant|Assistente|Bot):\s*', '', resposta_sanitizada, flags=re.IGNORECASE)

    return resposta_sanitizada.strip()


# Teste simples: Se correres este script diretamente, ele testa a lógica
if __name__ == "__main__":
    print("=" * 60)
    print("TESTES DO AGENTE VALIDADOR")
    print("=" * 60)
    
    # Teste 1: Alucinacao com prescricao
    teste_alucinacao = "Eu receito que tome amoxicilina para essas dores de garganta."
    print("\n[Teste 1] Alucinacao (prescricao):")
    print(validar_resposta_agente(teste_alucinacao))
    
    # Teste 2: Resposta segura
    teste_seguro = "Os seus sintomas sugerem uma constipacao. Beba muitos liquidos."
    print("\n[Teste 2] Resposta Segura:")
    print(validar_resposta_agente(teste_seguro))
    
    # Teste 3: Urgencia nao reconhecida pelo LLM
    teste_urgencia = "Pode ser uma inflamacao muscular. Descanse e tome paracetamol."
    msg_utilizador = "Tenho uma dor no peito forte que irradia para o braco esquerdo"
    print("\n[Teste 3] Urgencia nao reconhecida:")
    print(validar_resposta_agente(teste_urgencia, msg_utilizador))
    
    # Teste 4: Urgencia corretamente reconhecida
    teste_urgencia_ok = "Estes sintomas podem indicar um enfarte. Ligue imediatamente o 112 e dirija-se a urgencia."
    print("\n[Teste 4] Urgencia corretamente reconhecida:")
    print(validar_resposta_agente(teste_urgencia_ok, msg_utilizador))