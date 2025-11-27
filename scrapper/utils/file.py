"""Module used to merge and export data, and detect duplicates."""

import json
import csv
from itertools import chain, starmap


def merge_json_files(file_name, n_files=1):
    """Merges a set of indexed JSON files (1, 2, ..., n) into a new one.

    Args:
        file_name (str): Name of the file to be merged without their indexes and extension.
        n_files (int): Amount of files to be merged.

    Returns:
        The merged file.

    """

    # Creates the data object and its `wines` array
    data = {}
    data['wines'] = []

    # Iterates through every possible file
    for i in range(n_files):
        try:
            # Opens the input file
            with open(f'{i+1}_{file_name}', 'r', encoding='utf-8') as f:
                # Loads the temporary data
                tmp_data = json.load(f)

                # Merges the data
                data['wines'] += tmp_data.get('wines', [])
                
                print(f"Merged {i+1}_{file_name}: {len(tmp_data.get('wines', []))} wines")

            # Closes the file
            f.close()
        except FileNotFoundError:
            print(f"Warning: File {i+1}_{file_name} not found, skipping...")
        except Exception as e:
            print(f"Error processing {i+1}_{file_name}: {e}")

    print(f"\nTotal wines merged: {len(data['wines'])}")
    
    # Remove duplicates based on id and vintage combination
    unique_wines = {}
    for wine in data['wines']:
        # Create a unique key combining id and vintage
        key = (wine.get('id'), wine.get('vintage'))
        if key not in unique_wines:
            unique_wines[key] = wine
    
    data['wines'] = list(unique_wines.values())
    print(f"Unique wines after deduplication: {len(data['wines'])}")

    # Opens the output file
    with open(f'{file_name}', 'w', encoding='utf-8') as f:
        # Dumps the merged data (FIXED: was tmp_data, now data)
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully created {file_name}")
    
    return data


def flatten_json_file(json_file):
    """Flattens a multi-level nested JSON file.

    Args:
        json_file (str): Name of the file to be loaded and flattened.

    Returns:
        List containing every flattened record from JSON file.

    """

    def _depack(key, value):
        # Checks whether value is a dictionary
        if isinstance(value, dict):
            # Iterates for every key and value
            for k, v in value.items():
                # Creates a new key string
                new_k = f'{key}_{k}'

                yield new_k, v

        # Checks whether value is a list
        elif isinstance(value, list):
            # Iterates through every value
            for i, v in enumerate(value):
                # Creates a new key string
                new_k = f'{key}_{i}'

                yield new_k, v

        # If the key is not nested
        else:
            yield key, value

    # Opens the JSON file
    with open(json_file, 'r') as f:
        # Loads the JSON file
        json_data = json.load(f)

    # Instantiates a list that will hold every unpacked data
    json_data_list = []

    # Iterates through every sample in the data
    for json_datum in json_data:
        # Performs an all-time true loop
        while True:
            # Unpacks the file
            json_datum = dict(chain.from_iterable(starmap(_depack, json_datum.items())))

            # Creates a loop-break condition
            if not any(isinstance(value, (dict, list)) for value in json_datum.values()):
                break

        # Appends to the list
        json_data_list.append(json_datum)

    return json_data_list


def json_to_csv(json_file, csv_file=None):
    """Converts a JSON file with wine data to CSV format.

    Args:
        json_file (str): Path to the input JSON file.
        csv_file (str): Path to the output CSV file. If None, uses json_file name with .csv extension.

    Returns:
        None

    """

    # If no CSV filename provided, generate one from the JSON filename
    if csv_file is None:
        csv_file = json_file.replace('.json', '.csv')

    # Open and load the JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Get the list of wines
    wines = data.get('wines', [])

    if not wines:
        print("No wines found in JSON file")
        return
    
    # Remove duplicates based on id and vintage combination
    print(f"Total wines before deduplication: {len(wines)}")
    unique_wines = {}
    for wine in wines:
        # Create a unique key combining id and vintage
        key = (wine.get('id'), wine.get('vintage'))
        if key not in unique_wines:
            unique_wines[key] = wine
    
    wines = list(unique_wines.values())
    print(f"Unique wines after deduplication: {len(wines)}")

    # Define the CSV headers based on the wine data structure
    headers = [
        'id', 'name', 'vintage', 'country', 'winery', 'grapes',
        'rating', 'price', 'acidity', 'intensity', 'sweetness', 'tannin',
        'flavor_rank1', 'flavor_rank2', 'flavor_rank3'
    ]

    # Write to CSV file
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)

        # Write header
        writer.writeheader()

        # Write each wine record
        for wine in wines:
            # Create a row with only the headers we want
            row = {header: wine.get(header) for header in headers}
            writer.writerow(row)

    print(f"Successfully converted {json_file} to {csv_file}")
    print(f"Total rows in CSV: {len(wines)} (excluding header)")


# Example usage - uncomment to run
merge_json_files("25-11-2025.json", 228)
json_to_csv("25-11-2025.json", "25-11-2025.csv")
