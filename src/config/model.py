from sentence_transformers import SentenceTransformer

model = SentenceTransformer('BAAI/bge-small-en-v1.5') # as consultas precisam estar em ingles para manter a perfomance
# model = SentenceTransformer('intfloat/multilingual-e5-small') # multi idiomas