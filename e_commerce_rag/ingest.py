import os
import pandas as pd
import uuid

from qdrant_client import QdrantClient, models



qdrant_client = QdrantClient("http://qdrant:6333")
model_handle = "jinaai/jina-embeddings-v2-small-en"

def load_index():

    url = "https://raw.githubusercontent.com/imsoumya18/E-commerce_FAQ/main/Ecommerce_FAQs.csv"
    df_faq = pd.read_csv(url).reset_index().rename(columns={'index': 'id'})
    documents = df_faq.to_dict(orient='records')


    EMBEDDING_DIMENSIONALITY = 512
    collection_name = "project-sparse-and-dense"
    #collection_name = "project"

    # ✅ hybrid search
    # ✅ Check if collection already exists
    try:
        qdrant_client.get_collection(collection_name)
        print(f"Collection `{collection_name}` already exists. Skipping creation.")
    except Exception:
        qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    # Named dense vector for jinaai/jina-embeddings-v2-small-en
                    "jina-small": models.VectorParams(
                        size=512,
                        distance=models.Distance.COSINE,
                    ),
                },
                sparse_vectors_config={
                    "bm25": models.SparseVectorParams(
                        modifier=models.Modifier.IDF,
                    )
                }
            )

        # ✅ Only upsert documents if creating for the first time
        qdrant_client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=uuid.uuid4().hex,
                    vector={
                        "jina-small": models.Document(
                            text=doc['response'],
                            model="jinaai/jina-embeddings-v2-small-en",
                        ),
                        "bm25": models.Document(
                            text=doc['response'], 
                            model="Qdrant/bm25",
                        ),
                    },
                    payload={
                        "prompt": doc['prompt'],
                        "response": doc['response'],
                        "id": uuid.uuid4().hex
                    }
                )
                for doc in documents
            ]
        )
        print(f"Inserted {len(documents)} documents into `{collection_name}`.")