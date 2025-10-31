#!/usr/bin/env python3
"""
Analyze data dictionary and HTML tables for research question
"""

import pandas as pd
import re
from pathlib import Path
from bs4 import BeautifulSoup
import os

# Set working directory
base_dir = r'G:\Škola\BOCCONI\1st semester\empirical'
os.chdir(base_dir)
print(f"Working directory: {os.getcwd()}")

# Read data dictionary
print("="*80)
print("DATA DICTIONARY ANALYSIS")
print("="*80)

try:
    df_dict = pd.read_excel('data_dictionary.xlsx')
    print(f"\nData Dictionary Shape: {df_dict.shape}")
    print(f"\nColumns in Data Dictionary:")
    print(df_dict.columns.tolist())
    print(f"\nFirst 50 rows:")
    print(df_dict.head(50).to_string())
    
    # Save full dictionary to text file
    with open('data_dictionary_full.txt', 'w', encoding='utf-8') as f:
        f.write(df_dict.to_string())
    print("\n✅ Full data dictionary saved to 'data_dictionary_full.txt'")
    
except Exception as e:
    print(f"❌ Error reading data dictionary: {e}")

# Analyze HTML file for table names
print("\n" + "="*80)
print("HTML TABLE ANALYSIS")
print("="*80)

try:
    with open('comprehensive_analysis.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all table titles/headers
    print("\n🔍 Searching for tables in HTML...")
    
    # Look for h2, h3, h4 headers that might indicate table names
    headers = soup.find_all(['h1', 'h2', 'h3', 'h4'])
    table_info = []
    
    for header in headers:
        text = header.get_text(strip=True)
        # Find the next table after this header
        next_table = header.find_next('table')
        if next_table:
            # Count columns
            thead = next_table.find('thead')
            if thead:
                cols = thead.find_all('th')
                col_names = [col.get_text(strip=True) for col in cols]
                table_info.append({
                    'header': text,
                    'level': header.name,
                    'columns': col_names,
                    'num_cols': len(col_names)
                })
    
    print(f"\n📊 Found {len(table_info)} tables with headers\n")
    
    with open('html_tables_summary.txt', 'w', encoding='utf-8') as f:
        for i, info in enumerate(table_info, 1):
            output = f"\n{i}. {info['header']} ({info['level']})\n"
            output += f"   Columns ({info['num_cols']}): {', '.join(info['columns'][:10])}"
            if len(info['columns']) > 10:
                output += f" ... and {len(info['columns']) - 10} more"
            output += "\n"
            print(output)
            f.write(output)
    
    print("✅ Table summary saved to 'html_tables_summary.txt'")
    
except Exception as e:
    print(f"❌ Error reading HTML: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)

