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
from datetime import datetime, timedelta
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

KB_PATH = "/app/Milestone3/kb.json" # Path to the KB file

USERNAME = "RAG"
PASSWORD = "password3"

# LLM MODEL 
model = ChatOpenAI(
    base_url='http://ollama:11434/v1',
    temperature = 0, 
    api_key = 'not-needed',
    model_name = 'mistral'
)

# PROMPTS
# Different prompts for different types of queries
# Each prompt is designed to guide the evaluator to provide the necessary information or answer based on the query type. 
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

    Step 2: Identify the Operation
    Check if the query mentions any of the following operations:
    - sum, avg, max, min.
    If no operation is mentioned, leave this field as 'null'.

    Step 3: Extract the Following Details:
    Extract and organize the information as described below:
    - For a Specific Date:
        - Provide it in the start_range field in YYYY-MM-DD format.
    - For a Date Range:
        - Provide both start_range and end_range fields in YYYY-MM-DD format.
    - For an Aggregation Period:
        - Provide start_range and end_range fields in YYYY-MM-DD format.
    - 'operation': Specify the operation mentioned (e.g., 'sum,' 'avg,' 'max,' 'min'). If none, set this field to 'null'.
    - 'KPI_name': Identify the key performance indicator mentioned.
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
# Define the Langchain pipeline for processing the queries and generating responses
# The pipeline consists of a series of steps that process the input data and generate the final response.
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


def get_token():
    """
    This function retrieves the token value from the API by sending a POST request with the username and password.

    Returns:
    - str: The token value.
    """
    resposne = requests.post("https://api-layer/user/login", headers = {"username": USERNAME, "password": PASSWORD}, verify=False)

    if resposne.status_code == 200:
        return resposne.json()
    else:
        return None

def check_aggregation(input_string, start_date, end_date):
    """
    Checks if the input string contains the words 'daily', 'monthly', or 'weekly'
    (case-insensitive) and returns the first match. If no match is found, returns None.

    Args:
    input_string (str): The input string to check.
    start_date (str): The start date of the period to analyze.
    end_date (str): The end date of the period to analyze.

    Returns:
    str or None: The matched time aggregation word ('daily', 'monthly', 'weekly'), 
                'daily' if start_date equals end_date, or 'overall' otherwise.
    """
    # Convert the input string to lowercase for case-insensitive comparison
    input_lower = input_string.lower()
    
    # List of time aggregation keywords to search for
    time_aggregations = ['daily', 'monthly', 'weekly']
    
    # Check if any of the keywords are present in the input string
    for word in time_aggregations:
        if word in input_lower:  # If the current keyword is found in the input string
            if word == 'daily':
                return 'day'
            elif word == 'monthly':
                return 'month'
            elif word == 'weekly':
                return 'week'
            return word          # Return the matched keyword (e.g., 'daily', 'monthly', 'weekly')
        
    # If no keyword is found, check the dates provided
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    
    # If start_date is exactly one day before end_date
    if start_date_obj + timedelta(days=1) == end_date_obj:
        return 'day'  # Default aggregation to 'daily' if start_date is the day before end_date
    else:
        return 'overall'  # Default aggregation to 'overall' if start_date is not the day before end_date

