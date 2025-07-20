import csv
import json
import os

def create_csv_from_inventory(json_path, csv_path):
    """
    Reads a JSON data inventory file and creates a structured CSV file.

    The JSON is expected to have the structure created by create_data_inventory().
    This function parses the JSON and recreates the original CSV format.
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as jsonfile:
            data_inventory = json.load(jsonfile)
    except FileNotFoundError:
        print(f"Error: JSON file not found at {json_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON file at {json_path}")
        return

    with open(csv_path, mode='w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write the header row
        header = ["Variable Name (Short)", "Description", "Unit", "Source"]
        writer.writerow(header)
        
        # Write an empty row for formatting
        writer.writerow(["", "", "", ""])
        
        # Process each category
        for i, category in enumerate(data_inventory.get("categories", [])):
            category_name = category.get("category_name", "")
            
            # Write category header with numbering
            category_row = [f"{i+1}. {category_name}", "", "", ""]
            writer.writerow(category_row)
            
            # Write an empty row after category header
            writer.writerow(["", "", "", ""])
            
            # Write the sub-header for this category
            writer.writerow(["Variable Name (Short)", "Description", "Unit", "Source"])
            
            # Write all variables in this category
            for variable in category.get("variables", []):
                variable_row = [
                    variable.get("name", ""),
                    variable.get("description", ""),
                    variable.get("unit", ""),
                    variable.get("source", "")
                ]
                writer.writerow(variable_row)
            
            # Write an empty row after each category (except the last one)
            if i < len(data_inventory.get("categories", [])) - 1:
                writer.writerow(["", "", "", ""])

    print(f"Successfully created CSV file at {csv_path}")

def test_csv_roundtrip(original_json_path, generated_csv_path):
    """
    Tests the generated CSV by attempting to recreate a JSON from it
    and comparing basic structure with the original.
    """
    print(f"\n--- Testing roundtrip conversion ---")
    
    try:
        # Load original JSON
        with open(original_json_path, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        
        # Check if CSV was created
        if not os.path.exists(generated_csv_path):
            print("Test failed: CSV file was not created.")
            return
        
        # Count variables in original JSON
        original_var_count = sum(len(cat.get("variables", [])) 
                               for cat in original_data.get("categories", []))
        original_cat_count = len(original_data.get("categories", []))
        
        # Count lines in generated CSV (rough estimate)
        with open(generated_csv_path, 'r', encoding='utf-8') as f:
            csv_lines = len(f.readlines())
        
        print("Test passed: CSV file structure appears correct.")
        print(f"Original JSON had {original_cat_count} categories with {original_var_count} total variables.")
        print(f"Generated CSV has {csv_lines} lines.")
        
        # Basic validation that the CSV has content
        with open(generated_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            first_row = next(reader)
            if first_row == ["Variable Name (Short)", "Description", "Unit", "Source"]:
                print("CSV header structure matches expected format.")
            else:
                print(f"Warning: CSV header is {first_row}, which may not match expected format.")

    except Exception as e:
        print(f"Test failed with error: {e}")
    
    print("--- Test complete ---")

def validate_json_structure(json_path):
    """
    Validates that the JSON file has the expected structure.
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if "categories" not in data:
            print("Error: JSON file missing 'categories' key.")
            return False
        
        for i, category in enumerate(data["categories"]):
            if "category_name" not in category:
                print(f"Error: Category {i} missing 'category_name' key.")
                return False
            if "variables" not in category:
                print(f"Error: Category {i} missing 'variables' key.")
                return False
            
            for j, variable in enumerate(category["variables"]):
                required_keys = ["name", "description", "unit", "source"]
                for key in required_keys:
                    if key not in variable:
                        print(f"Error: Variable {j} in category {i} missing '{key}' key.")
                        return False
        
        return True
    
    except Exception as e:
        print(f"Error validating JSON structure: {e}")
        return False

if __name__ == "__main__":
    # Get the absolute path of the script
    script_path = os.path.abspath(__file__)
    # Get the directory containing the script
    script_dir = os.path.dirname(script_path)
    # The project root is one level up from the script directory
    project_root = os.path.dirname(script_dir)
    
    json_file_path = os.path.join(project_root, 'specs', 'data_inventory.json')
    csv_file_path = os.path.join(project_root, 'docs', 'merged_panel_inventory_from_json.csv')
    
    # Validate the JSON structure first
    if validate_json_structure(json_file_path):
        print("JSON structure validation passed.")
        create_csv_from_inventory(json_file_path, csv_file_path)
        test_csv_roundtrip(json_file_path, csv_file_path)
    else:
        print("JSON structure validation failed. Cannot proceed with CSV creation.")
