from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import HuggingFacePipeline, GPT4All, HuggingFaceHub
from langchain.chains import LLMChain, RetrievalQA
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.docstore import InMemoryDocstore
from langchain.docstore.document import Document
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from flask import Flask, request, jsonify
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
import faiss
import numpy as np
import re
import networkx as nx
import torch
import logging
from datetime import datetime
import json
from fpdf import FPDF
import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt
import requests
import os
import threading
import time

os.environ["TOKENIZERS_PARALLELISM"] = "false"

KB_PATH = "/app/Milestone2/kb.json"

model = ChatOpenAI(
    base_url='http://ollama:11434/v1',  # Nome del servizio Docker
    temperature = 0, 
    api_key = 'not-needed',
    model_name = 'mistral'
)




# PROMPTS 
enough_info_prompt = ChatPromptTemplate.from_template(
    """
    You are an evaluator. Your job is not to answer the query. Your task is to determine if historical data, which consists only of previously recorded measurements of specific KPIs provided in the context, is needed to answer the query.

    Important:
    - Historical data refers strictly to the past measurements of the KPIs that are explicitly provided in the context.
    - Historical data does not contain information about whether a KPI exists if that KPI is not mentioned in the context. You cannot make assumptions or speculate about the existence of additional KPIs.
    - If a KPI is explicitly mentioned in the context, you do not need historical data to confirm that it exists. Historical data is only useful for analyzing past measurements, trends, or comparing values over time for that KPI.

    Historical data is needed only if the query requires:
    - Analyzing trends or changes over time.
    - Looking at historical records of measurements for KPIs that are explicitly mentioned in the context.

    If the query is about confirming the existence of a KPI that is already provided in the context, historical data is not needed.

    Explain your reasoning and conclude with a final answer: respond 'yes' if historical data is needed, otherwise respond 'no'.
    You must strictly adhere to this format.
    Context: {context}. Question: {query}.
    Answer:
    """
)

informational_query_prompt = ChatPromptTemplate.from_template(
    """
    Please answer the following question using the information in the provided context. 
    Your answer should be direct and concise, focusing specifically on addressing the question. 
    If the question asks for additional details, provide only the specific information requested. 
    Do not introduce information or explanations beyond what is directly asked for in the question. 
    Context: {context}. Question: {query}. 
    Answer:
    """
)

action_query_prompt = ChatPromptTemplate.from_template(
"""
    Analyze the provided query to extract specific details. Follow these steps precisely:

    Step 1: Determine the Timeframe 
    Identify the timeframe mentioned in the query. Classify it into one of the following categories:

    1. Specific Date:
    - A single, specific point in time. Examples include:
        - "on September 15th"
        - "on 2023-09-15"
        - "yesterday"
        - "two days ago"
    
    2. Range of Dates:
    - A continuous range that has a clear start and end date. Examples include:
        - "between September 1st and September 15th"
        - "over the past week"
        - "from July to August"
    - Note: A range always involves a start and an end date, covering all the days in between.

    3. Aggregation Period:
    - A period that indicates a repeating aggregation, usually associated with a specific frequency or regular interval, to group data. Examples include:
        - "monthly between July and September" (meaning data grouped month by month)
        - "weekly in the last month" (meaning data grouped week by week over the past month)
    - Note: An aggregation period focuses on dividing the timeframe into repeated intervals (e.g., weekly, monthly) for aggregated analysis. Only classify it as an aggregation period if **explicit** mention of terms like "monthly", "weekly", or similar are found in the query.

    Step 2: Identify the Operation
    Check if the query mentions any of the following operations:
    - sum, avg, max, min.
    If no operation is mentioned, leave this field as 'null'.

    Step 3: Extract the Following Details:
    Extract and organize the information as described below:
    - For a Specific Date:
        - Provide it in the `start_range` field in YYYY-MM-DD format.
    - For a Date Range:
        - Provide both `start_range` and `end_range` fields in YYYY-MM-DD format.
    - For an Aggregation Period:
        - Provide `start_range` and `end_range` fields in YYYY-MM-DD format.
        - Additionally, include the `aggregation` field (e.g., 'monthly', 'weekly', or 'daily').
    - 'operation': Specify the operation mentioned (e.g., 'sum,' 'avg,' 'max,' 'min'). If none, set this field to 'null'.
    - 'KPI_name': Identify the key performance indicator mentioned. If none, set this field to 'null'.
    - 'machine_name': Determine the machine referred to in the query. 

    Return the extracted information in a structured format (json).
    Today's date is {current_date} for reference.

    Query: {query}.
    Context: {context}.
    Answer
"""
)

