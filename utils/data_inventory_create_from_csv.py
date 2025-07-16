import csv
import json
import os

def create_data_inventory(csv_path, json_path):
    """
    Reads a structured CSV file and creates a JSON data inventory.

    The CSV is expected to have section headers and variable definitions.
    This function parses the CSV and creates a structured JSON file.
    """
    data_inventory = {
        "data_inventory_description": "This file contains a detailed inventory of all variables in the merged panel dataset. It is structured by variable category, based on the merged_panel_inventory.csv file.",
        "categories": []
    }
    current_category = None
    
    # The CSV file seems to have some encoding issues, trying 'utf-8-sig' to handle potential BOM
    with open(csv_path, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile)
        header = [h.strip() for h in next(reader)]

        for row in reader:
            if not any(field.strip() for field in row):
                continue # Skip empty rows

            # Check for a category header row
            if row[0] and all(not item for item in row[1:]):
                category_name = row[0].strip()
                # Heuristic to remove numbering like "1. "
                if '. ' in category_name and category_name.split('. ', 1)[0].isdigit():
                    category_name = category_name.split('. ', 1)[1]

                current_category = {
                    "category_name": category_name,
                    "variables": []
                }
                data_inventory["categories"].append(current_category)
                continue

            # Check for a variable row
            if current_category is not None and row[0] and row[1]:
                # Skip rows that look like subheaders or repeated main headers
                if row[0].lower().strip() == 'variable name (short)':
                    continue

                variable = {
                    "name": row[0].strip(),
                    "description": row[1].strip(),
                    "unit": row[2].strip(),
                    "source": row[3].strip()
                }
                current_category["variables"].append(variable)

    with open(json_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(data_inventory, jsonfile, indent=4, ensure_ascii=False)

    print(f"Successfully created data inventory at {json_path}")

def test_inventory(json_path):
    """
    Tests the created data inventory file.
    """
    print(f"\n--- Testing {json_path} ---")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert "data_inventory_description" in data
        assert "categories" in data
        assert len(data["categories"]) > 0
        
        print("Test passed: JSON structure is valid.")
        print(f"Found {len(data['categories'])} categories.")
        
        for i, category in enumerate(data['categories']):
            print(f"  Category {i+1}: '{category['category_name']}' has {len(category['variables'])} variables.")

    except FileNotFoundError:
        print(f"Test failed: File not found at {json_path}")
    except json.JSONDecodeError:
        print(f"Test failed: Not a valid JSON file at {json_path}")
    except AssertionError as e:
        print(f"Test failed: {e}")
    print("--- Test complete ---")


if __name__ == "__main__":
    # Get the absolute path of the script
    script_path = os.path.abspath(__file__)
    # Get the directory containing the script
    script_dir = os.path.dirname(script_path)
    # The project root is one level up from the script directory's parent
    project_root = os.path.dirname(script_dir)
    
    csv_file_path = os.path.join(project_root, 'docs', 'merged_panel_inventory.csv')
    json_file_path = os.path.join(project_root, 'data_inventory.json')
    
    create_data_inventory(csv_file_path, json_file_path)
    test_inventory(json_file_path)
