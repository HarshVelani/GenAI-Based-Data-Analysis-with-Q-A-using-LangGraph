from langgraph.graph import StateGraph
from my_agent.State import InputState, OutputState
from my_agent.DataAgent import DataAgent
from my_agent.DataVisualizer import DataVisualizer
from langgraph.graph import END

class WorkflowManager:
    def __init__(self):
        self.sql_agent = DataAgent()
        self.data_visualizer = DataVisualizer()

    def create_workflow(self) -> StateGraph:
        """Create and configure the workflow graph."""
        workflow = StateGraph(input=InputState, output=OutputState)

        # Add nodes to the graph
        workflow.add_node("parse_question", self.sql_agent.parse_question)
        workflow.add_node("get_unique_nouns", self.sql_agent.get_unique_nouns)
        workflow.add_node("filter_data", self.sql_agent.filter_data)
        workflow.add_node("format_results", self.sql_agent.format_results)
        workflow.add_node("choose_visualization", self.sql_agent.choose_visualization)
        workflow.add_node("visualization_generator", self.data_visualizer.generate_visualization)
        
        # Define edges
        workflow.add_edge("parse_question", "get_unique_nouns")
        workflow.add_edge("get_unique_nouns", "filter_data")
        workflow.add_edge("filter_data", "format_results")
        workflow.add_edge("filter_data", "choose_visualization")
        workflow.add_edge("choose_visualization", "visualization_generator")
        workflow.add_edge("visualization_generator", END)
        workflow.add_edge("format_results", END)
        workflow.set_entry_point("parse_question")

        return workflow
    
    def returnGraph(self):
        return self.create_workflow().compile()

    def run_sql_agent(self, question: str) -> dict:
        """Run the SQL agent workflow and return the formatted answer and visualization recommendation."""
        app = self.create_workflow().compile()

        result = app.invoke({"question": question})
        return {
            "answer": result['answer'],
            "visualization": result['visualization'],
            "visualization_reason": result['visualization_reason'],
            "visualization_code": result['visualization_code']
        }