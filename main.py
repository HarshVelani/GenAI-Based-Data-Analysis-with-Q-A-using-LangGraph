from my_agent.WorkflowManager import WorkflowManager

run = WorkflowManager()

# for deployment on langgraph cloud
graph = WorkflowManager().returnGraph()
    
question = input("Enter your question: ")
path = "Churn_Modelling.csv"
# path = "Updated_Red_Chilli_AP_GTR.csv"
# path = "cardekho_dataset.csv"
graph.invoke({"question": question, "path": path})