from langchain_openai import ChatOpenAI
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

import os

def langchainModel():
    llm = ChatOpenAI(
        api_key=os.getenv("OLLAMA_API_KEY"),
        base_url=os.getenv("GENERATIVE_HOST"),
        model=os.getenv("GENERATIVE_MODEL")
    )
    return llm

def langchainInvoke(systemPrompt, userPrompt, inputVariable, schema):
    # llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview")
    # llm = ChatOpenAI(
    #         api_key=os.getenv("OPENROUTER_API_KEY"),
    #         base_url="https://openrouter.ai/api/v1",
    #         model="google/gemma-3-27b-it:free"
    #     )
    try:
        llm = langchainModel()
        parser = PydanticOutputParser(pydantic_object=schema)

        template = ChatPromptTemplate.from_messages([
            ("system", systemPrompt),
            ("human", userPrompt)
        ])

        pipeline = template | llm | parser
        response = pipeline.invoke(inputVariable)
        return response
    except Exception as e:
        print(f"There's an error while do Invoke Langchain with error: {str(e)}")
        return False