def build_graph_from_json(json_file_path):
    '''
    This function builds a directed graph from a JSON file.
    The graph contains nodes for machines and KPIs, and edges representing the relationships
    where machines monitor specific KPIs.

    Parameters:
    - json_file_path (str): Path to the JSON file containing the graph data.

    Returns:
    - G (networkx.DiGraph): A directed graph with machine and KPI nodes and their relationships.
    '''

    # Create an empty directed graph using NetworkX
    G = nx.DiGraph()

    # Open and read the JSON file
    with open(json_file_path, 'r') as f:  # Open the file in read mode
        data = json.load(f)  # Load the JSON content into the 'data' dictionary

    # Add the machine nodes to the graph
    for machine in data.get("machines", []):  # Iterate through the "machines" list in the JSON data
        G.add_node(  # Add a node for each machine with its attributes
            machine["id"],  # Node ID is set as the machine's ID
            node_type="Machine",  # Node type attribute to differentiate it as a machine
            name=machine["name"],  # Name of the machine
            production_line=machine["productionLine"],  # Production line the machine belongs to
            factory=machine["factory"],  # Factory to which the machine belongs
            machine_type=machine["machineType"]  # Type of the machine
        )

    # Add the KPI nodes to the graph
    for kpi in data.get("kpis", []):  # Iterate through the "kpis" list in the JSON data
        G.add_node(  # Add a node for each KPI with its attributes
            kpi["nameID"],  # Node ID is set as the KPI's nameID
            node_type="Base KPI" if kpi.get("formula") is None else "Derived KPI",  
            # Determine if KPI is 'Base KPI' (no formula) or 'Derived KPI' (has a formula)
            name=kpi["nameID"].replace("_"," "),  # Description of the KPI
            description=kpi["description"],  # Description of the KPI
            category=kpi["category"],  # Category of the KPI
            unit=kpi["unit"],  # Measurement unit of the KPI
            relation_number=kpi["relationNumber"],  # Relation number (a specific attribute)
            formula=kpi.get("formula"),  # Formula (optional; None if not provided)
            kpi_id=kpi["nameID"]         
        )

    # Add relations (edges) between machines and KPIs
    for rel in data.get("relation", []):  # Iterate through the "relation" list in the JSON data
        machine = rel["machineID"]  # Extract the machine ID
        kpi_rel = rel["kpiID"]  # Extract the KPI ID

        #take the kpi that has relationNumber = kpi_rel
    

        #scorri tutti i kpi dal Grafo

        kpi_nodes = [(node, data) for node, data in G.nodes(data=True) if "Base KPI" in data.get("node_type", "") or "Derived KPI" in data.get("node_type", "")]
        
        kpi_def = None
        for kpi in kpi_nodes:
            _,values = kpi
            if values["relation_number"] == kpi_rel:
                kpi_def = values["kpi_id"] 
                break
        

        G.add_edge(  # Add a directed edge between machine and KPI
            kpi_def,  # Target node: kpiID
            rel["machineID"],  # Source node: machineID
            relationship="monitors"  # Edge attribute to describe the relationship
        )

    # Return the constructed graph
    return G

