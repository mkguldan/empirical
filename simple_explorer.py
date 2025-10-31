#!/usr/bin/env python3
"""
Simple PE/VC Data Explorer
Quick insights into your research opportunities
"""

import pandas as pd
import numpy as np
from pathlib import Path

class SimpleExplorer:
    """Simple data explorer for research opportunities"""
    
    def __init__(self, data_dir="core_tables"):
        self.data_dir = Path(data_dir)
        self.data = {}
        print("🔄 Loading key tables...")
        self.load_key_tables()
        
    def load_key_tables(self):
        """Load the most important tables"""
        key_files = {
            'companies': 'Company.csv',
            'deals': 'Deal.csv', 
            'investors': 'Investor.csv',
            'people': 'Person.csv',
            'funds': 'Fund.csv'
        }
        
        for name, filename in key_files.items():
            file_path = self.data_dir / filename
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    self.data[name] = df
                    print(f"   ✅ {name}: {len(df):,} rows, {len(df.columns)} columns")
                except Exception as e:
                    print(f"   ❌ Error loading {filename}: {e}")
            else:
                print(f"   ⚠️  {filename} not found - add your CSV files to {self.data_dir}/")
        
        if len(self.data) > 0:
            print(f"\n🎯 Loaded {len(self.data)} core tables!")
        else:
            print(f"\n📁 No data files found. Please add your CSV files to the '{self.data_dir}' directory")
    
    def show_research_opportunities(self):
        """Show specific research opportunities based on your data"""
        print("\n" + "="*60)
        print("🔍 TOP RESEARCH OPPORTUNITIES FOR YOUR CLASS PROJECT")
        print("="*60)
        
        opportunities = [
            {
                'title': '💰 DEAL PERFORMANCE ANALYSIS',
                'difficulty': '🟢 PERFECT FOR CLASS PROJECT',
                'description': 'Analyze what drives successful deals - size, timing, industry',
                'why_great': 'Clear variables, straightforward analysis, practical insights',
                'sample_questions': [
                    'Do larger deals have better returns?',
                    'Which industries see the highest valuations?',
                    'How has deal performance changed over time?'
                ],
                'data_needed': 'Deal.csv with DealSize, PostValuation, DealDate columns'
            },
            {
                'title': '🌍 GEOGRAPHIC INVESTMENT PATTERNS',
                'difficulty': '🟢 PERFECT FOR CLASS PROJECT', 
                'description': 'Where do investments happen? Geographic concentration effects',
                'why_great': 'Great visualizations, clear policy implications, European angle',
                'sample_questions': [
                    'Is venture capital geographically concentrated?',
                    'Do local investors outperform distant ones?',
                    'How do European vs US patterns differ?'
                ],
                'data_needed': 'Company.csv with HQLocation, HQCountry columns'
            },
            {
                'title': '🎓 ELITE NETWORKS & SUCCESS',
                'difficulty': '🟡 INTERMEDIATE - VERY INTERESTING',
                'description': 'Do elite MBA programs create PE/VC success? Network effects',
                'why_great': 'Personal relevance (Bocconi!), novel insights, network analysis',
                'sample_questions': [
                    'Do top MBA programs dominate PE/VC?',
                    'Does educational prestige predict fund performance?',
                    'How important are alumni networks?'
                ],
                'data_needed': 'Person.csv + PersonEducationRelation.csv'
            },
            {
                'title': '📈 FUND STRATEGY & PERFORMANCE',
                'difficulty': '🟡 INTERMEDIATE - HIGH IMPACT',
                'description': 'What investment strategies work best? Size, specialization, timing',
                'why_great': 'Practical for investors, clear metrics, policy relevant',
                'sample_questions': [
                    'Do specialized funds outperform generalists?',
                    'Is there an optimal fund size?',
                    'Does market timing matter for fund performance?'
                ],
                'data_needed': 'Fund.csv with IRR, TVPI, DPI performance metrics'
            }
        ]
        
        # Display opportunities
        for i, opp in enumerate(opportunities, 1):
            print(f"\n{i}. {opp['title']}")
            print(f"   Difficulty: {opp['difficulty']}")
            print(f"   📝 What: {opp['description']}")
            print(f"   💡 Why great: {opp['why_great']}")
            print(f"   📊 Data needed: {opp['data_needed']}")
            print(f"   🎯 Sample questions:")
            for q in opp['sample_questions']:
                print(f"      • {q}")
        
        print(f"\n🎯 MY TOP RECOMMENDATION FOR YOU:")
        print("="*50)
        print(f"📌 💰 DEAL PERFORMANCE ANALYSIS")
        print(f"✨ Why: Clear variables, straightforward analysis, practical insights")
        print(f"📊 Data: Need Deal.csv with valuation and size data")
        
        return opportunities
    
    def quick_data_check(self, table_name):
        """Quick check of a specific table"""
        if table_name not in self.data:
            print(f"❌ Table '{table_name}' not available!")
            print(f"Available tables: {list(self.data.keys())}")
            return
        
        df = self.data[table_name]
        print(f"\n📊 QUICK CHECK: {table_name.upper()}")
        print("="*40)
        print(f"Rows: {len(df):,}")
        print(f"Columns: {len(df.columns)}")
        
        # Show column types
        print(f"\nColumn types:")
        for dtype in df.dtypes.value_counts().index:
            count = df.dtypes.value_counts()[dtype]
            print(f"  {dtype}: {count} columns")
        
        # Show sample columns
        print(f"\nSample columns:")
        for col in df.columns[:10]:
            print(f"  • {col}")
        if len(df.columns) > 10:
            print(f"  ... and {len(df.columns) - 10} more")
        
        # Check for missing data
        missing_pct = (df.isnull().sum() / len(df) * 100)
        high_missing = missing_pct[missing_pct > 50]
        if len(high_missing) > 0:
            print(f"\n⚠️  Columns with >50% missing data: {len(high_missing)}")
        
        print(f"\n📋 Sample data:")
        print(df.head(3).to_string())

def main():
    """Main exploration function"""
    print("🚀 PE/VC Research Opportunity Finder")
    print("="*50)
    
    # Load data
    explorer = SimpleExplorer()
    
    # Show opportunities
    opportunities = explorer.show_research_opportunities()
    
    print(f"\n🚀 READY TO START?")
    print("1. Add your CSV files to the 'core_tables/' directory")
    print("2. Run: explorer.quick_data_check('deals')")
    print("3. Pick your research question and start analyzing!")
    
    return explorer

if __name__ == "__main__":
    explorer = main()


