# **RAG Task - ReadMe**

## **Task Description**

### **Objective**  
Build a chatbot system integrating .NET Web API with a Python backend, utilizing LangChain for Retrieval-Augmented Generation (RAG) functionality.

### **Key Features**
- User questions are received via HTTP POST (in .NET API).  
- Queries are processed using LangChain to retrieve answers from provided text documents.  
- Responses are logged into an SQL database for tracking.

---

## **System Components and Requirements**

### **1. .NET Web API**  
**Functions**:  
- Accepts user questions via HTTP POST requests.  
- Sends questions to the Python backend over HTTP.  
- Receives the chatbot’s responses from the Python backend.  
- Logs queries and responses into an SQL database.

---

### **2. Python Backend**  
**Framework**: LangChain for RAG pipeline implementation.  

**Tasks**:  
1. Index and embed provided text documents, saving the embeddings into a vector database.  
2. Retrieve relevant document chunks based on queries.  
3. Generate responses using a language model (`gemini-1.0-pro`).  
4. Send responses back to the .NET API.

---

### **3. SQL Database**

#### **Schema Analysis**

##### **1. UserQueries Table**  
**Purpose**: Store user-submitted questions.  

**Columns**:  
- **QueryId**: Unique identifier for each query.  
- **SessionId**: Unique identifier for user sessions to group queries.  
- **Question**: The user's question.  
- **Timestamp**: When the query was made.  
- **SessionExpiration**: Unique identifier for user sessions to group queries. Remains constant for 15 minutes per session.  

##### **2. ChatbotResponses Table**  
**Purpose**: Store chatbot responses linked to user queries.  

**Columns**:  
- **ResponseId**: Unique identifier for each response.  
- **QueryId**: Foreign key linking the response to a specific query.  
- **Response**: The generated chatbot response.  
- **Timestamp**: When the response was created.

---

### **4. Streamlit Web Interface**

#### **Purpose**  
- Provide a web interface for users to interact with the chatbot.  
- Allow testing of the chatbot's functionality during development.

#### **Streamlit Components**  

1. **Frontend Interface**:  
   - A text input box for users to ask questions.  
   - A "Send" button to submit queries to the backend.  
   - A display area to show chatbot responses.  
   - A reset button to reset the session.  

2. **Backend Communication**:  
   - Send user queries to the .NET Web API using HTTP requests.  
   - Receive responses from the API and display them in the interface.
