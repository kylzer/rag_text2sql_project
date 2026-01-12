from model import VectorInput, VectorMetadata, Summary, Keywords
from utils import langchainInvoke
from indexing.prompt import (SUMMARIZATION_SYSTEM_PROMPT, SUMMARIZATION_USER_PROMPT,
                             KEYWORDS_SYSTEM_PROMPT, KEYWORDS_USER_PROMPT)

from database import WeaviateRepository

from rich.console import Console
console = Console()
class Upserter:
    def __init__(self, doc_id, fileName, collection, chunkedDocs, n_chunk):
        self.doc_id = doc_id
        self.fileName = fileName
        self.collection = collection
        self.chunkedDocs = chunkedDocs
        self.n_chunk = n_chunk

    def _extract_keywords(self, combined_content):
        keywords = langchainInvoke(KEYWORDS_SYSTEM_PROMPT, KEYWORDS_USER_PROMPT, {'text':combined_content}, Keywords)
        if keywords == False:
            return {"keywords": [], "entities": [], "questions": []} 
        return keywords.__dict__

    def _generate_summary(self, combined_content):
        summary = langchainInvoke(SUMMARIZATION_SYSTEM_PROMPT, SUMMARIZATION_USER_PROMPT, {'text':combined_content}, Summary)
        if summary == False:
            return "Error generating summary"
        print(summary)
        return summary.summary

    def _document_formatter(self, content, keywords_dict, summary):
        keywords = keywords_dict['keywords']
        entities = keywords_dict['entities']
        questionHyp = keywords_dict['questions']

        document = VectorInput(
            document_id=self.doc_id,
            page_content=content,
            summary=summary,
            keywords=keywords,
            entities=entities,
            questions=questionHyp,
            filename=self.fileName
        )
        
        # Convert to dict for Weaviate
        return document.__dict__

    def _restructure(self):
        restructured_chunks = []
        print(f"Total Chunk : {len(self.chunkedDocs)}")

        for i in range(0, len(self.chunkedDocs), self.n_chunk):
            chunk_group = self.chunkedDocs[i:i + self.n_chunk]      
            combined_content = " ".join([chunk.text for chunk in chunk_group])
            
            print("Get Keywords!")
            keywords = self._extract_keywords(combined_content)
            print(keywords)
            print("Get Summary!")
            summary = self._generate_summary(combined_content)
            print(summary)
            
            for chunk in chunk_group:
                formatted_doc = self._document_formatter(
                    content=chunk.text,
                    keywords_dict=keywords,
                    summary=summary 
                )
                restructured_chunks.append(formatted_doc)
        
        return restructured_chunks

    def upsert(self):
        restructured_chunks = self._restructure()
        try:
            _ = WeaviateRepository(restructured_chunks, self.collection).upsert_docs()
            return True
        except Exception as e:
            console.log(f"Error while upserting : {str(e)}")
            return False