single_value_prompt = ChatPromptTemplate.from_template(
    """
    Please answer the following question using the provided value and the given unit of measurement. 
    Your answer should be direct and concise, focusing specifically on addressing the question. 
    If the question asks for additional details, provide only the specific information requested. 
    Do not introduce information or explanations beyond what is directly asked for in the question. 
    Value: {value}. Unit of measurement: {unit}. Query: {query}. 
    Answer:
    """
)


description_prompt = ChatPromptTemplate.from_template(
    """
    Provide a concise one-sentence description of the content based on the given query.

    Example 1:
    - Query: What was the working time for LaserCutter_1 over the past week?
    - Answer: Below is the working time for LaserCutter_1 over the past week.

    Example 2:
    - Query: Show a dashboard with the utilization rate for Machine_Z over the past week.
    - Answer: Below is the dashboard with the utilization rate for Machine_z over the past week.

    Query: {query}
    Answer:
    """
)


report_prompt = ChatPromptTemplate.from_template(
    """
    You are a report generator for factory production data.
    Analyze the provided data to create a concise and accurate report that includes:

    1. Title: Create a clear and specific title based on the query.

    2. Key Performance Metrics:
       - Identify the highest and lowest production rates, including the dates.
       - Highlight the range of values (difference between highest and lowest).

    3. Overall Trends:
       - Summarize key patterns or trends over time (e.g., increases, decreases, consistency).
       - Highlight any periods of significant change.

    4. Observations:
       - Point out any anomalies or outliers, if present.
       - Provide a general evaluation of the performance (e.g., stable, improving, declining).

    Data: {data}.
    Unit of measurement: {unit}.
    Query: {query}.

    Output Guidelines:
    - Structure the report as above, using clear headers and bullet points.
    - Derive the title from the query context to provide a meaningful summary of the report’s content.
    - Keep the report concise and factual.

    Answer:
    """
)


# PIPELINES
chain1 = (
    {
        'context': RunnablePassthrough(), 
        'query': RunnablePassthrough()  
    }
    | enough_info_prompt  
    | model  
    | StrOutputParser()  
)

chain2 = (
    {
        'context': RunnablePassthrough(),  
        'query': RunnablePassthrough()  
    }
    | informational_query_prompt 
    | model   
    | StrOutputParser()  
)

chain3 = (
    {
        'context': RunnablePassthrough(), 
        'query': RunnablePassthrough(), 
        'current_date':  RunnablePassthrough()
    }
    | action_query_prompt 
    | model   
    | StrOutputParser()  
)

# Different chains 
chain4 = (
    {
        'query': RunnablePassthrough(), 
        'value': RunnablePassthrough(),
        'unit': RunnablePassthrough(),
    }
    | single_value_prompt 
    | model   
    | StrOutputParser()  
)

chain5 = (
    {
        'query': RunnablePassthrough()
    }
    | description_prompt
    | model   
    | StrOutputParser()  
)

chain6 = (
    {
        'query': RunnablePassthrough(),
        'data': RunnablePassthrough(),
        'unit': RunnablePassthrough(),
    }
    | report_prompt  
    | model   
    | StrOutputParser()  
)


