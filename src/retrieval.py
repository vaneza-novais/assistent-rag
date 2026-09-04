from sentence_transformers import SentenceTransformer
import json
import numpy as np
import os
import faiss

path = '../data/processed/chunks_peps.json'
outpath_embeddings = '../data/processed/embeddings_peps.npy'
caminho_json = "../data/processed/chunks_peps.json" # Ler o arquivo JSON

# Definir o modelo 
model = SentenceTransformer('BAAI/bge-small-en-v1.5') # as consultas precisam estar em ingles para manter a perfomance

with open(caminho_json, 'r', encoding='utf-8') as f:
    chunks = json.load(f)

# Extrair apenas o texto de cada chunk para uma lista
textos = [chunk['text'] for chunk in chunks]

if os.path.exists(outpath_embeddings):
    # Se o arquivo .npy já existe, carrega do disco em milissegundos
    embeddings = np.load(outpath_embeddings)
    print("✅ Embeddings existentes carregados com sucesso!")

else:
    # Se não existe, inicializa o modelo e gera os embeddings
    print("⚡ Gerando embeddings (arquivo não encontrado)...")

    embeddings = model.encode(
        textos, 
        show_progress_bar=True
    )
    
    # Salva na pasta ../data/processed/
    np.save(outpath_embeddings, embeddings)
    print("✅ Embeddings gerados e salvos com sucesso!")

class busca:
    def __init__(self, model, vetor, k, xq):
        '''Indique o embendding, modelo, a quantidade de caracteres correspondente e também a query'''
        self.model = model
        self.vetor = np.ascontiguousarray(vetor, dtype=np.float32) # Garante que os vetores estejam no formato float32 que o FAISS exige
        self.k = k
        
        #garantir que o vetor da query seja float32
        vetor_query = model.encode([xq]) 
        self.xq = np.ascontiguousarray(vetor_query, dtype=np.float32)

        self.d = self.vetor.shape[1]
        # self.index = None # armazenar o indice

        self.nlist = 50  # defini a quantiade de celulas a dividir toda base de embendding
        self.m = 8 # quantidade de sub vetores
        self.bits = 8 # quantidade de bits para guardar

    def treino(self, index): # verificar se está treinado
        self.index = index

        if self.index.is_trained:
            pass
        else:
            index.train(self.vetor)  

        return index

    def retorno(self, index):
        index = self.treino(index)      
        index.add(self.vetor)
        self.index = index
        
        D, I = index.search(self.xq, self.k)  # busca
        print(I)

        return I

    def metrica(self, tipo):
        '''Indique o tipo de busca: 1 para IndexFlatL2, 2 para XXXX e 3 para YYYY'''
        self.tipo = tipo

        if self.tipo == 1: #IndexFlatL2
            index = faiss.IndexFlatL2(self.d)

            return self.retorno(index)

        elif self.tipo == 2: #IndexIVFFlat
            self.quantificador = faiss.IndexFlatL2(self.d) # mapeear e indentificar qual celula o vetor esta

            index = faiss.IndexIVFFlat(
                self.quantificador, #
                self.d, 
                self.nlist
            )

            return self.retorno(index)

        elif self.tipo == 3: #IndexIVFPQ
            self.quantificador = faiss.IndexFlatL2(self.d) # mapeear e indentificar qual celula o vetor esta

            index = faiss.IndexIVFPQ(
                self.quantificador, 
                self.d, 
                self.nlist, # quantidade de divisao
                self.m, # quantidade de sub vetores
                self.bits # quantidade de bits para guardar
            ) 

            return self.retorno(index)

        else:
           print('Indicar a métrica é obrigatório')
           return None

if __name__ == "__main__":
    while True:
        pergunta = input("\nPergunta (ou 'sair' para encerrar): ")
        if pergunta.lower() == "sair":
            break

        buscador = busca(model=model, vetor=embeddings, k=5, xq=pergunta)
        indices = buscador.metrica(tipo=1)  # 1 = IndexFlatL2

        chunks_encontrados = [chunks[i] for i in indices[0]]
        for c in chunks_encontrados:
            print(f"\n---\n{c['text'][:300]}...")