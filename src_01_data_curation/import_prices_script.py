#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Import Prices Data Script
This script imports and cleans data from import price Excel files
"""

# Import necessary libraries
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# Display settings
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 50)

# Define file paths
base_path = "/Users/adam/Library/Mobile Documents/com~apple~CloudDocs/School/Master's Thesis/Analysis/profit-margins-inflation"
PRICES_FILE = os.path.join(base_path, 'data/source_raw/economy/import_prices/CEN07STALEVAHY.xlsx')
AA_FILE = os.path.join(base_path, 'data/source_raw/economy/import_prices/CEN07AA-112-2.xlsx')

# Check if files exist
if os.path.exists(PRICES_FILE):
    print(f"File found: {PRICES_FILE}")
else:
    print(f"File not found: {PRICES_FILE}")
    
if os.path.exists(AA_FILE):
    print(f"File found: {AA_FILE}")
else:
    print(f"File not found: {AA_FILE}")

# Import and clean fixed weights data from CEN07STALEVAHY.xlsx
def import_fixed_weights(file_path):
    # Based on our examination, we need to skip the first 5 rows and select only relevant columns
    df = pd.read_excel(file_path, sheet_name='DATA', skiprows=5)
    
    # Select relevant columns (SITC, Title, and the weight columns for different years)
    # Column indices: 1=SITC, 2=Title, 3=2021 weight, 4=2015 weight, 5=2010 weight, 6=2005 weight
    df = df.iloc[:, 1:7].copy()
    
    # Rename the columns
    df.columns = ['SITC', 'Title', 'weight_2021', 'weight_2015', 'weight_2010', 'weight_2005']
    
    # Filter out rows that don't contain useful data (footer rows, etc.)
    df = df[df['SITC'].notna() & ~df['SITC'].str.contains('Code:', na=False)]
    
    # Split data into export and import weights
    # Find the row index where 'Import total' starts
    import_start_idx = df[df['Title'] == 'Import total'].index[0]
    
    # Split the dataframe
    export_weights = df[:import_start_idx].copy()
    import_weights = df[import_start_idx:].copy()
    
    # Add type column to distinguish export vs import
    export_weights['type'] = 'export'
    import_weights['type'] = 'import'
    
    # Combine back together
    all_weights = pd.concat([export_weights, import_weights], axis=0)
    
    # Reset index
    all_weights = all_weights.reset_index(drop=True)
    
    return all_weights

# Import and clean import prices data (2015=100) from CEN07AA-112-2.xlsx
def import_prices_data(file_path):
    # Based on our examination, we need to skip the first 5 rows
    df = pd.read_excel(file_path, sheet_name='DATA', skiprows=5)
    
    # Since we're only interested in the import prices (as per the comment in the first cell),
    # we'll filter and reshape the dataframe
    
    # First, select all columns from 'SITC' (column 2) onwards, dropping the first column
    df = df.iloc[:, 1:].copy()
    
    # The first row contains "Import" in the first column
    # The third row contains "SITC" in the first column and years in the other columns
    # Let's extract column headers (years) from the third row
    years = df.iloc[2, 2:].values  # Get year values starting from column 3
    
    # Extract SITC names and codes
    # Start from row 4 (index 3) and take only rows until 'Code:' appears (which marks the end of data)
    data_end_idx = df[df.iloc[:, 0].astype(str).str.contains('Code:', na=False)].index[0]
    
    # Extract the actual price data
    price_data = df.iloc[3:data_end_idx].copy()  # Extract rows with actual data
    
    # Rename columns
    price_data.columns = ['Category', 'Name'] + [str(int(year)) if not pd.isna(year) else f'Year{i}' 
                                               for i, year in enumerate(years)]
    
    # Drop rows with NaN in the Category column
    price_data = price_data[price_data['Category'].notna()]
    
    # Melt the dataframe to convert from wide to long format
    price_data_long = pd.melt(
        price_data,
        id_vars=['Category', 'Name'],
        value_vars=[col for col in price_data.columns if col not in ['Category', 'Name']],
        var_name='Year',
        value_name='Price_Index'
    )
    
    # Convert Year column to integer (handle any non-numeric years appropriately)
    price_data_long['Year'] = pd.to_numeric(price_data_long['Year'], errors='coerce')
    
    # Drop rows with NaN in Year or Price_Index
    price_data_long = price_data_long.dropna(subset=['Year', 'Price_Index'])
    
    # Reset index
    price_data_long = price_data_long.reset_index(drop=True)
    
    return price_data_long

# Import the data
print("\n--- Importing and cleaning data ---")
fixed_weights = import_fixed_weights(PRICES_FILE)
import_prices = import_prices_data(AA_FILE)

# Display the first few rows to verify
print("\nImport/Export weights data:")
print(fixed_weights.head(10))
print("\nImport weights:")
print(fixed_weights[fixed_weights['type'] == 'import'].head(5))
print("\nImport prices data (long format):")
print(import_prices.head(10))

# Also create a pivot version for easier time series analysis
import_prices_pivot = import_prices.pivot_table(
    index=['Category', 'Name'],
    columns='Year',
    values='Price_Index'
).reset_index()

print("\nImport prices data (pivoted):")
print(import_prices_pivot.head(5))

# Final data cleaning
print("\n--- Final data cleaning and saving ---")

# 1. Fix any data type issues in the weights dataset
fixed_weights['SITC'] = fixed_weights['SITC'].astype(str)
for col in ['weight_2021', 'weight_2015', 'weight_2010', 'weight_2005']:
    fixed_weights[col] = pd.to_numeric(fixed_weights[col], errors='coerce')

# 2. Fix any data type issues in the prices dataset
import_prices['Category'] = import_prices['Category'].astype(str)
import_prices['Year'] = import_prices['Year'].astype(int)
import_prices['Price_Index'] = pd.to_numeric(import_prices['Price_Index'], errors='coerce')

# 3. Create clean output directory if it doesn't exist
output_dir = os.path.join(base_path, 'data/source_cleaned')
os.makedirs(output_dir, exist_ok=True)

# 4. Save the cleaned data to parquet files
import_weights_file = os.path.join(output_dir, 'import_weights.parquet')
import_prices_file = os.path.join(output_dir, 'import_prices.parquet')

# Save only import weights (filter by type='import')
fixed_weights[fixed_weights['type'] == 'import'].to_parquet(import_weights_file)

# Save import prices
import_prices.to_parquet(import_prices_file)

print(f"Saved import weights to: {import_weights_file}")
print(f"Saved import prices to: {import_prices_file}")

# Also save a CSV version for easy inspection
fixed_weights[fixed_weights['type'] == 'import'].to_csv(
    os.path.join(output_dir, 'import_weights.csv'), index=False
)
import_prices.to_csv(
    os.path.join(output_dir, 'import_prices.csv'), index=False
)

# Print summary statistics
print("\nSummary of import weights data:")
print(fixed_weights[fixed_weights['type'] == 'import'].describe())

print("\nSummary of import prices data:")
print(import_prices.describe())

# Count the number of unique SITC categories in both datasets
num_weight_categories = fixed_weights[fixed_weights['type'] == 'import']['SITC'].nunique()
num_price_categories = import_prices['Category'].nunique()

print(f"\nNumber of unique SITC categories in weights data: {num_weight_categories}")
print(f"Number of unique SITC categories in prices data: {num_price_categories}")

print("\n--- Script execution completed ---")