def build_graph_from_json(json_file_path):
    # Crea un grafo vuoto
    G = nx.DiGraph()

    # Leggi il file JSON
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    # Aggiungi i nodi macchina
    for machine in data.get("machines", []):
        G.add_node(
            machine["id"],
            node_type="Machine",
            name=machine["name"],
            production_line=machine["productionLine"],
            factory=machine["factory"],
            machine_type=machine["machineType"]
        )

    # Aggiungi i nodi KPI
    for kpi in data.get("kpis", []):
        G.add_node(
            kpi["nameID"],
            node_type="Base KPI" if kpi.get("formula") is None else "Derived KPI",
            name=kpi["description"],
            category=kpi["category"],
            unit=kpi["unit"],
            relation_number=kpi["relationNumber"],
            formula=kpi.get("formula")
        )

    # Aggiungi le relazioni
    for rel in data.get("relation", []):
        G.add_edge(
            rel["machineID"],
            rel["kpiID"],
            relationship="monitors"
        )

    return G


def describe_networkx_graph(G):
    # Dizionario per descrizioni
    descriptions = {}
    
    # Descrivi i nodi delle macchine
    machine_nodes = [node for node, data in G.nodes(data=True) if data.get("node_type") == "Machine"]

    for node in machine_nodes:
        data = G.nodes[node]
        machine_name = data.get("name", "unknown name")
        machine_type = data.get("machine_type", "Unknown type")
        production_line = data.get("production_line", "unknown line")
        factory = data.get("factory", "unknown factory")

        incoming_edges = G.in_edges(node)
        source_nodes = [edge[0] for edge in incoming_edges]
        kpi_names = [G.nodes[source].get('name', '') for source in source_nodes]
        concatenated_kpi_names = ", ".join(kpi_names)
        
        # Genera descrizione per la macchina
        description = f"It is a {machine_type} machine located in {factory} on production line {production_line}."
        
        if kpi_names:
            description += f" It monitors the following KPIs: {concatenated_kpi_names}."
        else:
            description += " It has no KPIs associated with it."

        descriptions[machine_name] = description
    
    # Descrivi i nodi dei KPI
    kpi_nodes = [node for node, data in G.nodes(data=True) if "Base KPI" in data.get("node_type", "") or "Derived KPI" in data.get("node_type", "")]
    
    for node in kpi_nodes:
        data = G.nodes[node]
        kpi_name = data.get('name', 'unknown name')
        category = data.get('category', 'unknown category')
        has_formula = "Derived KPI" in data.get("node_type", "")
        formula = data.get('formula', 'no formula') if has_formula else 'no formula'
        unit = data.get('unit', 'unknown unit')
        
        description = f"It is a KPI in the {category} category. "
        if has_formula:
            description += f"It is a derived KPI and uses the formula: {formula}. "
        else:
            description += "It is a base KPI with no formula."
        
        description += f"The unit of measurement is {unit}."
        descriptions[kpi_name] = description

    return descriptions




def periodic_read_kb():
    while True:
        print("Reading kb...")
        read_kb()  #! Read the KB
        time.sleep(3600)  
        print("completed reading kb")


# Avvia il thread
thread = threading.Thread(target=periodic_read_kb, daemon=True)
thread.start()