def describe_networkx_graph(G):
    '''
    This function generates a description of all nodes in a NetworkX graph.
    Nodes are categorized into machines and KPIs, and detailed descriptions are provided
    based on their attributes and relationships.

    Parameters:
    - G (networkx.Graph): A NetworkX graph containing nodes and edges with attributes.

    Returns:
    - descriptions (dict): A dictionary where keys are node names, and values are their descriptions.
    '''

    # Dictionary to contain the description of the nodes
    descriptions = {}

    # Machine nodes description
    machine_nodes = [node for node, data in G.nodes(data=True) if data.get("node_type") == "Machine"]
    # Extract all nodes where the node_type is "Machine"

    for node in machine_nodes:  # Iterate over all machine nodes
        data = G.nodes[node]  # Retrieve node attributes
        machine_name = data.get("name", "unknown name")  # Get machine name (default: 'unknown name')
        machine_type = data.get("machine_type", "Unknown type")  # Get machine type
        production_line = data.get("production_line", "unknown line")  # Get production line info
        factory = data.get("factory", "unknown factory")  # Get factory name

        # Find incoming edges to the machine node (KPIs that this machine monitors)
        incoming_edges = G.in_edges(node)  # Retrieve incoming edges for the node
        source_nodes = [edge[0] for edge in incoming_edges]  # Extract source nodes of these edges
        kpi_names = [G.nodes[source].get('name', '') for source in source_nodes]  
        # Retrieve 'name' attribute of the source nodes (KPIs)
        concatenated_kpi_names = ", ".join(kpi_names)  # Concatenate KPI names into a single string

        # Build the machine description
        description = f"It is a {machine_type} machine located in {factory} on production line {production_line}."
        # Include monitored KPIs, if any
        if kpi_names:
            description += f" It monitors the following KPIs: {concatenated_kpi_names}."
        else:
            description += " It has no KPIs associated with it."

        # Add the description to the dictionary with the machine name as the key
        descriptions[machine_name] = description

    # KPI nodes description
    kpi_nodes = [node for node, data in G.nodes(data=True) if "Base KPI" in data.get("node_type", "") or "Derived KPI" in data.get("node_type", "")]
    # Extract nodes where the node_type contains 'Base KPI' or 'Derived KPI'

    for node in kpi_nodes:  # Iterate over all KPI nodes
        data = G.nodes[node]  # Retrieve node attributes
        kpi_name = data.get('name', 'unknown name')  # Get KPI name (default: 'unknown name')
        description_kpi = data.get('description', 'no description')  # Get KPI description
        category = data.get('category', 'unknown category')  # Get KPI category
        has_formula = "Derived KPI" in data.get("node_type", "")  # Check if the KPI is derived (has a formula)
        formula = data.get('formula', 'no formula') if has_formula else 'no formula'  
        # Retrieve formula if the KPI is derived, otherwise set as 'no formula'
        unit = data.get('unit', 'unknown unit')  # Get the measurement unit

        # Build the KPI description
        description = f"It is a KPI in the {category} category. "
        if has_formula:
            description += f"It is a derived KPI and uses the formula: {formula}. "
        else:
            description += "It is a base KPI with no formula."

        description += f"The unit of measurement is {unit}."

        description += f" It is {description_kpi}"  # Add the KPI description to the overall description

        # Add the description to the dictionary with the KPI name as the key
        descriptions[kpi_name] = description

    # Return the dictionary containing all node descriptions
    return descriptions

# Usage
G = build_graph_from_json(KB_PATH)  # Assuming this function is already implemented

def read_kb():
    '''
    This function fetches the knowledge base (KB) from a remote API and updates
    the local KB file if any changes are detected.

    - It compares the API response with the existing local KB file.
    - If the content differs, it updates the file and triggers further processing.

    Returns:
    - The result of the `faiss_generation` function if updates occur.
    - None if no update is needed or an error occurs.
    '''
    url = "https://api-layer/machineXKPI"  # Endpoint URL for fetching the KB

    try:
        # Prepare headers with an authorization token
        headers_to_send = {
            "Authorization": get_token()  # Authorization header for secure access
        }
        response = requests.get(url, verify=False, headers=headers_to_send)  
        # Make an HTTP GET request to fetch data from the KB API
        # verify=False bypasses SSL verification (use with caution)

        if response.status_code == 200:  # Check if the request was successful
            response_data = response.json()  # Parse the response as JSON
            
            try:
                with open(KB_PATH, "r") as file:  # Attempt to open the local KB file
                    local_data = json.load(file)  # Load existing KB data from the file
            except FileNotFoundError:  # Handle case where local file does not exist
                local_data = None  # Set local_data to None if file is not found
            
            # Compare the fetched data with local data
            if response_data != local_data:
                print("Content differs. Updating local file and processing.")
                # If content is different, update the local file
                with open(KB_PATH, "w") as file:
                    json.dump(response_data, file, indent=4)  # Write updated data to the file
                
                return faiss_generation()  # Trigger further processing (e.g., FAISS index generation)
            else:
                print("Content is identical. No update needed.")  # Log message if no update is required
        else:
            print(f"Error: Received status code {response.status_code}")  # Log the error status code
            print(response.text)  # Print the error response text for debugging

    except Exception as e:  # Handle any exceptions that occur during the process
        print(f"An error occurred: {e}")  # Log the exception details

def periodic_read_kb():
    '''
    This function runs in an infinite loop, periodically calling the `read_kb` function
    to fetch and update the knowledge base every 3600 seconds (1 hour).

    It is designed to be run as a daemon thread to ensure non-blocking execution in the main program.
    '''
    while True:
        print("Reading kb...")  # Log message indicating the KB reading process has started
        read_kb()  # Uncomment this line to call the KB reading function if needed
        time.sleep(3600)  # Pause execution for 1 hour (3600 seconds)
        print("completed reading kb")  # Log message indicating the KB reading process has completed

