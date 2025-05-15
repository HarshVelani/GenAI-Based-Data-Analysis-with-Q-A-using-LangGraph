from my_agent.DataManager import DataManager
import matplotlib.pyplot as plt
import pandas as pd

db_manager = DatabaseManager()
data = db_manager.get_data('Updated_Red_Chilli_AP_GTR.csv')

data['Date'] = pd.to_datetime(data['Date'])
data['Year'] = data['Date'].dt.year

yearly_avg_price = data.groupby('Year')['Price'].mean().reset_index()

plt.figure(figsize=(10,6))
plt.plot(yearly_avg_price['Year'], yearly_avg_price['Price'], marker='o')
plt.xlabel('Year')
plt.ylabel('Average Price')
plt.title('Trend of Average Price Over the Years')
plt.legend(['Average Price'])

plt.savefig(f'line_{"yearly_avg_price"}.png')
print("=======> Chart Generated")