from weaviate.util import generate_uuid5
from weaviate import classes as wvc
import weaviate

import sys
import os

from rich.console import Console
console = Console()

class Weaviate:
        def __init__(self, collection_name):
            self.collection_name = collection_name
            self.client = self.create_client()

        def create_client(self):
            client = weaviate.connect_to_custom(
                http_host=os.getenv("WEAVIATE_HOST"),
                http_port=os.getenv("WEAVIATE_HTTP_PORT"),
                http_secure=False,
                grpc_host=os.getenv("WEAVIATE_HOST"),
                grpc_port=os.getenv("WEAVIATE_GRPC_PORT"),
                grpc_secure=False,
            )
            return client

        def init_conn(self):
            console.log('Connecting to Weaviate')
            if not self.client.collections.exists(self.collection_name):
                self.client.collections.delete(self.collection_name)
                self.client.collections.create(
                    name=self.collection_name,
                    vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_ollama(
                        api_endpoint=os.getenv("VECTORIZER_HOST"), 
                        model=os.getenv("VECTORIZER_MODEL")
                    ),
                    generative_config=wvc.config.Configure.Generative.ollama(
                        api_endpoint=os.getenv("GENERATIVE_HOST"), 
                        model=os.getenv("GENERATIVE_MODEL")
                    ),
                    properties=[
                    wvc.config.Property(
                        name="page_content",
                        data_type=wvc.config.DataType.TEXT
                    ),
                    wvc.config.Property(
                        name="metadata",
                        data_type=wvc.config.DataType.TEXT,
                        skip_vectorization=True
                    ),
                    wvc.config.Property(
                        name="document_id",
                        data_type=wvc.config.DataType.TEXT,
                        skip_vectorization=True
                    ),
                    ]
                )
            index = self.client.collections.get(self.collection_name)
            console.log(f'Weaviate Connected: {self.collection_name}')

            return index
        

class WeaviateRepository:
    def __init__(self, documents, collection_name):
        self.doc = documents
        self.collection_name = collection_name
        self.weaviate_config = Weaviate(collection_name)
        self.index = self.determine_connection()
        self.client = self.weaviate_config.client

    def determine_connection(self):
        index = self.weaviate_config.init_conn()
        return index

    def _store_vector(self):
        collections = self.client.collections.get(self.collection_name)
        try:
            for i, d in enumerate(self.doc):
                uuid = generate_uuid5(d['document_id'] + '_' + str(i))
                d["metadata"] = str(d["metadata"])
                try:
                    collections.data.insert(properties=d, uuid=uuid)
                except Exception as insert_error:
                    if "already exists" in str(insert_error):
                        collections.data.replace(
                            properties=d,
                            uuid=uuid
                        )
                        console.log(f"Replaced existing document: {uuid}")
                    else:
                        raise insert_error
        except Exception as e:
            _, _, exc_tb = sys.exc_info()
            message = f"error {e} at {exc_tb.tb_lineno}, vector store upsert failed"
            print(message)
        finally:
            self.client.close()
 
    def upsert_docs(self):
        """
        Upsert function
        """
        try:
            self._store_vector()
        except Exception as e:
            _, _, exc_tb = sys.exc_info()
            message = f"error {e} at {exc_tb.tb_lineno}, upsert failed"
            print(message)