# Start the thread
thread = threading.Thread(target=periodic_read_kb, daemon=True)
# Create a daemon thread that runs the `periodic_read_kb` function.
# The `daemon=True` ensures the thread exits when the main program ends.

thread.start()  # Start the thread execution

# RETRIEVAL
def faiss_generation():
    '''
    This function generates a FAISS vector store from a knowledge base (KB) JSON file.
    It creates a graph, describes its nodes, converts these descriptions into embeddings,
    and builds a FAISS index to enable efficient retrieval.

    Steps:
    1. Build a graph from the KB JSON file.
    2. Generate natural language descriptions for nodes in the graph.
    3. Embed the descriptions using HuggingFace's Sentence-Transformers model.
    4. Create a FAISS vector store with these embeddings for retrieval.
    5. Save the FAISS vector store locally.

    Returns:
    - embeddings (list): List of embeddings generated for node descriptions.
    - vector_store (FAISS): The FAISS vector store object.
    '''
    # Step 1: Build the graph from the local knowledge base (KB)
    G = build_graph_from_json(KB_PATH)  # Build a graph from the KB JSON file
    generated_descriptions = describe_networkx_graph(G)  # Generate descriptions for graph nodes
    descriptions = []  # Initialize an empty list for formatted descriptions

    # Iterate through the generated descriptions and print them
    for node, desc in generated_descriptions.items():
        print(f"{node}: {desc}")  # Log the node name and description
        descriptions.append({node: desc})  # Append node-description pair to the list
    
    # Step 2: Convert node descriptions into Langchain Document objects
    documents = []  # Initialize an empty list for Document objects

    for item in descriptions:  # Iterate through node-description pairs
        for node, desc in item.items():  # Extract node and description
            # Combine node name and description into a single string
            document_text = f"{node}: {desc}"
            # Create a Langchain Document object with metadata
            documents.append(Document(page_content=document_text, metadata={"node": node}))

    # Step 3: Generate embeddings for each node description using HuggingFace
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    # Load the HuggingFace embedding model for generating embeddings

    embeddings = [embedding_model.embed_query(doc.page_content) for doc in documents]
    # Generate embeddings for each document's content and store them in a list

    # Step 4: Create a FAISS index and add the embeddings
    dimension = len(embeddings[0])  # Determine the dimensionality of the embeddings
    faiss_index = faiss.IndexFlatL2(dimension)  # Create a FAISS index with L2 (Euclidean) distance
    faiss_index.add(np.array(embeddings))  # Add embeddings to the FAISS index

    # Step 5: Create `index_to_docstore_id` and an in-memory docstore
    index_to_docstore_id = {i: str(i) for i in range(len(documents))}  # Map indices to document IDs
    docstore = InMemoryDocstore({str(i): doc for i, doc in enumerate(documents)})  
    # Create an in-memory docstore to hold the documents

    # Step 6: Create FAISS vector store with HuggingFace embeddings and the node documents
    vector_store = FAISS.from_documents(documents, embedding_model)
    # Build a FAISS vector store by embedding documents and linking them with their FAISS index

    # Step 7: Save the FAISS vector store locally
    vector_store.save_local("/app/Milestone3/vector_store")
    # Save the FAISS vector store for persistent storage

    return embeddings, vector_store  # Return the embeddings and the FAISS vector store


