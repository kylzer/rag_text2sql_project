import sqlite3
import json

from langchain.tools import tool

from database import Weaviate
from model import FraudDocument

from weaviate import classes
from weaviate.classes.query import MetadataQuery

from rich.console import Console
console = Console()

@tool
def database_information():
    """
    Before generate a query for SQLite.
    You need to get information by this function.
    
    This function included the Schema, Description, and Record Sample.
    This will help to generate a query more accurate.
    """
    schema = ""
    record = {}
    try:
        with open("database/db_schema.json", "r") as f:
            schema = json.load(f)

        conn = sqlite3.connect("database/data.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            AND name NOT LIKE 'sqlite_%';
        """)
        tables = [row[0] for row in cursor.fetchall()]    
        for table_name in tables:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            rows = cursor.fetchall()        
            record[table_name] = [dict(row) for row in rows]
        
        conn.close()

        messages = f"""
            Database Schema :
            {schema}

            Record Examples :
            {record}
        """
        return messages
    except Exception as e:
        return f"There's an error while gaining information with error: {str(e)}"

@tool
def fraud_database(query: str):
    """
    Execute a SQL query against the SQLite database. 
    Use database_information first to see available tables.

    Args :
        query        : SQLite query
    """
    try:
        danger_keywords = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "TRUNCATE"]
        if any(word in query.upper() for word in danger_keywords):
            return "Generated Query contain malicious command or keyword!"

        conn = sqlite3.connect("database/data.db")
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        results = [dict(zip(column_names, row)) for row in rows]
        conn.close()
        return results
    except Exception as e:
        return f"Error while using fraud_database tool: {str(e)}"


@tool(args_schema=FraudDocument)
def fraud_knowledge(question: str = None, collection_name: str = None, document_id: str = None):
    """
    Function to retrieve knowledge from vector database
    Args :
        question        : user question
        collection_name : collection where's the document stored
        document_id     : id to retrieve the document
    """

    chunk_list = []

    vector_conn = Weaviate(collection_name)
    client = vector_conn.client
    with client as client:
        if client.collections.exists(collection_name):
            console.log(f'Successfully connected to collection: {collection_name}')
            collection = client.collections.get(collection_name)
            try:
                weaviate_param = {
                    "query": question,
                    "return_metadata": MetadataQuery(distance=True, score=True, explain_score=True),
                    "limit": 5
                }

                if document_id is not None:
                    weaviate_param["filters"] = classes.query.Filter.by_property("document_id").contains_any([document_id]) 
                    response = collection.query.hybrid(**weaviate_param)
                else:
                    response = collection.query.near_text(**weaviate_param)           

                if hasattr(response, 'objects') and response.objects:
                    if document_id:
                        console.log(f'Found {len(response.objects)} objects with document_id: {document_id}')
                    else:
                        console.log(f'Found {len(response.objects)} objects across all documents')
                    for result in response.objects:
                        chunk_list.append(result.properties.get("page_content", ""))
                    console.log(f"Chunk List :\n{chunk_list}")
                    return chunk_list
                else:
                    console.log(f'No existing objects found with document_id: {document_id}')
                    return f"No existing objects found with document_id: {document_id}"
                
            except Exception as e:
                console.log(f"Error during operation: {str(e)}")
                return "Error during retrieving from weaviate"
        else:
            console.log(f"Collection {collection_name} does not exist")
            return f"Collection named {collection_name} does not exist"
