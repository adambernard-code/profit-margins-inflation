import os
import pandas as pd
from datetime import datetime

# Define file paths

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, ".."))

input_file = os.path.join(project_root, "data", "source_raw", "export-7.csv")
output_folder = os.path.join(project_root, "data", "quality_reports")

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Read the CSV file with semicolon delimiter and proper quoting
df = pd.read_csv(input_file, delimiter=';', quotechar='"')

# Prepare a list to store quality metrics for each column
quality_metrics = []

# Total number of rows in the dataset
total_count = len(df)

# Iterate over each column in the DataFrame
for col in df.columns:
    col_data = df[col]
    # Compute basic metrics
    non_missing_count = col_data.count()
    missing_count = total_count - non_missing_count
    missing_percentage = (missing_count / total_count) * 100
    unique_count = col_data.nunique(dropna=True)
    data_type = col_data.dtype

    # Initialize default stats for numeric columns
    min_val = max_val = mean_val = std_val = None

    if pd.api.types.is_numeric_dtype(col_data):
        min_val = col_data.min()
        max_val = col_data.max()
        mean_val = col_data.mean()
        std_val = col_data.std()

    quality_metrics.append({
        "Column Name": col,
        "Data Type": data_type,
        "Total Count": total_count,
        "Non-Missing Count": non_missing_count,
        "Missing Count": missing_count,
        "Missing Percentage (%)": round(missing_percentage, 2),
        "Unique Count": unique_count,
        "Min": min_val,
        "Max": max_val,
        "Mean": mean_val,
        "Std": std_val
    })

# Create a DataFrame with quality metrics
quality_df = pd.DataFrame(quality_metrics)

# Create a timestamp for the output filename using format YYYYDDHHMM
timestamp = datetime.now().strftime("%Y%d%H%M")
output_filename = f"data_quality_report_{timestamp}.xlsx"
output_path = os.path.join(output_folder, output_filename)

# Write the quality report to an Excel file
quality_df.to_excel(output_path, index=False)

print(f"Data quality report has been saved to: {output_path}")