def extract_json_from_llm_response(response):
    '''
    This function extracts relevant JSON data from an LLM response and formats it into a structured dictionary. 
    It also retrieves the corresponding machine ID from the knowledge base (KB) based on the machine name.

    Parameters:
    - response (str): The raw response from the LLM, which contains JSON-like content.

    Returns:
    - result (dict): A dictionary containing extracted and formatted values for KPI queries, 
                    including the machine ID and default values for missing fields.
    '''

    # Step 1: Extract JSON-like content from the response using regex
    matches = re.findall(r'\{.*?\}', response, re.DOTALL)
    # Use regex to find content wrapped in curly braces `{}` across multiple lines (DOTALL allows multiline matches)

    if not matches:  # If no matches are found, return an empty dictionary
        return {}

    content = matches[0]  # Take the first match as the JSON content

    # Step 2: Clean up and process the content line by line
    lines = content.splitlines()  # Split the content into individual lines
    cleaned_lines = []  # Initialize an empty list for cleaned lines
    for line in lines:
        cleaned_line = re.sub(r',.*', '', line).strip()  # Remove trailing content after commas and strip whitespace
        if cleaned_line:  # Add non-empty lines to the cleaned list
            cleaned_lines.append(cleaned_line)

    # Step 3: Initialize a dictionary with desired keys and default `None` values
    desired_keys = ["kpi_name", "machine_name", "start_range", "end_range", "operation", "start_date", "end_date", "kpi", "machine", "date"]
    result = {key: None for key in desired_keys}  # Initialize the result dictionary

    # Step 4: Extract key-value pairs from cleaned lines
    for line in cleaned_lines:  # Iterate through cleaned lines
        for key in desired_keys:  # Check for desired keys
            if line.lower().startswith(f'"{key}"'):  # If the line starts with a specific key
                value = line.split(':', 1)[-1].strip().strip('"')  # Extract the value after ':' and clean it
                result[key] = value  # Store the value in the result dictionary
                break  # Break once a key is matched



    # Step 5: Retrieve the machine ID from the knowledge base (KB)
    if result["machine_name"] is not None:  # If the machine name is provided in the result
        machine_name = result["machine_name"] # Extract the machine name from the result
    else:
        machine_name = result["machine"] # Extract the machine name from the result
        result["machine_name"] = result["machine"]
    del result["machine"]
    

    if result["kpi_name"] is not None:  # If the KPI name is provided in the result
        kpi_name = result["kpi_name"] # Extract the KPI name from the result
    else:
        kpi_name = result["kpi"]
        result["kpi_name"] = result["kpi"]
    del result["kpi"]

    machine_id = None # Initialize the machine ID as None
    kpi_id = None # Initialize the KPI ID as None

    with open(KB_PATH, "r") as file: # Open the KB file in read mode
        kb_data = json.load(file) # Load the KB data from the file
        if machine_name is not None:
            for machine in kb_data["machines"]: # Iterate through the machines in the KB
                if machine["name"].lower() == machine_name.lower(): # If the machine name matches the query
                    machine_id = machine["id"] # Retrieve the machine ID
                    break # Break the loop once the ID is found
        
        if kpi_name is not None:     
            for kpi in kb_data["kpis"]: # Iterate through the KPIs in the KB
                if kpi["nameID"].replace("_"," ").lower() == kpi_name.lower(): # If the KPI name matches the query
                    kpi_id = kpi["nameID"] # Retrieve the KPI ID
                    break # Break the loop once the ID is found



    # in result i valori "null" falli diventare None

    for key in result:
        if result[key] == "null":
            result[key] = None

    # Step 6: Set default values for missing fields
    if result["start_range"] is None: # If start_range is not provided
        if result["start_date"] is not None: # If start_date is provided
            result["start_range"] = result["start_date"] # Use start_date as the default value
        else:
            result["start_range"] = result["date"]
        # remove the key start_date from result

    del result["start_date"]
    del result["date"]


    if result["end_range"] is None and result["end_date"] is None: # If end_range is not provided
        result["end_range"] = result["start_range"]

    elif result["end_range"] is None and result["end_date"] is not None:
        result["end_range"] = result["end_date"]    
    del result["end_date"]


    if result["operation"] is None: # If operation is not provided
        result["operation"] = "sum"

    # La data in formato stringa
    end_date = result["end_range"]

    
    # Converti la stringa in oggetto datetime
    date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    # Aggiungi un giorno
    new_date_obj = date_obj + timedelta(days=1)
    # Converti di nuovo in stringa
    new_date_str = new_date_obj.strftime('%Y-%m-%d')
    # Aggiorna il valore di end_range
    result["end_range"] = new_date_str  

    # Step 7: Add the retrieved machine ID to the result
    result["machine_id"] = machine_id
    result["kpi_id"] = kpi_id

    # Return the formatted result dictionary
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

    # Initialize a dictionary to hold the structured report data
    report_data = {
        "title": "",  # Placeholder for the report title
        "sections": {  # Predefined sections for the report
            "Key Performance Metrics": [],
            "Overall Trends": [],
            "Observations": []
        }
    }

    # Split the report text into individual lines, stripping whitespace and line breaks
    lines = report_text.strip().split("\n")
    
    # Variables to track the current section being processed and if the title has been assigned
    current_section = None
    is_title_assigned = False

    # Step 1: Parse the text line by line
    for line in lines:
        line = line.strip()  # Clean up the current line

        # Step 2: Detect the title section
        if line.startswith("**Title:**"):  # If the line starts with "Title:"
            report_data["title"] = line.replace("**Title:**", "").strip()  # Extract the title text
            is_title_assigned = True  # Mark the title as assigned

        # Step 3: Detect section headers (lines surrounded by double asterisks **)
        elif line.startswith("**") and line.endswith("**"):
            section_title = line.strip("*").strip(":")  # Remove asterisks and colons to clean the header

            # Check if the section header matches a predefined section
            if section_title in report_data["sections"]:
                current_section = section_title  # Update the current section
            elif not is_title_assigned:  # If no title has been assigned, treat the first header as the title
                report_data["title"] = section_title
                is_title_assigned = True
            else:  # Raise an error if an unknown section is encountered
                raise ValueError(f"Unknown section or title: {section_title}")

        # Step 4: Handle content lines (lines starting with "-")
        elif line.startswith("-"):
            if current_section:  # Ensure a section is currently active
                # Add the cleaned line content to the current section
                report_data["sections"][current_section].append(line.strip("- ").strip())

    # Step 5: Return the structured dictionary
    return report_data


