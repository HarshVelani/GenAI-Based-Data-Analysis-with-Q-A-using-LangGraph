from my_agent.DatabaseManager import DatabaseManager
import matplotlib.pyplot as plt
import pandas as pd

db_manager = DatabaseManager()
data = db_manager.get_data('cardekho_dataset.csv')

data['vehicle age'] = pd.to_numeric(data['vehicle age'])
filtered_data = data[data['vehicle age'] > 10]

model_counts = filtered_data['model'].value_counts()

plt.figure(figsize=(10,6))
model_counts.plot(kind='bar')
plt.xlabel('Car Model')
plt.ylabel('Count')
plt.title('Distribution of Car Models > 10 Years Old')
plt.legend(title='Car Models')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('car_model_distribution.png')
plt.close()