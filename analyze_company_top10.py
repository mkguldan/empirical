import pandas as pd
from pathlib import Path

def analyze_top_occurrences(csv_path, output_md_path, top_n=10):
    """
    Analyze a CSV file and generate a markdown report with top N occurring values for each column.
    
    Parameters:
    -----------
    csv_path : str
        Path to the CSV file to analyze
    output_md_path : str
        Path to save the markdown output
    top_n : int
        Number of top occurrences to report (default: 10)
    """
    # Read the CSV file
    print(f"Reading {csv_path}...")
    df = pd.read_csv(csv_path, low_memory=False)
    
    # Get basic statistics
    total_rows = len(df)
    total_columns = len(df.columns)
    
    # Start building the markdown content
    md_content = []
    md_content.append("# Company.csv - Top 10 Occurring Data Points Analysis\n")
    md_content.append(f"**File:** `{csv_path}`\n")
    md_content.append(f"**Total Rows:** {total_rows:,}\n")
    md_content.append(f"**Total Columns:** {total_columns}\n")
    md_content.append(f"**Analysis Date:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    md_content.append("\n---\n")
    
    # Analyze each column
    for idx, column in enumerate(df.columns, 1):
        print(f"Analyzing column {idx}/{total_columns}: {column}")
        
        md_content.append(f"\n## {idx}. {column}\n")
        
        # Get value counts
        value_counts = df[column].value_counts(dropna=False)
        
        # Count null/missing values
        null_count = df[column].isna().sum()
        null_percentage = (null_count / total_rows) * 100
        
        md_content.append(f"**Total Unique Values:** {len(value_counts):,}\n")
        md_content.append(f"**Missing Values:** {null_count:,} ({null_percentage:.2f}%)\n")
        md_content.append(f"**Non-Missing Values:** {total_rows - null_count:,}\n\n")
        
        # Get top N occurrences
        top_values = value_counts.head(top_n)
        
        if len(top_values) > 0:
            md_content.append("| Rank | Value | Count | Percentage |\n")
            md_content.append("|------|-------|-------|------------|\n")
            
            for rank, (value, count) in enumerate(top_values.items(), 1):
                percentage = (count / total_rows) * 100
                
                # Handle display of different value types
                if pd.isna(value):
                    display_value = "*[Missing/NaN]*"
                elif isinstance(value, str):
                    # Truncate long strings for display
                    if len(value) > 100:
                        display_value = f"{value[:97]}..."
                    else:
                        display_value = value.replace("|", "\\|")  # Escape pipe characters
                else:
                    display_value = str(value)
                
                md_content.append(f"| {rank} | {display_value} | {count:,} | {percentage:.2f}% |\n")
        else:
            md_content.append("*No data available*\n")
        
        md_content.append("\n")
    
    # Write to markdown file
    output_content = "".join(md_content)
    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    print(f"\nAnalysis complete! Report saved to: {output_md_path}")
    return output_md_path


if __name__ == "__main__":
    # Define paths
    csv_file = r"D:\School\Bocconi\Empirical\core_tables\Company.csv"
    output_file = r"D:\School\Bocconi\Empirical\company_top10_analysis.md"
    
    # Run analysis
    analyze_top_occurrences(csv_file, output_file, top_n=10)

