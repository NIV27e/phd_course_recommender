import os
import json
import pandas as pd
from PhDParser import PhDParser

def run_parser(discipline, keywords, output_path):
    parser = PhDParser(discipline=discipline, keywords=keywords)
    parser.saveCurrentAsJson(file_path=output_path)

def convert_json_to_csv(json_path, csv_path):
    with open(json_path) as json_file:
        data = json.load(json_file)

    # Define headers
    headers = [
        "title", "description", "date_updated", "deadline",
        "access_time", "funding", "link", "country", "university", "location"
    ]

    # Create a list of dicts
    rows = []
    for key, value in data.items():
        row = {
            "title": key,
            "description": value.get("description", ""),
            "date_updated": value.get("date_updated", ""),
            "deadline": value.get("deadline", ""),
            "access_time": value.get("access_time", ""),
            "funding": value.get("funding", ""),
            "link": value.get("link", ""),
            "country": value.get("country", ""),
            "university": value.get("university", ""),
            "location": value.get("location", "")  # Ensure location is included
        }
        rows.append(row)

    # Convert to DataFrame and save as CSV
    df = pd.DataFrame(rows, columns=headers)
    df.to_csv(csv_path, index=False)

if __name__ == "__main__":
    # Define the discipline and keywords for the search
    discipline = input("Enter the discipline (e.g., 'computer science'): ").strip().lower()
    keywords = input("Enter keywords (comma separated, leave empty for none): ").strip()

    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_output_path = os.path.join(base_dir, 'phd_courses.json')
    csv_output_path = os.path.join(base_dir, 'phd_courses.csv')

    # Run the parser and save the output as JSON
    run_parser(discipline, keywords, json_output_path)

    # Convert the JSON output to CSV
    convert_json_to_csv(json_output_path, csv_output_path)

    print(f"Data saved to {csv_output_path}")
