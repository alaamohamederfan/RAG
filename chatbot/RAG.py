from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
import os
from dotenv import load_dotenv
load_dotenv()

# Step 1: Load and Preprocess Documents
file_paths = ["E:/Projects ML/ldc task/chatbot/HR_Policy_Dataset1.txt", "E:/Projects ML/ldc task/chatbot/HR_Policy_Dataset2.txt"]
documents = []

os.environ["GOOGLE_API_KEY"] = "AIzaSyAg1k4KlW-vWrurKC6ISnFmMGWB41_tw9M"
for file_path in file_paths:
    loader = TextLoader(file_path)
    docs = loader.load()
    documents.extend(docs)

text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs_split = text_splitter.split_documents(documents)

# Step 2: Create Embeddings and Chroma Vector Store
gemini_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
chroma_vector_store = Chroma.from_documents(docs_split, gemini_embeddings, persist_directory="./chroma_db")

# Step 3: Set up Retrieval and QA Chain
retriever = chroma_vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 2})
chat_model = ChatGoogleGenerativeAI(model="gemini-1.0-pro", convert_system_message_to_human=True)

# Step 4: Custom Generator Prompt
generator_prompt_template = PromptTemplate(
    template=(
        "You are an HR assistant chatbot.\n\n"
        "User's Query: {question}\n\n"
        "Chat History: {chat_history}\n\n"
        "Relevant Documents: {context}\n\n"
        "Provide a short answers, helpful answer based on the documents in english only"
    ),
    input_variables=["question", "chat_history", "context"]
)

qa_chain = ConversationalRetrievalChain.from_llm(
    llm=chat_model,
    retriever=retriever,
    return_source_documents=False,
    combine_docs_chain_kwargs={"prompt": generator_prompt_template}
)