# FUNCTIONS TO DEFINE THE KIND OF CONTACT WITH GUI 

def generate_string(textual_response):
    """
    Generates a structured dictionary for a text response.

    Args:
        textual_response (str): The textual message or response.

    Returns:
        dict: A structured dictionary containing the text response and placeholders 
            for optional dashboard or report data.
    """
    data_6 = {
        "type": "text",          # Specifies the type as a text response
        "text": textual_response,  # The actual text response to display
        "dashboard": None,       # Placeholder for dashboard data (not used here)
        "report": None,          # Placeholder for report data (not used here)
    }
    return data_6


def generate_report(report):
    """
    Generates a structured dictionary for a report.

    Args:
        report (dict): The report content to include, structured as a dictionary.

    Returns:
        dict: A structured dictionary containing the report data and placeholders 
            for optional text or dashboard elements.
    """
    data_6 = {
        "type": "report",   # Specifies the type as a report
        "text": None,       # Placeholder for text response (not used here)
        "dashboard": None,  # Placeholder for dashboard data (not used here)
        "report": report,   # The actual report content to include
    }
    return data_6


def generate_dashboard(values, intro_string, x_axis_name, y_axis_name):
    """
    Generates a structured dictionary for a dashboard visualization.

    Args:
        values (list): List of values for the dashboard (e.g., data points).
        intro_string (str): Introductory text for the dashboard (e.g., "Here is the weekly production rate for Machine_X").
        x_axis_name (str): Name of the X-axis (e.g., "Date").
        y_axis_name (str): Name of the Y-axis (e.g., KPI name or value type).

    Returns:
        dict: A structured dictionary containing the dashboard data, including axis labels, 
            introductory text, and values to display.
    """
    data_6 = {
        "type": "dashboard",      # Specifies the type as a dashboard
        "text": intro_string,     # Introductory text for the dashboard
        "x_axis_name": x_axis_name,  # Name of the X-axis (e.g., "Date")
        "y_axis_name": y_axis_name,  # Name of the Y-axis (e.g., KPI name)
        "values": values,         # Data points for the dashboard visualization
        "report": None,           # Placeholder for report data (not used here)
    }
    return data_6


