from fpdf import FPDF
from datetime import datetime

def limpar_texto_para_pdf(texto):
    if not texto:
        return ""
    # 1. Resolve o teu erro: Substitui os travessões longos por hífens normais
    texto = texto.replace("–", "-").replace("—", "-")
    
    # 2. Limpa aspas curvas e apóstrofos especiais do LLM
    texto = texto.replace("“", '"').replace("”", '"')
    texto = texto.replace("‘", "'").replace("’", "'")
    
    # 3. Força a codificação segura para a fonte Helvetica não quebrar com acentos portugueses
    return texto.encode('latin-1', 'replace').decode('latin-1')

def gerar_pdf_triagem(dados, mensagens, urgencia):
    """
    Gera um relatório de triagem em formato PDF.
    Retorna os bytes do PDF gerado.
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Configurações de página e fontes
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Título do Documento (Limpo com a nossa função)
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(0, 102, 102) # Cor principal do projeto
    pdf.cell(0, 10, limpar_texto_para_pdf("Relatório de Triagem Médica"), align="C", ln=True)
    pdf.set_font("helvetica", "I", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, f"Gerado a: {datetime.now().strftime('%d/%m/%Y %H:%M')}", align="C", ln=True)
    pdf.ln(5)
    
    # Seção: Dados do Doente
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, limpar_texto_para_pdf("Ficha do Doente"), ln=True, border="B")
    pdf.set_font("helvetica", "", 11)
    
    nome = dados.get("nome", "Não informado")
    identificacao = dados.get("nome_idade", "Não informada")
    genero = dados.get("genero", "Não informado")
    queixa = dados.get("queixa", "Não informada")
    
    pdf.ln(3)
    pdf.cell(40, 8, limpar_texto_para_pdf("Identificação:"), border=0)
    pdf.cell(0, 8, limpar_texto_para_pdf(identificacao), ln=True)
    pdf.cell(40, 8, limpar_texto_para_pdf("Género:"), border=0)
    pdf.cell(0, 8, limpar_texto_para_pdf(genero.capitalize()), ln=True)
    
    # Estado de Urgência
    pdf.cell(40, 8, limpar_texto_para_pdf("Nível de Risco:"), border=0)
    if urgencia == "Vermelho":
        pdf.set_text_color(220, 53, 69) # Vermelho
        pdf.cell(0, 8, limpar_texto_para_pdf("EMERGÊNCIA"), ln=True)
    elif urgencia == "Amarelo":
        pdf.set_text_color(255, 193, 7) # Amarelo
        pdf.cell(0, 8, limpar_texto_para_pdf("Avaliação"), ln=True)
    else:
        pdf.set_text_color(40, 167, 69) # Verde
        pdf.cell(0, 8, limpar_texto_para_pdf("Risco Baixo"), ln=True)
        
    pdf.set_text_color(0, 0, 0)
    
    pdf.ln(5)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 8, limpar_texto_para_pdf("Queixa Principal:"), ln=True)
    pdf.set_font("helvetica", "", 11)
    pdf.multi_cell(0, 8, limpar_texto_para_pdf(queixa))
    
    pdf.ln(10)
    
    # Seção: Histórico Clínico (Conversa)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, limpar_texto_para_pdf("Histórico Clínico (Registo de Conversa)"), ln=True, border="B")
    pdf.ln(3)
    
    for msg in mensagens:
        role = msg["role"]
        content = msg["content"]
        
        # Ignorar o disclaimer automático longo na versão PDF para ficar mais limpo
        content = content.replace("Isto não substitui uma consulta com um médico ou profissional de saúde. Para orientações clínicas específicas, consulte um especialista ou contacte o SNS 24 (808 24 24 24).", "")
        
        # Limpar formatações Markdown básicas (* e **)
        content = content.replace("**", "").replace("*", "")
        
        # Aplicar a limpeza de caracteres e acentos antes de desenhar no PDF
        content_seguro = limpar_texto_para_pdf(content.strip())
        
        if role == "user":
            pdf.set_font("helvetica", "B", 10)
            pdf.set_text_color(0, 102, 102)
            pdf.cell(0, 6, limpar_texto_para_pdf("Doente:"), ln=True)
            pdf.set_font("helvetica", "", 10)
            pdf.set_text_color(50, 50, 50)
        else:
            pdf.set_font("helvetica", "B", 10)
            pdf.set_text_color(220, 53, 69) if "[Nota de Segurança]" in content else pdf.set_text_color(22, 160, 133)
            pdf.cell(0, 6, limpar_texto_para_pdf("Assistente de Triagem:"), ln=True)
            pdf.set_font("helvetica", "", 10)
            pdf.set_text_color(50, 50, 50)
            
        pdf.multi_cell(0, 6, content_seguro)
        pdf.ln(4)
        
    # Retornar como bytes
    return bytes(pdf.output())