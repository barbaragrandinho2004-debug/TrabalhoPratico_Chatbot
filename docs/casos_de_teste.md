# 🧪 Casos de Teste para o Chatbot de Triagem Médica

Para povoares o teu dashboard com cores bonitas (Verde, Amarelo, Vermelho) e testares os modelos rigorosamente para o teu relatório, usa os seguintes **3 Cenários de Teste**. 

Deves fazer cada um destes testes duas vezes: uma vez com o modelo `gemma3:4b` e outra com o `llama3.2:3b`, tirando prints para o teu relatório.

---

### 🔴 Caso 1: Emergência (Grau Vermelho)
*Este caso deve forçar o bot a mandar o paciente ligar para o 112 imediatamente, ativando as barreiras de segurança do `agent_validator.py`.*

**Identificação:** "Olá, o meu nome é Carlos, tenho 68 anos e sou homem."
**Sintomas (Prompt):**
> "Estou com uma dor muito forte no centro do peito que começou há cerca de meia hora. Sinto também que o meu braço esquerdo está dormente e estou com muita falta de ar e a suar frio."
**Resultado Esperado:** O chatbot deve interromper imediatamente as perguntas de diagnóstico e instruir o Carlos a ligar para o 112 (Emergência Médica) devido a suspeita de EAM (Enfarte Agudo do Miocárdio).

---

### 🟡 Caso 2: Em Avaliação / Cuidados Primários (Grau Amarelo)
*Este caso foca-se na extração de informação detalhada usando RAG (sintomas agudos, mas não vida-ou-morte).*

**Identificação:** "Sou a Maria, tenho 32 anos e identifico-me como mulher."
**Sintomas (Prompt):**
> "Estou com febre de 39 graus desde ontem à noite. Tenho muita tosse seca, dores no corpo todo e a minha garganta parece que tem vidro quando engulo."
**Resultado Esperado:** O bot deve fazer perguntas adicionais de triagem (ex: "Tem dificuldade em respirar?", "Tomou alguma medicação para baixar a febre?") e depois aconselhar o contacto com a Linha SNS24 (808 24 24 24) ou marcação de consulta no Centro de Saúde.

---

### 🟢 Caso 3: Risco Baixo / Autocuidados (Grau Verde)
*O bot deve usar um tom calmo, educativo e sugerir alívio sintomático em casa.*

**Identificação:** "Chamo-me Pedro, sou rapaz e tenho 21 anos."
**Sintomas (Prompt):**
> "Fui jogar futebol ontem à noite e agora tenho uma dor ligeira na barriga da perna direita. Não está inchado nem roxo, mas dói quando apoio o pé no chão com força."
**Resultado Esperado:** O bot deve tranquilizar o Pedro, classificar como dor muscular ligeira (possível contratura), e sugerir repouso, aplicação de gelo local, e reavaliação se não melhorar em alguns dias.

---

## 🧠 Como testar o Few-Shot Prompting (Para o Relatório)

O teu professor quer ver se tu entendes o conceito de "Few-Shot Prompting" (dar exemplos ao modelo dentro do *prompt* de sistema para que ele aprenda o formato desejado).

Para testares isto, primeiro corres um teste com o teu `modelfile.txt` atual (Zero-Shot).
Depois, modificas o teu ficheiro `modelfile.txt` e adicionas a secção de **EXEMPLOS** no final da instrução `SYSTEM`. Fica assim:

```dockerfile
FROM gemma3:4b
PARAMETER temperature 0.1
PARAMETER num_ctx 4096

SYSTEM """
És um assistente virtual de triagem médica inspirado na Linha Saúde 24 (Portugal).
Deves ser extremamente empático, conciso e responsável.

[... O resto das tuas instruções originais ...]

---
EXEMPLOS DE INTERAÇÕES IDEAIS (FEW-SHOT):

Exemplo 1 (Emergência):
Doente: Tenho uma dor esmagadora no peito e falta de ar.
Tu: Avaliei os seus sintomas. Esta é uma situação de alerta máxima. Por favor, pare o que está a fazer e ligue imediatamente para o 112 (Emergência Médica). Não conduza até ao hospital.

Exemplo 2 (Pouca Informação):
Doente: Dói-me a cabeça.
Tu: Lamento saber que não se sente bem. Para o poder ajudar corretamente, há quanto tempo começou a dor de cabeça? É a primeira vez que sente uma dor com esta intensidade ou costuma ter enxaquecas?

Exemplo 3 (Risco Baixo):
Doente: Queimei um bocadinho o dedo no forno, ficou vermelho mas não tem bolha.
Tu: Entendo. Como é uma queimadura superficial e sem bolha, deve arrefecer a área com água corrente natural (não gelada) durante cerca de 10 a 15 minutos. Se a dor persistir, pode aplicar um creme calmante ou hidratante.
"""
```

### O que observar para o teu relatório:
1. **Velocidade (Tokens/segundo):** Podes verificar se o Llama3.2 é mais rápido a gerar texto que o Gemma3 (ou vice-versa).
2. **Consistência:** Vê se com o *Few-Shot Prompting* (com os exemplos lá colocados), o modelo pára de "inventar" conselhos estranhos e adota o tom de voz profissional idêntico ao dos teus exemplos.
3. **Respeito pelo RAG:** Compara se o Llama ou o Gemma segue melhor a informação que lhe passas dos documentos PDFs da DGS.
