from my_agent.DatabaseManager import DatabaseManager
import matplotlib.pyplot as plt
import pandas as pd

db_manager = DatabaseManager()
data = db_manager.get_data('Churn_Modelling.csv')

data['Estimated Salary'] = pd.to_numeric(data['Estimated Salary'])

grouped_data = data.groupby('Gender')['Estimated Salary'].mean().reset_index()

plt.figure(figsize=(10,6))
plt.bar(grouped_data['Gender'], grouped_data['Estimated Salary'], color=['blue', 'red'])
plt.xlabel('Gender')
plt.ylabel('Average Estimated Salary')
plt.title('Average Estimated Salary by Gender')
plt.legend()
plt.savefig('bar_avg_salary_by_gender.png')
print("=======> Chart Generated")