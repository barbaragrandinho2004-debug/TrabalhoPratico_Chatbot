import json
import numpy as np
import faiss
import ollama

# Ficheiros onde vamos guardar o índice vetorial e os textos
FAISS_INDEX_FILE = "base_conhecimento.index"
CHUNKS_JSON_FILE = "chunks_texto.json"
MODELO_EMBEDDINGS = "nomic-embed-text"  # Modelo leve ideal para embeddings


def criar_base_vetorial(caminho_txt):
    """
    Lê o TXT médico, divide em chunks semânticos, cria os embeddings e guarda no FAISS.
    Cada linha do TXT corresponde a uma condição médica, com campos separados por '|'.
    Deve ser corrido apenas uma vez (ou quando o TXT for atualizado).
    """
    print("[1/4] A carregar o documento...")
    # Lê o ficheiro txt para ter menos ruído (sem logos, imagens, etc.)
    with open(caminho_txt, 'r', encoding='utf-8') as f:
        texto = f.read()

    print("[2/4] A dividir em chunks semânticos...")

    # O ficheiro tem uma condição médica por linha, com campos separados por '|':
    # Nome | Grupos de Risco | Sinais Vitais | Sintomas | Evolução | Contraindicações | Perguntas Triagem | Recomendações
    linhas = texto.strip().split('\n')
    linhas = [l.strip() for l in linhas if len(l.strip()) > 10]

    # Nomes dos campos para cada secção separada por '|'
    nomes_campos = [
        "Condição/Doença",
        "Grupos de Risco",
        "Sinais Vitais de Alerta",
        "Sintomas Principais",
        "Evolução / Quando Piorar",
        "Contraindicações",
        "Perguntas de Triagem",
        "Recomendações e Tratamento"
    ]

    chunks = []

    for linha in linhas:
        campos = [c.strip() for c in linha.split('|')]

        if len(campos) >= 2:
            # Extrair o nome da condição (primeiro campo)
            nome_condicao = campos[0] if campos else "Condição Desconhecida"

            # Chunk 1: Visão geral (condição + grupos de risco + sintomas)
            # Agrupa os campos mais relevantes para pesquisa por sintomas
            partes_sintomas = []
            for i, campo in enumerate(campos):
                if i < len(nomes_campos):
                    partes_sintomas.append(f"{nomes_campos[i]}: {campo}")
                else:
                    partes_sintomas.append(campo)

            chunk_completo = f"[{nome_condicao}]\n" + "\n".join(partes_sintomas)
            chunks.append(chunk_completo)

            # Chunk 2: Apenas sintomas e perguntas de triagem (para melhor match semântico)
            # Isto permite que a pesquisa por sintomas tenha maior precisão
            if len(campos) >= 7:
                chunk_triagem = (
                    f"[{nome_condicao} - Triagem]\n"
                    f"Sintomas: {campos[3] if len(campos) > 3 else ''}\n"
                    f"Perguntas de Triagem: {campos[6] if len(campos) > 6 else ''}\n"
                    f"Recomendações: {campos[7] if len(campos) > 7 else ''}"
                )
                chunks.append(chunk_triagem)

    print(f"[INFO] Total de chunks criados: {len(chunks)}")

    if not chunks:
        print("[ERRO] Nenhum chunk foi criado! Verifica o formato do ficheiro TXT.")
        return

    # Gerar o primeiro embedding para detetar automaticamente a dimensão do vetor
    print("[3/4] A detetar a dimensao dos embeddings...")
    resposta_teste = ollama.embed(model=MODELO_EMBEDDINGS, input=chunks[0])
    dimensao_vetor = len(resposta_teste.embeddings[0])
    print(f"      Dimensao detetada: {dimensao_vetor}")

    # Inicializa o FAISS (usando a distância L2)
    index = faiss.IndexFlatL2(dimensao_vetor)
    documentos_originais = []

    print("[4/4] A gerar embeddings e a guardar na base de dados vetorial...")
    # Passar os chunks para vetores
    for i, chunk in enumerate(chunks):
        try:
            resposta = ollama.embed(model=MODELO_EMBEDDINGS, input=chunk)
            embedding = np.array([resposta.embeddings[0]], dtype='float32')

            index.add(embedding)
            documentos_originais.append({"id": i, "texto": chunk})
            print(f"      [OK] Chunk {i+1}/{len(chunks)} processado")
        except Exception as e:
            print(f"      [ERRO] Chunk {i}: {e}")

    # Guardar o índice FAISS e o JSON com os textos correspondentes
    faiss.write_index(index, FAISS_INDEX_FILE)
    with open(CHUNKS_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(documentos_originais, f, ensure_ascii=False, indent=4)

    print(f"\n[SUCESSO] Motor RAG criado com sucesso!")
    print(f"   Indice FAISS: {FAISS_INDEX_FILE}")
    print(f"   Chunks JSON: {CHUNKS_JSON_FILE}")
    print(f"   Total de vetores indexados: {index.ntotal}")


def pesquisar_no_rag(pergunta_utilizador, k=3):
    """
    Recebe a pergunta do utilizador, vetoriza e procura os K chunks mais relevantes no FAISS.
    Retorna o contexto médico recuperado ou string vazia se não encontrar.
    """
    try:
        # Carregar a base de dados vetorial e os textos originais
        index = faiss.read_index(FAISS_INDEX_FILE)
        with open(CHUNKS_JSON_FILE, "r", encoding="utf-8") as f:
            documentos = json.load(f)
    except Exception:
        return "⚠️ Base de dados RAG não encontrada. Execute primeiro: python rag_engine.py"

    if index.ntotal == 0:
        return "⚠️ A base de dados RAG está vazia. Execute primeiro: python rag_engine.py"

    # A pergunta também é enviada e passada para vetor
    resposta = ollama.embed(model=MODELO_EMBEDDINGS, input=pergunta_utilizador)
    embedding_pergunta = np.array([resposta.embeddings[0]], dtype='float32')

    # É calculada a semelhança/proximidade entre os pontos vetoriais
    # Limita k ao número real de documentos para evitar erros
    k_real = min(k, index.ntotal)
    distancias, indices = index.search(embedding_pergunta, k_real)

    # São selecionados os chunks mais importantes para responder à pergunta
    contexto_recuperado = ""
    for idx, i in enumerate(indices[0]):
        if i != -1 and i < len(documentos):  # -1 significa que o FAISS não encontrou resultados suficientes
            # Adiciona a distância para referência (menor = mais relevante)
            contexto_recuperado += f"--- Documento {idx+1} (relevância: {distancias[0][idx]:.2f}) ---\n"
            contexto_recuperado += documentos[i]["texto"] + "\n\n"

    return contexto_recuperado


# Se correres este script diretamente, ele recria a base de dados.
if __name__ == "__main__":
    criar_base_vetorial("docs/triagem_saude24.txt")