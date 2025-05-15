# SQLAgent.py

###### def parse_question

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from my_agent.DatabaseManager import DatabaseManager
from my_agent.LLMManager import LLMManager
import pandas as pd
import VS_code
import os

db_manager = DatabaseManager()
llm_manager = LLMManager()

question = "give car model whose age is greater than 10 years."
path = "cardekho_dataset.csv"
data = db_manager.get_data(path)

df = data 
columns = df.columns.tolist()
print(f"Columns: {columns}")

prompt = ChatPromptTemplate.from_messages([
            ("system", '''You are a data analyst that can help summarize pandas dataframe and parse user questions about a data. 
Given the question and pandas dataframe, identify the relevant tables and columns. 
If the question is not relevant to the dataframe or if there is not enough information to answer the question, set is_relevant to false.

Your response should be in the following JSON format:
{{
    "is_relevant": boolean,
    "relevant_tables": [
        {{
            "table_name": string,
            "columns": [string],
            "noun_columns": [string]
        }}
    ]
}}

The "noun_columns" field should contain only the columns that are relevant to the question and contain nouns or names, for example, the column "Artist name" contains nouns relevant to the question "What are the top selling artists?", but the column "Artist ID" is not relevant because it does not contain a noun. Do not include columns that contain numbers.
'''),
            ("human", "===Data columns:\n{schema}\n\n===User question:\n{question}\n\nIdentify relevant tables and columns:")
        ])

output_parser = JsonOutputParser()
        
response = llm_manager.invoke(prompt, schema=columns, question=question)
parsed_response = output_parser.parse(response)
print(f"Parsed response: {parsed_response}")







############# def get_unique_nouns:

parsed_question = parsed_response
        
if not parsed_question['is_relevant']:
    unique_nouns = {"unique_nouns": []}

unique_nouns = set()
for table_info in parsed_question['relevant_tables']:
    table_name = table_info['table_name']
    noun_columns = table_info['columns']
    print(f"Table: {table_name}, Noun Columns: {noun_columns}")
    if noun_columns:
        unique_nouns = list(noun_columns)

print(f"unique_nouns: {unique_nouns}")








################### def excecute_sql:


if not parsed_question['is_relevant']:
    results = {"results": "NOT_RELEVANT"}
    print(results)
try:
    results = df[unique_nouns]
    results = {"results": results}
    print(results)
except Exception as e:
    print({"error": str(e)})







################# def format_results:

"""Format query results into a human-readable response."""


if results == "NOT_RELEVANT":
    print({"answer": "Sorry, I can only give answers relevant to the database."})

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AI assistant that formats user query results into a human-readable response. Give a conclusion to the user's question based on the query results. Do not give the answer in markdown format. Only give the answer in one line."),
    ("human", "User question: {question}\n\nQuery results: {results}\n\nFormatted response:"),
])

response = llm_manager.invoke(prompt, question=question, results=results)
print({"answer": response})






################## def choose_visualization:

"""Choose an appropriate visualization for the data."""

if results == "NOT_RELEVANT":
    print({"visualization": "none", "visualization_reasoning": "No visualization needed for irrelevant questions."})

