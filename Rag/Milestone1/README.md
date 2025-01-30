# Project Name: **KPI Machine Monitoring System with Retrieval-Augmented Generation (RAG)**

## Project Description

This project aims to monitor and manage the efficiency and performance of machinery, such as laser cutters, within a production system. By using directed graphs and machine learning techniques, we define and calculate Key Performance Indicators (KPIs) based on collected data. Additionally, an NLP model (FLAN-T5) provides accurate, context-aware responses to user queries about the indicators and machinery.

## Project Goals

1. **Creation and management of a machine and KPI graph**: Machines are represented as nodes and connected to KPI nodes that monitor specific metrics.
3. **Query retrieval and response**: Using LLM models, the system answers user questions about machinery KPIs, providing specific information.
4. **Integration with embedding models**: The project uses Sentence Transformers and FAISS for retrieval of relevant information based on queries.

## Development Phases

### 1. Graph Definition and Structure
- **Creating the directed graph**: Definition of machines and KPIs as nodes using the NetworkX package.
- **Assigning attributes and relationships**: Each node is assigned specific attributes like node type, description, and measurement units.
- **Defining relationships**: Directed edges connect machines to the KPIs they measure and derived KPIs to base KPIs.

### 2. Automatic Description Generation
- **Function `generate_descriptions`**: This function generates textual descriptions for each node (machine or KPI) in the graph.
- **Attribute-based descriptions**: Descriptions include machine models, KPI normal ranges, calculation formulas, and relationships with other nodes.

### 3. Embedding and Information Retrieval
- **Creating embeddings**: Sentence Transformer models are used to generate embeddings of node descriptions.
- **Creating a FAISS index**: Node embeddings are added to a FAISS index to enable fast retrieval of similar information based on the user query.
- **Retrieval function `retrieve_top_k_nodes`**: This function retrieves the most relevant nodes based on the user’s query.

### 4. Query Answering via NLP Models
- **Models used**: FLAN-T5 is used for both query classification and text response generation.
- **Classification and generation pipeline**: Inference pipelines determine whether the query can be answered with the current data and, if so, provide the response. Otherwise, it provides necessary information to pass to the KPI Calculation Engine.
  
### 5. Usage Examples and Testing
Example questions tested:
- "How many Laser Cutter machines are there?"
- "What is the utilization rate for LaserCutter_1 last month?"
- "Is there a KPI that measures the percentage of time working?"

## Requirements

- Python 3.x
- Libraries:
  - `networkx` for graph management
  - `SentenceTransformer` and `FAISS` for embeddings and retrieval
  - `transformers` for the FLAN-T5 NLP model
  - `torch` for CUDA support and inference

## Project Execution

1. **Set up the environment**: Install dependencies.
2. **Run the code**: Execute scripts to create the graph, calculate KPIs, and respond to queries.
3. **Test the system with sample queries**.
