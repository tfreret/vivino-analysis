import csv
import os

def filter_wines(input_file, output_file):
    """
    Filter wines from input CSV file based on price range (7-15)
    and save to output CSV file.
    """
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return False
    
    # Check if output file exists and ask for confirmation
    if os.path.exists(output_file):
        response = input(f"File '{output_file}' already exists. Replace it? (y/n): ")
        if response.lower() != 'y':
            print("Operation cancelled.")
            return False
    
    try:
        filtered_rows = []
        header = None
        filtered_count = 0
        total_count = 0
        
        # Read input file
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            header = reader.fieldnames
            
            for row in reader:
                total_count += 1
                try:
                    price = float(row['price'])
                    # Filter: price between 1 and 15 (inclusive)
                    if 7 <= price <= 15:
                        filtered_rows.append(row)
                        filtered_count += 1
                except (ValueError, KeyError) as e:
                    print(f"Warning: Skipping row {total_count} due to invalid price data")
                    continue
        
        # Write output file
        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=header)
            writer.writeheader()
            writer.writerows(filtered_rows)
        
        print(f"\nFiltering complete!")
        print(f"Total wines processed: {total_count}")
        print(f"Wines matching criteria (price 7-15): {filtered_count}")
        print(f"Output saved to: {output_file}")
        return True
        
    except Exception as e:
        print(f"Error processing files: {e}")
        return False

def main():
    print("Wine CSV Filter - Price Range: 7 to 15")
    print("-" * 40)
    
    # Get input file name
    input_file = input("Enter input CSV file name: ").strip()
    
    # Get output file name
    output_file = input("Enter output CSV file name: ").strip()
    
    # Filter wines
    filter_wines(input_file, output_file)

if __name__ == "__main__":
    main()