# FUNCTION TO ELABORATE KPI ENGINE RESPONSE
def response_creation(query, kpi_response, kpi_name):
    """
    Processes the response from the KPI engine and generates an appropriate structured response
    based on the query and KPI values.

    Args:
        query (str): The query provided by the user.
        kpi_response (dict): The response from the KPI engine containing KPI values and units.
        kpi_name (str): The name of the KPI being processed.

    Returns:
        dict: A structured dictionary that represents a text response, a report, or a dashboard 
            based on the KPI data and query context.
    """

    # Step 1: Handle the case where no data is found
    if len(kpi_response["values"]) == 0:
        return generate_string("No data found for the given query.")
    # Step 2: Handle case where only a single KPI value is returned
    elif len(kpi_response["values"]) == 1:  # Check if there is only one value in the response
        kpi_value = kpi_response["values"][0]["value"]  # Extract the KPI value
        unit = kpi_response["unit"]        # Extract the KPI unit

        # Prepare input data for further processing
        input_data = {"value": kpi_value, "unit": unit, "query": query}
        response_4 = chain4.invoke(input_data)  # Invoke chain4 to process the single KPI value

        # Format the output as a structured text response
        response_4 = generate_string(response_4)
        return response_4# Step 3: Handle case where multiple KPI values are returned
    else:
        values = kpi_response["values"]  # Extract all KPI values from the response

        # Check if the query requests a "report"
        if "report" in query.lower():  # If the query explicitly asks for a report
            input_data = {'query': query, 'data': values}  # Prepare input data for chain6
            report_text = chain6.invoke(input_data)  # Generate a textual report using chain6

            # Parse the report text into a structured dictionary
            report = parse_report_to_dict(report_text)

            # Format the output as a structured report
            response_6 = generate_report(report)
            return response_6

        # Handle case where a dashboard is needed
        else:
            input_data = {"query": query}  # Prepare input data for chain5
            intro_string = chain5.invoke(input_data)  # Generate introductory text for the dashboard

            x_axis_name = kpi_name  # Set the X-axis name to the KPI name
            # Format the output as a structured dashboard response
            response_5 = generate_dashboard(values, intro_string, x_axis_name, "Values")
            return response_5


