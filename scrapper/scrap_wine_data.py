import argparse
import json
import os
import glob

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

    # Auto-resume logic: find the last scraped page
    if start_page == 1:
        dirname = os.path.dirname(output_file) or '.'
        basename = os.path.basename(output_file)
        
        # Search for files matching pattern {number}_{basename}
        search_pattern = os.path.join(dirname, f"*_{basename}")
        existing_files = glob.glob(search_pattern)
        
        max_page = 0
        for f_path in existing_files:
            f_name = os.path.basename(f_path)
            # Check if file matches {number}_{basename}
            if f_name.endswith(f"_{basename}"):
                try:
                    # Extract the number part
                    prefix = f_name[:-len(basename)-1]
                    page_num = int(prefix)
                    if page_num > max_page:
                        max_page = page_num
                except ValueError:
                    continue
        
        if max_page > 0:
            start_page = max_page + 1
            print(f"Found existing data up to page {max_page}. Auto-resuming from page {start_page}.")

    # Instantiates a wrapper over the `requests` package
    r = Requester(c.BASE_URL)

    # Defines the base payload
    base_payload = {
        "country_codes[]": "fr",
        "wine_type_ids[]": 1,
    }

    # Global variables for the recursive process
    global_page_counter = 1
    seen_wines = set()
    dumped_taste = False
    dumped_reviews = False

    def fetch_wines_recursive(min_price, max_price):
        global global_page_counter, dumped_taste, dumped_reviews
        
        # Create a copy of payload for this specific range
        current_payload = base_payload.copy()
        current_payload['price_range_min'] = min_price
        current_payload['price_range_max'] = max_price
        
        print(f"Checking price range: {min_price} - {max_price}")

        try:
            # Get the number of matches for this range
            res = r.get('explore/explore?', params=current_payload)
            if res is None or res.status_code != 200:
                print(f"Error fetching count for range {min_price}-{max_price}")
                return

            n_matches = res.json()['explore_vintage']['records_matched']
            print(f"Found {n_matches} matches for price range {min_price}-{max_price}")

            # If too many matches, split the range (unless range is too small)
            if n_matches >= 2000 and (max_price - min_price) > 0.02:
                mid_price = (min_price + max_price) / 2
                fetch_wines_recursive(min_price, mid_price)
                fetch_wines_recursive(mid_price, max_price)
                return

            # Calculate number of pages for this range
            num_pages = max(1, int(n_matches / c.RECORDS_PER_PAGE)) + 1
            
            # Optimization: Skip pages if we haven't reached start_page yet
            if global_page_counter + num_pages < start_page:
                print(f"Skipping {num_pages} pages (current: {global_page_counter}, target: {start_page})")
                global_page_counter += num_pages
                return

            # Iterate through pages for this range
            consecutive_duplicates = 0
            previous_matches = []

            for i in range(1, num_pages + 1):
                # Check if we should process this page based on global counter
                if global_page_counter < start_page:
                    global_page_counter += 1
                    continue

                current_payload['page'] = i
                print(f'Global Page: {global_page_counter} (Local Page: {i}, Price: {min_price}-{max_price})')

                try:
                    res = r.get('explore/explore', params=current_payload)
                    
                    if res is None or res.status_code != 200:
                        print(f"Error: Request failed")
                        continue
                    
                    response_data = res.json()
                    matches = response_data['explore_vintage'].get('matches', [])
                    
                    if not matches:
                        print(f"No matches found")
                        break

                    # Duplicate detection
                    current_ids = [m['vintage']['wine']['id'] for m in matches if 'vintage' in m and 'wine' in m['vintage']]
                    
                    # Check if all wines in this page have been seen before
                    duplicates_count = 0
                    new_wines_in_page = 0
                    for wine_id in current_ids:
                        if wine_id in seen_wines:
                            duplicates_count += 1
                        else:
                            seen_wines.add(wine_id)
                            new_wines_in_page += 1

                    if duplicates_count == len(current_ids) and len(current_ids) > 0:
                        consecutive_duplicates += 1
                        print(f"Duplicate content detected ({consecutive_duplicates}/5).")
                        if consecutive_duplicates >= 5:
                            print("Pagination limit reached for this range. Moving to next.")
                            break
                        continue
                    
                    consecutive_duplicates = 0

                    # Process wines
                    data = {'wines': []}
                    for match in matches:
                        try:
                            wine = match['vintage']['wine']
                            vintage = match['vintage']
                            
                            # ...existing code...
                            # Safely extract grapes
                            grapes_list = []
                            if wine.get('style') and isinstance(wine.get('style'), dict):
                                style_grapes = wine.get('style', {}).get('grapes', [])
                                if style_grapes and isinstance(style_grapes, list):
                                    grapes_list = [grape.get('name', '') for grape in style_grapes if isinstance(grape, dict) and grape.get('name')]
                            
                            wine_entry = {
                                'id' : wine['id'],
                                'name': vintage.get('name'),
                                'vintage': vintage.get('year'),
                                'country': wine['region']['country']['name'] if wine.get('region', {}).get('country') else None,
                                'winery': wine['winery']['name'] if wine.get('winery') else None,
                                'grapes': ';'.join(grapes_list),
                                'rating': vintage['statistics'].get('ratings_average'),
                                'reviews_count': vintage['statistics'].get('ratings_count'),
                                'price': match.get('price', {}).get('amount') if match.get('price') else None
                            }

                            # Fetch reviews for specific vintage
                            try:
                                res_reviews = r.get(f'wines/{wine["id"]}/reviews')
                                
                                if not dumped_reviews and res_reviews and res_reviews.status_code == 200:
                                    with open('debug_wine_reviews.json', 'w', encoding='utf-8') as f:
                                        json.dump(res_reviews.json(), f, indent=2, ensure_ascii=False)
                                    dumped_reviews = True
                                
                                if res_reviews and res_reviews.status_code == 200:
                                    reviews_data = res_reviews.json()
                                    # Store the number of reviews returned (usually capped at a page size, e.g. 3 or 10)
                                    # This confirms existence of text reviews for this vintage
                                    wine_entry['reviews_count'] = len(reviews_data.get('reviews', []))
                                else:
                                    wine_entry['reviews_count'] = 0
                            except Exception as e:
                                print(f"Error fetching reviews: {e}")
                                wine_entry['reviews_count'] = 0

                            # Fetch tastes
                            try:
                                res_taste = r.get(f'wines/{wine["id"]}/tastes')
                                if not dumped_taste:
                                    with open('debug_wine_tastes.json', 'w', encoding='utf-8') as f:
                                        json.dump(res_taste.json(), f, indent=2, ensure_ascii=False)
                                    dumped_taste = True
                                
                                tastes = res_taste.json() if res_taste and res_taste.status_code == 200 else {}
                            except Exception:
                                tastes = {}

                            # Process tastes
                            try:
                                tastes_block = tastes.get('tastes', {}) if isinstance(tastes, dict) else {}
                                structure = tastes_block.get('structure', {}) if isinstance(tastes_block, dict) else {}

                                wine_entry['acidity'] = structure.get('acidity') if structure else None
                                wine_entry['intensity'] = structure.get('intensity') if structure else None
                                wine_entry['sweetness'] = structure.get('sweetness') if structure else None
                                wine_entry['tannin'] = structure.get('tannin') if structure else None
                                
                                taste_flavors = tastes_block.get('flavor', []) if isinstance(tastes_block, dict) else []
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
                                for idx in range(len(sorted_flavors) + 1, 4):
                                    wine_entry[f'flavor_rank{idx}'] = None
                                    
                            except Exception as e:
                                print(f"Error processing taste: {e}")
                                # Fill None for taste fields
                                for field in ['acidity', 'intensity', 'sweetness', 'tannin', 'flavor_rank1', 'flavor_rank2', 'flavor_rank3']:
                                    wine_entry[field] = None

                            data['wines'].append(wine_entry)

                        except Exception as e:
                            print(f"Error processing match: {e}")
                            continue

                    # Save file using global counter
                    try:
                        filename = f'{global_page_counter}_{output_file}'
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                        print(f"Saved {filename}")
                    except Exception as e:
                        print(f"Error saving file: {e}")

                except Exception as e:
                    print(f"Error on page {i}: {e}")
                
                # Increment global counter after processing the page
                global_page_counter += 1

        except Exception as e:
            print(f"Error in recursive fetch: {e}")

    # Start the recursive scraping from 0 to 50000 (should cover all wines)
    print("Starting scraping with price segmentation...")
    fetch_wines_recursive(0, 50000)

