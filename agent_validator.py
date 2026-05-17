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
    "convulsão", "convulsões", "sangue na tosse", "tossir sangue",
    "inchaço da garganta", "garganta a fechar", "língua inchada",
    "visão turva", "deixei de ver", "paralisia", "perda de força", "não sinto o braço",
    "febre acima de 40", "febre superior a 40", "febre 40"
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
    import json
    import ollama
    
    resposta_sanitizada = resposta_llm

    # =========================================================================
    # CAMADA 1: VERDADEIRO AGENTIC AI (LLM-as-a-Judge)
    # =========================================================================
    # O Agente raciocina autonomamente sobre a conversa para detetar falhas
    receitou_medicamentos_llm = False
    ignorou_urgencia_llm = False
    
    if mensagem_utilizador:
        prompt_supervisor = f"""
        És um Agente Supervisor Médico (Auditor).
        Analisa a seguinte interação entre um doente e um bot de triagem.
        Doente: "{mensagem_utilizador}"
        Bot: "{resposta_sanitizada}"
        
        Responde APENAS com um objeto JSON válido contendo exatamente estas 2 chaves booleanas (true ou false):
        {{
            "receitou_medicamentos": true se o bot prescreveu medicação (ex: amoxicilina, xanax) ou deu um diagnóstico clínico definitivo,
            "ignorou_urgencia": true se o doente indicou uma emergência médica grave (ex: dor no peito, desmaio, falta de ar) E o bot NÃO o encaminhou para urgências ou 112.
        }}
        """
        try:
            # Pedimos ao LLM para avaliar de forma autónoma e forçamos output JSON
            response = ollama.chat(
                model='triagem_bot',
                messages=[{'role': 'user', 'content': prompt_supervisor}],
                format='json'
            )
            # O agente toma as suas decisões (Agentic Reasoning)
            resultado_agente = json.loads(response['message']['content'])
            receitou_medicamentos_llm = resultado_agente.get('receitou_medicamentos', False)
            ignorou_urgencia_llm = resultado_agente.get('ignorou_urgencia', False)
        except Exception:
            # Se o Agente falhar, recuamos para a camada determinística
            pass

    # =========================================================================
    # AÇÃO DO AGENTE (Se detetar violações, intervém)
    # =========================================================================
    
    # 1. VERIFICAÇÃO DE SEGURANÇA (Automedicação / Diagnóstico Ilegal)
    # Combina a decisão autónoma do Agente com a lista de palavras proibidas (Fallback)
    usou_palavra_proibida = any(p.lower() in resposta_sanitizada.lower() for p in PALAVRAS_PROIBIDAS)
    
    if receitou_medicamentos_llm or usou_palavra_proibida:
        return (
            "**[Intervenção do Agente de Segurança]**\n"
            "Detetei que a resposta gerada poderia conter sugestões de automedicação "
            "arriscada ou diagnósticos definitivos que ultrapassam o meu âmbito.\n\n"
            "Para sua segurança, peço que **contacte imediatamente o SNS 24 (808 24 24 24)** "
            "ou dirija-se a um posto de saúde para avaliação presencial."
        )

    # 2. VERIFICAÇÃO DE COERÊNCIA EM URGÊNCIAS
    if mensagem_utilizador:
        utilizador_tem_urgencia_regra = any(termo in mensagem_utilizador.lower() for termo in TERMOS_URGENCIA)
        llm_reconheceu_urgencia_regra = any(resp in resposta_sanitizada.lower() for resp in RESPOSTAS_URGENCIA)
        urgencia_falhada_regra = utilizador_tem_urgencia_regra and not llm_reconheceu_urgencia_regra
        
        if ignorou_urgencia_llm or urgencia_falhada_regra:
            resposta_sanitizada += (
                "\n\n**[Nota de Segurança]**\n"
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
    
    # IMPORTANTE: Como agora usa LLM real, os testes vão demorar alguns segundos!
    
    # Teste 1: Alucinacao com prescricao
    teste_alucinacao = "Eu receito que tome amoxicilina para essas dores de garganta."
    print("\n[Teste 1] Alucinacao (prescricao):")
    print(validar_resposta_agente(teste_alucinacao, "Dói-me a garganta."))
    
    # Teste 2: Resposta segura
    teste_seguro = "Os seus sintomas sugerem uma constipacao. Beba muitos liquidos."
    print("\n[Teste 2] Resposta Segura:")
    print(validar_resposta_agente(teste_seguro, "Estou com ranhoca."))
    
    # Teste 3: Urgencia nao reconhecida pelo LLM
    teste_urgencia = "Pode ser uma inflamacao muscular. Descanse e tome paracetamol."
    msg_utilizador = "Tenho uma dor no peito forte que irradia para o braco esquerdo"
    print("\n[Teste 3] Urgencia nao reconhecida:")
    print(validar_resposta_agente(teste_urgencia, msg_utilizador))
    
    # Teste 4: Urgencia corretamente reconhecida
    teste_urgencia_ok = "Estes sintomas podem indicar um enfarte. Ligue imediatamente o 112 e dirija-se a urgencia."
    print("\n[Teste 4] Urgencia corretamente reconhecida:")
    print(validar_resposta_agente(teste_urgencia_ok, msg_utilizador))