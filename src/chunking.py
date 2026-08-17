import re
import json
from pathlib import Path
import pandas as pd

class chunking:
    def __init__(self, texto, chunk = 0, overlap = 0):
        '''Apresente o texto, a quantidade de elementos por divisões e, caso tenha, o overlap.'''
        self.texto = texto
        self.chunk = chunk
        self.overlap = overlap #garantir a sobreposição

        self.chunks_gen = []
        self.start = 0

    def fix_size(self, tipo):
        '''Se o tipo seja 1 o chunking será por tokens, caso contrário será por caracteres.'''
        self.tipo = tipo
        # reset
        self.chunks_gen = []
        self.start = 0

        if self.tipo == 1: #tokens 
            tokenization = self.texto.split() #tranformar em palavras

            while self.start < len(tokenization):
                end_texto = self.chunk + self.start
                chunk = tokenization[self.start:end_texto]
                self.chunks_gen.append(' '.join(chunk)) # join pois não quero uma lista de palavras para cada palavras, e sim listas com frases prontas separadas por espaço

                self.start = self.start + self.chunk - self.overlap 

        else: #caracteres
            while self.start < len(self.texto):
                    end_texto = self.chunk + self.start
                    self.chunks_gen.append(self.texto[self.start:end_texto])

                    self.start = self.start + self.chunk - self.overlap 

        return self.chunks_gen


    def structural(self, tipo):
        '''Se o tipo for 1 o chunking será por parágrafo, caso contrário será por final de sentenças'''
        self.tipo = tipo
        # reset
        self.chunks_gen = []
        self.start = 0

        if self.tipo == 1: #paragrafos 
            blocks = self.texto.split('\n\n') 
            
            self.chunks_gen = [b.strip() for b in blocks if b.strip()]# Limpa espaços extras ou linhas em branco residuais

        else: #senteças (. , ? !)
            sentence = re.split(r'(?<=[.!?])\s+', self.texto)

            self.chunks_gen = [s.strip() for s in sentence if s.strip()] # Limpa espaços extras ou linhas em branco residuais

        return self.chunks_gen



# --- Função para extrair dados do arquivo PEP ---
def extrair_pep(caminho_arquivo):
    with open(caminho_arquivo, 'r', encoding='utf-8', errors='ignore') as f:
        linhas = f.readlines()
        
    metadados = {}
    corpo_linhas = []
    em_cabecalho = True
    
    for linha in linhas:
        if em_cabecalho:
            if linha.strip() == '' or linha.startswith('..'):
                em_cabecalho = False
                continue
            match = re.match(r'^([A-Za-z\-]+):\s*(.*)$', linha)
            if match:
                chave, valor = match.groups()
                metadados[chave.lower()] = valor.strip()
            else:
                em_cabecalho = False
                corpo_linhas.append(linha)
        else:
            corpo_linhas.append(linha)

    return {
        'pep_numero': metadados.get('pep', caminho_arquivo.stem),
        'titulo': metadados.get('title', 'Sem título'),
        'status': metadados.get('status', 'Desconhecido'),
        'conteudo': ''.join(corpo_linhas).strip()
    }


# --- Função para salvar com json ---

def processar_e_salvar_chunks_json(
    diretorio_peps, 
    arquivo_saida_json="chunks_peps.json", 
    metodo="fix_size_tokens",
    tamanho_chunk=200, 
    overlap=30
):
    pasta = Path(diretorio_peps).resolve()
    lista_chunks = []

    if not pasta.exists():
        print(f"[ERRO] A pasta '{pasta}' não existe.")
        return pd.DataFrame(columns=['chunk_id', 'source', 'text'])

    extensoes_validas = ['.rst', '.txt', '.md']

    for arquivo in pasta.rglob('*'):
        if arquivo.is_file() and arquivo.suffix.lower() in extensoes_validas:
            
            pep_data = extrair_pep(arquivo)
            texto = pep_data['conteudo']
            
            if not texto.strip():
                continue

            # Instancia a sua classe chunking
            chunker = chunking(texto=texto, chunk=tamanho_chunk, overlap=overlap)
            
            # Seleciona o método de chunking
            if metodo == "fix_size_tokens":
                pedacos = chunker.fix_size(tipo=1)
            elif metodo == "fix_size_caracteres":
                pedacos = chunker.fix_size(tipo=2)
            elif metodo == "structural_paragrafos":
                pedacos = chunker.structural(tipo=1)
            elif metodo == "structural_sentencas":
                pedacos = chunker.structural(tipo=2)
            else:
                pedacos = chunker.fix_size(tipo=1)

            # Caminho relativo para a chave 'source'
            source_caminho = str(arquivo.relative_to(pasta.parent if pasta.parent != pasta else pasta))

            for idx, pedaco in enumerate(pedacos):
                chunk_obj = {
                    "chunk_id": f"pep_{pep_data['pep_numero']}_{idx+1:03d}",
                    "source": source_caminho,
                    "text": pedaco
                }
                lista_chunks.append(chunk_obj)

    if not lista_chunks:
        print("[AVISO] Nenhum chunk foi gerado. Verifique a pasta.")
        return pd.DataFrame(columns=['chunk_id', 'source', 'text'])

    # 1. Salva no arquivo JSON no formato especificado
    caminho_saida = Path(arquivo_saida_json)
    with open(caminho_saida, 'w', encoding='utf-8') as f:
        json.dump(lista_chunks, f, ensure_ascii=False, indent=4)

    print(f"Sucesso! {len(lista_chunks)} chunks foram salvos em: {caminho_saida.resolve()}")

RAIZ_PROJETO = Path(__file__).resolve().parent.parent


processar_e_salvar_chunks_json(
    diretorio_peps='data/raw/peps', 
    arquivo_saida_json='data/processed/chunks_peps.json',  # opcional: caminho do json
    metodo='fix_size_tokens',
    tamanho_chunk=200,
    overlap=30
)