from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from my_agent.DatabaseManager import DatabaseManager
from my_agent.LLMManager import LLMManager
import pandas as pd

class SQLAgent:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.llm_manager = LLMManager()

    def parse_question(self, state: dict) -> dict:
        """Parse user question and identify relevant columns."""
        question = state['question']
        path = state['path']
        
        data = self.db_manager.get_data(path)
        df = data
        columns = df.columns.tolist()
        # print(f"Columns: {columns}")
        print("===Data columns===")


        prompt = ChatPromptTemplate.from_messages([
            ("system", '''You are a data analyst that can help summarize pandas dataframe and parse user questions about a data. 
Given the question and data column names, identify all the relevant tables and columns. 
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
            ("human", "===Data columns:\n{columns}\n\n===User question:\n{question}\n\nIdentify relevant tables and columns:")
        ])

        output_parser = JsonOutputParser()
        
        response = self.llm_manager.invoke(prompt, columns=columns, question=question)
        parsed_response = output_parser.parse(response)
        print(f">>>>> Parsed response: {parsed_response}")
        print(f"===Relevant Columns===")
        return {"parsed_question": parsed_response}

    def get_unique_nouns(self, state: dict) -> dict:
        """Find unique nouns in relevant tables and columns."""
        parsed_question = state['parsed_question']
        
        if not parsed_question['is_relevant']:
            return {"unique_nouns": []}

        unique_nouns = set()
        for table_info in parsed_question['relevant_tables']:
            noun_columns = table_info['columns']
            
            if noun_columns:
                unique_nouns = list(set(noun_columns))

        print(f"\n>>>>> Relevant Columns: {unique_nouns}")
        return {"unique_nouns": unique_nouns}

    def filter_data(self, state: dict) -> dict:
        """Execute SQL query and return results."""

        parsed_question = state['parsed_question']
        unique_nouns = state['unique_nouns']
        path = state['path']

        data = self.db_manager.get_data(path)
        df = data
        
        if not parsed_question['is_relevant']:
            return {"results": "NOT_RELEVANT"}

        try:
            results = df[unique_nouns]
            # print(results)
            print(f"\n===Filtered Data===")
            return {"results": results.to_json(orient="records")}
            
        except Exception as e:
            return {"error": str(e)}

    def format_results(self, state: dict) -> dict:
        """Format query results into a human-readable response."""
        question = state['question']
        # print(f"results: {state["results"]}")
        
        if "results" not in state:
            print("Error: 'results' key missing in state")

        elif state["results"] == "NOT_RELEVANT":
            return {"answer": "Sorry, I can only give answers relevant to the database."}

        results = pd.read_json(state["results"])
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an AI assistant that formats user query results into a human-readable response. Give a conclusion to the user's question based on the query results. Do not give the answer in markdown format. Only give the answer in one line."),
            ("human", "User question: {question}\n\nQuery results: {results}\n\nFormatted response:"),
        ])

        response = self.llm_manager.invoke(prompt, question=question, results=results)
        print(f"\n>>>>> Formatted response: {response}")
        return {"answer": response}

    def choose_visualization(self, state: dict) -> dict:
        """Choose an appropriate visualization for the data."""
        question = state['question']
        results = pd.read_json(state["results"])

        if state["results"] == "NOT_RELEVANT":
            return {"visualization": "none", "visualization_reasoning": "No visualization needed for irrelevant questions."}

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
                Reason: [Brief explanation for your recommendation and explain the conditions for data preprocessing to make the suitable chart in matplotlib. For example, "the needs to be grouped by with specific columns, remove null values, conditions like greater, less than, equal to, etc. and sorted by a specific column."].
                    
                Your response should be in the following JSON format:
                {{
                    "visualization": string,
                    "reason": string
                }}
                '''),
            ("human", '''
                User question: {question}
                Query results: {results}

                Recommend a visualization:
                Your response should be in the following JSON format:
                {{
                    "visualization": string,
                    "reason": string
                }}
             '''),
        ])

        output_parser = JsonOutputParser()
        
        response = self.llm_manager.invoke(prompt, question=question, results=results)
        parsed_response = output_parser.parse(response)

        visualization = parsed_response['visualization']
        reason = parsed_response['reason']
        print(f"\n>>>>> Visualization: {visualization}")
        print(f"\n>>>>> Reason: {reason}")

        return {"visualization": visualization, "visualization_reason": reason}