prompt = ChatPromptTemplate.from_messages([
    ("system", '''
        You are an AI assistant that recommends appropriate data visualizations. Based on the user's question, and query results, suggest the most suitable type of graph or chart to visualize the data. If no visualization is appropriate, indicate that.

        Available chart types and their use cases:
        - Bar Graphs: Best for comparing categorical data or showing changes over time when categories are discrete and the number of categories is more than 2. Use for questions like "What are the sales figures for each product?" or "How does the population of cities compare? or "What percentage of each city is male?"
        - Horizontal Bar Graphs: Best for comparing categorical data or showing changes over time when the number of categories is small or the disparity between categories is large. Use for questions like "Show the revenue of A and B?" or "How does the population of 2 cities compare?" or "How many men and women got promoted?" or "What percentage of men and what percentage of women got promoted?" when the disparity between categories is large.
        - Scatter Plots: Useful for identifying relationships or correlations between two numerical variables or plotting distributions of data. Best used when both x axis and y axis are continuous. Use for questions like "Plot a distribution of the fares (where the x axis is the fare and the y axis is the count of people who paid that fare)" or "Is there a relationship between advertising spend and sales?" or "How do height and weight correlate in the dataset? Do not use it for questions that do not have a continuous x axis."
        - Pie Charts: Ideal for showing proportions or percentages within a whole. Use for questions like "What is the market share distribution among different companies?" or "What percentage of the total revenue comes from each product?"
        - Line Graphs: Best for showing trends and distributionsover time. Best used when both x axis and y axis are continuous. Used for questions like "How have website visits changed over the year?" or "What is the trend in temperature over the past decade?". Do not use it for questions that do not have a continuous x axis or a time based x axis.

        Consider these types of questions when recommending a visualization:
        1. Aggregations and Summarizations (e.g., "What is the average revenue by month?" - Line Graph)
        2. Comparisons (e.g., "Compare the sales figures of Product A and Product B over the last year." - Line or Column Graph)
        3. Plotting Distributions (e.g., "Plot a distribution of the age of users" - Scatter Plot)
        4. Trends Over Time (e.g., "What is the trend in the number of active users over the past year?" - Line Graph)
        5. Proportions (e.g., "What is the market share of the products?" - Pie Chart)
        6. Correlations (e.g., "Is there a correlation between marketing spend and revenue?" - Scatter Plot)


        Recommended Visualization: [Chart type or "None"]. ONLY use the following names: bar, horizontal_bar, line, pie, scatter, none
        Reason: [Brief explanation for your recommendation]
            
        Your response should be in the following JSON format:
        {{
            "visualization": string,
            "reason": string
        }}
'''),
            ("human", '''
                User question: {question}
                Query results: {results}

                Recommend a visualization:'''),
        ])

output_parser = JsonOutputParser()
        
response = llm_manager.invoke(prompt, question=question, results=results)
parsed_response = output_parser.parse(response)
print(f"Parsed response: {parsed_response}")

visualization = parsed_response['visualization']
reason = parsed_response['reason']

print({"visualization": parsed_response['visualization'], "visualization_reason": parsed_response['reason']})









## DataVisualizer

################# def code_generator_for_visualization:
"""Generates code for the specified visualization."""

if results == "NOT_RELEVANT":
    print({"visualization": "none", "visualization_reasoning": "No visualization needed for irrelevant questions."})

prompt = ChatPromptTemplate.from_messages([
    ("system", '''
You are an intelligent code generator for matplotlib that can generate code for data visualization. Based on the user's prompt, data and  type of chart specified, generate the code for the chart that is defined by user.
the code should include x and y axis labels, title and legend.
code should be in python and should be executable with indentation.
here data is in Pandas dataframe format.
give only the code without any explanation or comments.
Do not generate any Data.
use data according to the column names provided{datacolumns}.
Data should be read from the variable "data" which is a pandas dataframe.
Strictly chart should be saved as a png file with the name "filename.png". Give meaningful filename.
code should not contain any errors while running. it should be executable.
code should include below lines:
from my_agent.DatabaseManager import DatabaseManager
db_manager = DatabaseManager()
data = db_manager.get_data({datapath})'''),
            ("human", "===Data columns:\n{datacolumns}\n\n===Type Of Chart:\n{visualization}\n\n===prompt:\n{userprompt}\n\nGenerate code for the visualization:")
        ])

response = llm_manager.invoke(prompt, datacolumns=unique_nouns, visualization=parsed_response['visualization'], userprompt=reason, datapath=path)
print(response)


with open('VS_code.py', 'w') as f:
    codes = response.split('\n')
    code = "\n".join(codes[1:-1])
    f.write(code)

os.system('python VS_code.py')