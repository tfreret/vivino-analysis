import argparse
import json

import utils.constants as c
from utils.requester import Requester


def get_arguments():
    """Gets arguments from the command line.

    Returns:
        A parser with the input arguments.

    """

    parser = argparse.ArgumentParser(usage='Scraps all wine data from Vivino.')

    parser.add_argument('output_file', help='Output .json file', type=str)

    parser.add_argument('-start_page', help='Starting page identifier', type=int, default=1)

    return parser.parse_args()


if __name__ == '__main__':
    # Gathers the input arguments and its variables
    args = get_arguments()
    output_file = args.output_file
    start_page = args.start_page

    # Instantiates a wrapper over the `requests` package
    r = Requester(c.BASE_URL)

    # Defines the payload, i.e., filters to be used on the search
    payload = {
        # "country_codes[]": "fr",
        # "food_ids[]": 20,
        # "grape_ids[]": 3,
        # "grape_filter": "varietal",
        # "min_rating": 0,
        # "order_by": "ratings_average",
        # "order": "desc",
        # "price_range_min": 25,
        # "price_range_max": 100,
        # "region_ids[]": 383,
        # "wine_style_ids[]": 98,
        "wine_type_ids[]": 1,
        # "wine_type_ids[]": 2,
        # "wine_type_ids[]": 3,
        # "wine_type_ids[]": 4,
        # "wine_type_ids[]": 7,
        # "wine_type_ids[]": 24,
    }

    # Performs an initial request to get the number of records (wines)
    try:
        res = r.get('explore/explore?', params=payload)
        if res is None or res.status_code != 200:
            print(f"Error: Initial request failed with status code {res.status_code if res else 'None'}")
            exit(1)
        n_matches = res.json()['explore_vintage']['records_matched']
    except Exception as e:
        print(f"Error fetching initial data: {e}")
        exit(1)

    print(f'Number of matches: {n_matches}')

    # Iterates through the amount of possible pages
    for i in range(start_page, max(1, int(n_matches / c.RECORDS_PER_PAGE)) + 1):
        # Creates a dictionary to hold the data
        data = {}
        data['wines'] = []

        # Adds the page to the payload
        payload['page'] = i

        print(f'Page: {payload["page"]}')

        # Performs the request and scraps the URLs
        try:
            res = r.get('explore/explore', params=payload)
            if res is None or res.status_code != 200:
                print(f"Error: Request for page {i} failed with status code {res.status_code if res else 'None'}")
                continue
            
            response_data = res.json()
            if not response_data or 'explore_vintage' not in response_data:
                print(f"Error: Invalid response format for page {i}")
                continue
                
            matches = response_data['explore_vintage'].get('matches', [])
            if not matches:
                print(f"No matches found for page {i}")
                continue
                
        except Exception as e:
            print(f"Error fetching page {i}: {e}")
            continue

        # Iterates over every match
        for match in matches:
            try:
                # Gathers the wine-based data
                wine = match['vintage']['wine']
                vintage = match['vintage']

                print(f'Scraping data from wine: {wine["name"]}')

                # Safely extract grapes
                grapes_list = []
                if wine.get('style') and isinstance(wine.get('style'), dict):
                    style_grapes = wine.get('style', {}).get('grapes', [])
                    if style_grapes and isinstance(style_grapes, list):
                        grapes_list = [grape.get('name', '') for grape in style_grapes if isinstance(grape, dict) and grape.get('name')]
                
                # Create a clean wine entry with essential data
                wine_entry = {
                    'id' : wine['id'],
                    'name': vintage.get('name'),
                    'vintage': vintage.get('year'),
                    'country': wine['region']['country']['name'] if wine.get('region', {}).get('country') else None,
                    'winery': wine['winery']['name'] if wine.get('winery') else None,
                    'grapes': ';'.join(grapes_list),
                    'rating': vintage['statistics'].get('ratings_average'),
                    'price': match.get('price', {}).get('amount') if match.get('price') else None
                }

                # Gathers the full-taste profile from current match
                try:
                    res = r.get(f'wines/{wine["id"]}/tastes')
                    if res is None or res.status_code != 200:
                        print(f"Warning: Failed to fetch tastes for wine {wine['id']}")
                        tastes = {}
                    else:
                        tastes = res.json()
                except Exception as e:
                    print(f"Error fetching tastes for wine {wine['id']}: {e}")
                    tastes = {}

                # Extract structure safely (handle None values) and don't stop on errors
                try:
                    tastes_block = tastes.get('tastes', {}) if isinstance(tastes, dict) and tastes else {}
                    structure = tastes_block.get('structure', {}) if isinstance(tastes_block, dict) and tastes_block else {}

                    wine_entry['acidity'] = structure.get('acidity') if structure else None
                    wine_entry['intensity'] = structure.get('intensity') if structure else None
                    wine_entry['sweetness'] = structure.get('sweetness') if structure else None
                    wine_entry['tannin'] = structure.get('tannin') if structure else None
                    
                    # Extract top 3 taste groups as flavor_rank1, flavor_rank2, flavor_rank3
                    taste_flavors = tastes_block.get('flavor', []) if isinstance(tastes_block, dict) and tastes_block else []
                    
                    # Ensure taste_flavors is a list before sorting
                    if taste_flavors and isinstance(taste_flavors, list):
                        sorted_flavors = sorted(
                            taste_flavors, 
                            key=lambda x: x.get('stats', {}).get('mentions_count', 0) if isinstance(x, dict) else 0, 
                            reverse=True
                        )[:3]
                    else:
                        sorted_flavors = []
                    
                    for idx, flavor in enumerate(sorted_flavors, start=1):
                        wine_entry[f'flavor_rank{idx}'] = flavor.get('group') if isinstance(flavor, dict) else None
                    
                    # Fill missing ranks with None if less than 3 flavors
                    for idx in range(len(sorted_flavors) + 1, 4):
                        wine_entry[f'flavor_rank{idx}'] = None
                        
                except Exception as e:
                    print(f"Error processing taste data for wine {wine['id']}: {e}")
                    wine_entry['acidity'] = None
                    wine_entry['intensity'] = None
                    wine_entry['sweetness'] = None
                    wine_entry['tannin'] = None
                    wine_entry['flavor_rank1'] = None
                    wine_entry['flavor_rank2'] = None
                    wine_entry['flavor_rank3'] = None

                # Append the cleaned entry to the data
                data['wines'].append(wine_entry)
                
            except Exception as e:
                print(f"Error processing match: {e}")
                continue

        # Opens the output .json file
        try:
            with open(f'{i}_{output_file}', 'w') as f:
                # Dumps the data
                json.dump(data, f, indent=2)
            
            # Closes the file
            f.close()
            print(f"Successfully saved page {i} to {i}_{output_file}")
        except Exception as e:
            print(f"Error saving file for page {i}: {e}")
