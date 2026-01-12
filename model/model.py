from pydantic import BaseModel, Field
from dataclasses import dataclass
from typing import Any, Dict, List

import pandas as pd

@dataclass
class TabularStoringResponse:
    """
    TabularOrchestrator Response Model
    """
    status: str
    dropdown: Any
    summary: str
    preview: pd.DataFrame

@dataclass
class VectorInput:
    """
    Document Vectorized Store
    """
    document_id: str
    page_content: str
    summary: str
    keywords: List[str]
    entities: List[str]
    questions: List[str]
    filename: str

class VectorMetadata(BaseModel):
    """
    Metadata for Vectorized Store
    """
    keywords: list[str]
    entities: list[str]
    questions: list[str]
    summary: str
    filename: str

class FraudDocument(BaseModel):
    question: str = Field(..., description="User Question to retrieve very similar chunk to answer this question")
    collection_name: str = Field(..., description="Needs to filter which collection where's the document stored")
    document_id: str = Field(..., description="Unique ID for a Document to Retrieve as a Knowledge")

class Summary(BaseModel):
    summary: str = Field(description="Combination of Summary and Conclusion of the Content")

class Keywords(BaseModel):
    keywords: list = Field(description="Specific unique keywords")
    entities: list = Field(description="Mentioned entity such as, people, organization, building, etc")
    questions: list = Field(description="Hypothetical Questions to help RAG retrieval")

class TableSchema(BaseModel):
    table_desc: str = Field(description="Description of what this table stores")
    columns: Dict[str, str] = Field(
        description="Mapping column with their description"
    )

class DatabaseSchema(BaseModel):
    database_name: str = Field(description="Name of the database")
    database_desc: str = Field(description="Description of the database")
    table_list: Dict[str, TableSchema] = Field(
        description="Mapping table with their column and description"
    )