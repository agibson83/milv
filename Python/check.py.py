import pandas as pd

# Load the CSV files
productivity_df = pd.read_csv('C:/Users/aliso/OneDrive/Desktop/MILV/Python/Productivity_with_sections.csv', low_memory=False)
volume_df = pd.read_csv('C:/Users/aliso/OneDrive/Desktop/MILV/Python/Volume.csv')

# Print column names
print("Productivity Columns:", productivity_df.columns.tolist())
print("Volume Columns:", volume_df.columns.tolist())
