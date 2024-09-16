import pandas as pd

# List of your CSV files (replace these with your actual file paths)
csv_files = [
    '20230125_tr_note.csv',
    '20230125_tr_note_source.csv',
    '20230125_tr_topic_category.csv',
    '20230125_tr_topic.csv',
    'datapoints_2024-01-16T15 25 08.159208+01 00.csv',
    'query_result_2024-01-16T15 25 39.093368+01 00.csv',
]

# Process each file
for file_path in csv_files:
    # Load the CSV file
    df = pd.read_csv(file_path)
    
    # Calculate 20% of the number of rows
    rows_20_percent = int(len(df) * 0.2)
    
    # Select the first 20% of the rows
    df_20_percent = df.iloc[:rows_20_percent]
    
    # Create an output file name by appending '_20_percent' to the original file name
    output_file = file_path.replace('.csv', '_20_percent.csv')
    
    # Save the new DataFrame to a CSV file
    df_20_percent.to_csv(output_file, index=False)
    
    print(f"Saved the first 20% of {file_path} to {output_file}")

print("Processing complete for all files.")
