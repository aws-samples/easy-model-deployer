import time
from emd.integrations.langchain_clients import SageMakerVllmEmbeddings
from emd.integrations.langchain_clients import SageMakerVllmRerank

embedding_model = SageMakerVllmEmbeddings(
    model_id="bge-m3",
    # model_tag='dev-2'
)


text = 'The giant panda (Ailuropoda melanoleuca), sometimes called a panda bear or simply panda, is a bear species endemic to China.'
t0 = time.time()
r1 = embedding_model.embed_query(text)
t1 = time.time()
embedding_model.embed_documents([text]*1000)
t2 = time.time()
print(f"embed_query: {t1-t0}")
print(f"embed_documents: {t2-t1}")


# docs = ["hi",'The giant panda (Ailuropoda melanoleuca), sometimes called a panda bear or simply panda, is a bear species endemic to China.']

# query = 'what is panda?'

# rerank_model = SageMakerVllmRerank(
#     model_id="bge-reranker-v2-m3"
# )

# print(rerank_model.rerank(query=query,documents=docs))