def read_kb():
    url = "https://api-layer/machineXKPI"

    try:
        response = requests.get(url, verify=False, headers={"Authorization": "Bearer test_token"})
        
        if response.status_code == 200:
            response_data = response.json()
            

            try:
                with open(KB_PATH, "r") as file:
                    local_data = json.load(file)
            except FileNotFoundError:
                local_data = None  
            
            if response_data != local_data:
                print("Content differs. Updating local file and processing.")
                
                with open(KB_PATH, "w") as file:
                    json.dump(response_data, file, indent=4)
                
                return faiss_generation()
            else:
                print("Content is identical. No update needed.")
        else:
            print(f"Error: Received status code {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"An error occurred: {e}")



def faiss_generation():
    G = build_graph_from_json(KB_PATH)
    generated_descriptions = describe_networkx_graph(G)
    descriptions = []

    for node, desc in generated_descriptions.items():
        print(f"{node}: {desc}")
        descriptions.append({node: desc})


    # ## Retrieval

    # Convert the descriptions in a format suitable for retrieval through Langchain.

    # In[7]:


    # Step 1: Convert node descriptions into Langchain Document objects
    documents = []

    # Iterate over the list of dictionaries in `descriptions`
    for item in descriptions:
        for node, desc in item.items():  # Extract the key-value pair from each dictionary
            # Include the node name in the page content to make it explicit
            document_text = f"{node}: {desc}"
            documents.append(Document(page_content=document_text, metadata={"node": node}))

    # Step 2: Generate embeddings for each node description using HuggingFace
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    embeddings = [embedding_model.embed_query(doc.page_content) for doc in documents]

    # Step 3: Create FAISS index and add the embeddings
    dimension = len(embeddings[0])
    faiss_index = faiss.IndexFlatL2(dimension)
    faiss_index.add(np.array(embeddings))

    # Step 4: Create `index_to_docstore_id` and a `docstore`
    index_to_docstore_id = {i: str(i) for i in range(len(documents))}
    docstore = InMemoryDocstore(({str(i): doc for i, doc in enumerate(documents)}))

    # Step 5: Create FAISS vector store with HuggingFace embeddings and the node documents
    vector_store = FAISS.from_documents(documents, embedding_model)

    # Salva il vector store
    vector_store.save_local("/app/Milestone2/vector_store")

    return embeddings, vector_store


# FORMAT VALUES TO CONTACT THE KPI ENGINE
def extract_json_from_llm_response(response):
    matches = re.findall(r'\{.*?\}', response, re.DOTALL)
    
    if not matches:
        return {}
    
    content = matches[0]
    
    lines = content.splitlines()
    cleaned_lines = []
    for line in lines:
        cleaned_line = re.sub(r',.*', '', line).strip()
        if cleaned_line:
            cleaned_lines.append(cleaned_line)
    
    desired_keys = ["KPI_name", "machine_name", "start_range", "end_range", "aggregation", "operation"]
    result = {key: None for key in desired_keys}
    
    for line in cleaned_lines:
        for key in desired_keys:
            if line.startswith(f'"{key}"'):
                value = line.split(':', 1)[-1].strip().strip('"')
                result[key] = value
                break
    
    return result


# FORMAT REPORT TO CONTACT GUI
def parse_report_to_dict(report_text):
    """
    Parses a text-based report and converts it into a structured dictionary with a title and sections.

    Args:
        report_text (str): The report content in text format.

    Returns:
        dict: A dictionary containing the title and sections of the report.
    """
    report_data = {
        "title": "",
        "sections": {
            "Key Performance Metrics": [],
            "Overall Trends": [],
            "Observations": []
        }
    }
    
    lines = report_text.strip().split("\n")
    
    current_section = None
    is_title_assigned = False
    
    # Parse the text
    for line in lines:
        line = line.strip()
        if line.startswith("**Title:**"):  # Handle titles with "Title:"
            report_data["title"] = line.replace("**Title:**", "").strip()
            is_title_assigned = True
        elif line.startswith("**") and line.endswith("**"):  # Handle other headers
            section_title = line.strip("*").strip(":")  # Remove asterisks and colons
            if section_title in report_data["sections"]:  # If it's a known section
                current_section = section_title
            elif not is_title_assigned:  # Assign the first unmatched header as the title
                report_data["title"] = section_title
                is_title_assigned = True
            else:
                raise ValueError(f"Unknown section or title: {section_title}")
        elif line.startswith("-"):  # Add content to the current section
            if current_section:
                report_data["sections"][current_section].append(line.strip("- ").strip())
    
    return report_data


# FUNCTIONS TO DEFINE THE KIND OF CONTACT WITH GUI 
def generate_string(textual_response):
    """
    Generates a structured dictionary for a text response.

    Args:
        textual_response (str): The textual message or response.

    Returns:
        dict: A structured dictionary containing the text response and placeholders for optional dashboard or report data.
    """
    data_6 = {
        "type": "text",  # Specifies the type as a text response
        "text": textual_response,  # The actual text response
        "dashboard": None, 
        "report": None,  
    }
    return data_6

def generate_report(report):
    """
    Generates a structured dictionary for a report.

    Args:
        report (dict): The report content to include, structured as a dictionary.

    Returns:
        dict: A structured dictionary containing the report data and placeholders for optional text or dashboard elements.
    """
    data_6 = {
        "type": "report",  # Specifies the type as a report
        "text": None,  
        "dashboard": None,  
        "report": report,  # The actual report content
    }
    return data_6


def generate_dashboard(values, intro_string, x_axis_name, y_axis_name):
    """
    Generates a structured dashboard object.

    Args:
        values (list): List of values for the dashboard (e.g., data to display).
        intro_string (str): Introductory text for the dashboard (e.g., "Here is the weekly production rate for Machine_X").
        x_axis_name (str): Name of the X-axis (e.g., "Values").
        y_axis_name (str): Name of the Y-axis (e.g., KPI name).

    Returns:
        dict: A structured dictionary with the dashboard information.
    """
    data_6 = {
        "type": "dashboard",
        "text": intro_string,  # Introductory text for the dashboard
        "x_axis_name": x_axis_name,  # Name of the X-axis
        "y_axis_name": y_axis_name,  # Name of the Y-axis
        "values": values,  # Data points for the dashboard (e.g., {"x": "date", "y": value} or {"start_date": "date", "end_date": "date", "value": value})
        "report": None,
    }
    return data_6


# FUNCTION TO ELABORATE KPI ENGINE RESPONSE
def response_creation(query, kpi_response):
    if "value" in kpi_response:
        kpi_value = kpi_response["value"]
        unit = kpi_response["unit"]

        input_data = {"value": kpi_value, "unit": unit, "query": query}
        response_4 = chain4.invoke(input_data)
        response_4 = generate_string(response_4)
        return response_4

    elif "values" in kpi_response:
        values = kpi_response["values"]
        kpi_name = kpi_response["kpi_name"]

        if "report" in query.lower():
            input_data = {'query': query, 'data': values}
            report_text = chain6.invoke(input_data)
            report = parse_report_to_dict(report_text)
            response_6 = generate_report(report)
            return response_6
        else:
            input_data = {"query": query}
            intro_string = chain5.invoke(input_data)
            x_axis_name = kpi_name
            response_5 = generate_dashboard(values, intro_string, x_axis_name, "Values")

            return response_5


# FUNCTION TO CALL THE RAG PIPELINE
def steps(query, context, date):
    input_data = {"context": context, "query": query}
    response_1 = chain1.invoke(input_data)
    kpi_response = None
    first_two_tokens = response_1.strip().split()[:1]

    if " ".join(first_two_tokens) == "No,":
        response_2 = chain2.invoke(input_data)
        final_response = generate_string(response_2)    
    else:
        input_data = {"context": context, "query": query, "current_date": date}
        response_3 = chain3.invoke(input_data)

        response_3 = extract_json_from_llm_response(response_3)
        #####! TOPIC KPI ENGINE
        kpi_url = "http://127.0.0.1:8080/kpi-engine"

        try:
            response_kpi = requests.post(kpi_url)
            
            if response_kpi.status_code == 200:
                kpi_response = response_kpi.json()
                
            else:
                print("errore")
        except Exception as e:
            print(f"An error occurred: {e}")

        final_response = response_creation(query, kpi_response)
    
    return final_response


current_date = datetime.now().strftime("%Y-%m-%d")
# qui va gestita la lettura dinamica kb e la creazione degli embeddings
embeddings, _ = faiss_generation()

#! va messa la chiamta ogni x tempo e non per query
# embeddings, _ = read_kb()


app = Flask(__name__)

@app.route('/user-query', methods=['POST'])
def user_query():
    try:

        # Recupero del corpo della richiesta JSON
        data = request.get_json()

        # Validazione del corpo della richiesta
        if 'query' not in data:
            return jsonify({"error": "Query parameter is required"}), 400

        query = data['query']
        vector_store = FAISS.load_local(
            "/app/Milestone2/vector_store", HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"), allow_dangerous_deserialization=True
        )
        retriever = vector_store.as_retriever()
        context_docs = retriever.invoke(query)
        context = " ".join([doc.page_content for doc in context_docs])

        
        return jsonify(steps(query, context, current_date)), 200

    except Exception as e:
        #stampa lo stack dell'errore
        logging.error("An error occurred: ", exc_info=True,stack_info=True)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)






