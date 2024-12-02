import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# File paths
productivity_file = r'C:\Users\aliso\OneDrive\Desktop\MILV\Python\Productivity_with_sections.csv'
volume_file = r'C:\Users\aliso\OneDrive\Desktop\MILV\Python\Volume.csv'

# Load the data
productivity_df = pd.read_csv(productivity_file, low_memory=False)
volume_df = pd.read_csv(volume_file)

# Merge the datasets on 'Accession'
merged_df = pd.merge(productivity_df, volume_df, on='Accession', how='inner')

# Calculate Turnaround Time
merged_df['Turnaround_Time'] = pd.to_datetime(merged_df['End_Time']) - pd.to_datetime(merged_df['Start_Time'])
merged_df['Turnaround_Time_in_Hours'] = merged_df['Turnaround_Time'].dt.total_seconds() / 3600

# Calculate average turnaround time
average_turnaround = merged_df['Turnaround_Time_in_Hours'].mean()

# Filter rows with above-average turnaround times
above_average_df = merged_df[merged_df['Turnaround_Time_in_Hours'] > average_turnaround]

# Save the filtered data to a CSV
above_average_file = r'C:\Users\aliso\OneDrive\Desktop\MILV\Python\Above_Average_Turnaround.csv'
above_average_df.to_csv(above_average_file, index=False)
print(f"Filtered data saved to {above_average_file}")

# Create a historical visualization
merged_df['Date'] = pd.to_datetime(merged_df['Start_Time']).dt.date
daily_avg = merged_df.groupby('Date')['Turnaround_Time_in_Hours'].mean()

plt.figure(figsize=(10, 6))
plt.plot(daily_avg.index, daily_avg.values, marker='o')
plt.title('Daily Average Turnaround Time')
plt.xlabel('Date')
plt.ylabel('Average Turnaround Time (Hours)')
plt.grid()
plt.savefig(r'C:\Users\aliso\OneDrive\Desktop\MILV\Python\Turnaround_Time_Trend.png')
print("Trend visualization saved as 'Turnaround_Time_Trend.png'")
