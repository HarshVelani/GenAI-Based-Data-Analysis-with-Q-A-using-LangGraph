import json
from langchain_core.prompts import ChatPromptTemplate
from my_agent.LLMManager import LLMManager
from my_agent.DataManager import DataManager
from my_agent.graph_instructions import graph_instructions
import os
import pandas as pd

class DataVisualizer:
    def __init__(self):
        self.llm_manager = LLMManager()
        self.db_manager = DataManager()    

    def code_generator_for_visualization(self, datacolumns: list, visualization: str, reason: str, data: dict, path: str) -> str:
        """Generate code for the specified visualization."""
        
        data = pd.read_json(data)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", '''
            You are an intelligent code generator for Data analysis that can generate code for data visualization. Based on the user's prompt, data and  type of chart specified, generate the code for the chart that is defined by user.
            you will use matplotlib library for data visualization.
            Data should be read from the variable "data" which is a pandas dataframe and make preprocessing of data however needed and specified.
            the code should include x and y axis labels, title and legend.
            code should be in python and should be executable with indentation.
            here data is in Pandas dataframe format.
            give only the code without any explanation or comments.
            Do not generate any Data.
            use column names according to the column names provided{datacolumns}.
            Do not use this parameter in the code = "plt.gcf.transFigure".
            Strictly chart should be saved as a png file with the dynamic name "{visualization} + dynamic name.png".
            code should not contain any errors while running. it should be executable.
            code should include below lines:
            from my_agent.DataManager import DataManager
            db_manager = DataManager()
            data = db_manager.get_data({datapath})
            .
            .
             At lastline print the code with the message "=======> Chart Generated".'''),
            ("human", "===Data columns:\n{datacolumns}\n\n===Data Sample:\n{data}===Type Of Chart:\n{visualization}\n\n===prompt:\n{userprompt}\n\nGenerate code for the visualization:")
        ])
        
        response = self.llm_manager.invoke(prompt, datacolumns=datacolumns, visualization=visualization, userprompt= reason, datapath=path, data=data)
        print("\n====Visualization Code Generated====")
        return response
    
    def format_code_response(self, datacolumns: list, visualization: str, reason: str, data: dict, path: str) -> str:
        """Format the generated code for better readability."""

        # Here you can add any formatting logic you need
        response = self.code_generator_for_visualization(datacolumns, visualization, reason, data, path)

        with open('VS_code.py', 'w') as f:
            codes = response.split('\n')
            code = "\n".join(codes[1:-1])
            print("\n====Cleaned Code====")
            f.write(code)
        
        print(f"\n>>>>> Generated code:\n{code}")
        return code
    
    def generate_visualization(self, state: dict) -> str:
        """Generate the visualization code."""
        datacolumns = state['unique_nouns']
        visualization = state['visualization']
        reason = state['visualization_reason']
        path = state['path']
        df = pd.read_json(state['results']).head(10)
        
        print(f"\n====> Data: {df}")
        print("\n===Generating Code for Visualization===")
        data = df.to_json(orient="records")
        code = self.format_code_response(datacolumns, visualization, reason, data, path)

        print(f"\nGenerating Chart..........")
        os.system(f"python VS_code.py")
        print(f"\n********** Chart Generated **********")
        return {"visualization_code" : code}
    
# Generating Chart..........
# Data: Index(['Unnamed: 0', 'car name', 'brand', 'model', 'vehicle age', 'km driven',
#        'seller type', 'fuel type', 'transmission type', 'mileage', 'engine',
#        'max power', 'seats', 'selling price'],
#       dtype='object')
# Traceback (most recent call last):
#   File "E:\ViitorCloud\Projects\LangGraph_Data_Visualization\backend\VS_code.py", line 15, in <module>
#     plt.legend(title="Fuel Types", labels=fuel_type_counts.index, bbox_to_anchor=(1.05, 1), loc='upper left', bbox_transform=plt.gcf.transFigure)
#                                                                                                                              ^^^^^^^^^^^^^^^^^^^
# AttributeError: 'function' object has no attribute 'transFigure'