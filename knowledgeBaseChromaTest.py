from typing import Any

import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings
from openai import OpenAI, embeddings

from datetime import datetime
import time

class MaoEmbeddingService(EmbeddingFunction):
    def __init__(self, *args: Any, **kwargs: Any):
        self.client = OpenAI(
            api_key="a",  # 你的API密钥
            # 如果使用自定义推理服务器，需要指定base_url
            base_url="http://127.0.0.1:11434/v1"
        )

    def __call__(self, texts: Documents) -> Embeddings:
        embeddings = []
        for t in texts:
            while True:
                try:
                    embedding = self.create_embedding(t)
                    embeddings.append(embedding)
                    break
                except Exception as e:
                    print("嵌入模型访问失败，重试中...")
                    time.sleep(0.2)
        return embeddings

    def create_embedding(self, text):
        data_embedding_res = self.client.embeddings.create(input=text, model="bge-m3:567m")
        return data_embedding_res.data[0].embedding

def main():
    embedding_service = MaoEmbeddingService()
    client = chromadb.HttpClient(host='127.0.0.1', port=8000)
    collection = client.get_or_create_collection("mao-collection", embedding_function=embedding_service)
    collection.add(
        documents=[f"hello world {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"],
        ids=[f"id1-{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"],
        metadatas=[{"xichang": 201, "beijing": "118.5"}]
    )


if __name__ == '__main__':
    main()