# FUNCTION TO CALL THE RAG PIPELINE
def steps(query, context, date):
    """
    This function orchestrates the retrieval-augmented generation (RAG) pipeline. 
    It determines whether historical data is needed, processes queries, fetches KPI data, 
    and generates appropriate structured responses.

    Args:
        query (str): The user query or question.
        context (str): The context provided for processing the query.
        date (str): The current date for reference.

    Returns:
        dict: A structured dictionary representing the final response, 
            which can be a text, report, or dashboard.
    """

    # Step 1: Invoke chain1 to determine if historical data is needed
    input_data = {"context": context, "query": query}  # Prepare input for chain1
    response_1 = chain1.invoke(input_data)  # Invoke chain1 with the input data

    kpi_response = None  # Initialize KPI response placeholder
    first_two_tokens = response_1.strip().split()[:1]  # Extract the first token of the response

    # Step 2: If chain1 says "No", proceed with chain2
    if " ".join(first_two_tokens) == "No,":  # Check if chain1 indicates no historical data is needed
        response_2 = chain2.invoke(input_data)  # Invoke chain2 for an alternative response
        final_response = generate_string(response_2)  # Format the response as text
    else:
        # Step 3: If chain1 says historical data is needed, invoke chain3 to extract query details
        input_data = {"context": context, "query": query, "current_date": date}
        response_3 = chain3.invoke(input_data)  # Invoke chain3 to get structured query details


        # Step 4: Extract query details (e.g., KPI name, machine ID, and date ranges)
        response_3 = extract_json_from_llm_response(response_3)
        
        aggregation = check_aggregation(query, response_3.get("start_range"), response_3.get("end_range"))


        # Step 5: Prepare the KPI engine API request URL and headers
        if response_3.get('kpi_id') is None:
            return generate_string("Error: KPI name not found in the query.")
        
        if response_3.get('machine_id') is None:
            return generate_string("Error: Machine not found in the query.")


        # TOPIC KPI ENGINE
        kpi_url = f"https://api-layer/KPI/{response_3.get('kpi_id')}/{response_3.get('machine_id')}/values"

        try:
            headers_to_send = {
                "Authorization": get_token(),  # Authorization header with Bearer token
                "aggregationInterval": aggregation,  # Aggregation interval (e.g., day, week)
                "aggregationOp": response_3.get("operation"),          # Aggregation operation (e.g., sum, avg)
                "startDate": response_3.get("start_range"),            # Start date for KPI values
                "endDate": response_3.get("end_range")                 # End date for KPI values
            }


            # Step 6: Make an HTTP GET request to the KPI engine API
            response_kpi = requests.get(kpi_url, headers=headers_to_send, verify=False)

            # Step 7: Check if the request was successful
            if response_kpi.status_code == 200:
                kpi_response = response_kpi.json()  # Parse the KPI response as JSON
            
            else:
                return generate_string("Error: Failed to contact the KPI engine. "+str(response_kpi.status_code) + " " + str(response_kpi.text))

        except Exception as e:  # Handle exceptions that occur during the API request
            print(f"An error occurred: {e}")

        # Step 8: Create the final response using the KPI data
        final_response = response_creation(query, kpi_response, response_3.get("kpi_name"))

    # Step 9: Return the structured final response
    return final_response


current_date = datetime.now().strftime("%Y-%m-%d")
embeddings, _ = faiss_generation()

app = Flask(__name__)

@app.route('/user-query', methods=['POST'])
def user_query():
    """
    Endpoint to handle user queries.

    It processes a POST request with a JSON body containing a 'query' field. 
    The query is processed using a FAISS vector store and retrieval pipeline 
    to return the most relevant results processes by the LLM.

    Returns:
        JSON: A structured response based on the query, or an error message.
    """
    try:
        # Step 1: Retrieve the JSON body from the request
        data = request.get_json()

        # Step 2: Validate the JSON payload to ensure the 'query' parameter is provided
        if 'query' not in data:
            return jsonify({"error": "Query parameter is required"}), 400
            # Return a 400 Bad Request error if 'query' is missing.

        # Step 3: Extract the query from the request data
        query = data['query']

        # Step 4: Load the FAISS vector store for retrieval
        vector_store = FAISS.load_local(
            "/app/Milestone3/vector_store",  # Path to the saved FAISS vector store
            HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"), 
            # Use HuggingFace embeddings for text similarity
            allow_dangerous_deserialization=True  # Allow loading potentially unsafe serialized data (use with caution)
        )

        # Step 5: Convert the FAISS vector store into a retriever
        retriever = vector_store.as_retriever()

        # Step 6: Retrieve relevant context documents based on the query
        context_docs = retriever.invoke(query)  # Query the retriever for relevant documents

        # Combine the retrieved documents' content into a single context string
        context = " ".join([doc.page_content for doc in context_docs])

        # Step 7: Process the query using the pipeline defined in `steps` function
        response = steps(query, context, current_date)

        # Step 8: Return the final response as a JSON object with a 200 OK status
        return jsonify(response), 200

    except Exception as e:
        # Step 9: Log any unexpected errors with detailed information
        logging.error("An error occurred: ", exc_info=True, stack_info=True)
        # Return a 500 Internal Server Error response with the error message
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the Flask application on all available network interfaces (0.0.0.0)
    # Port 5001 is used to host the API
    # Debug mode is disabled for production use
    app.run(host='0.0.0.0', port=5001, debug=False)







