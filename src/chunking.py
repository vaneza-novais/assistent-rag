import re

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