# 🎓 Venture Capital & Founder Education Analysis

A comprehensive data analysis project examining the relationship between founder educational backgrounds (particularly Ivy League education) and venture capital funding success. Developed for Empirical Methods coursework at Bocconi University.

## 📊 Project Overview

This project analyzes a large-scale private equity and venture capital dataset to investigate:

**Primary Research Question:**  
*"Do U.S.-headquartered startups with Ivy League-educated founders raise significantly more venture capital than those without, and how is this relationship influenced by founder gender, industry sector, geographic context, and the year the startup was founded?"*

### Key Findings & Statistics
- **~5M records** across 60 variables in the master dataset
- **530,602 unique individuals** tracked across companies and deals
- **79,874 companies** in the U.S. with complete funding histories  
- **212,852 funding deals** analyzed
- **Focus on Venture Capital-backed companies** (filtering out accelerators, grants, crowdfunding)

---

## 🗂️ Project Structure

### Data Pipeline

The project follows a multi-stage data processing pipeline:

```
Raw Data Files (CSV)
    ↓
1. create_master_file.py → master_file.csv
    ↓
2. create_founder_vc_analysis.py → founder_vc_analysis.csv
    ↓
3. filter_founder_vc_final.py → founder_vc_final.csv
    ↓
4. clean_founder_vc_final.py → founder_vc_cleaned.csv
    ↓
5. categorize_and_format.py → founder_vc_final_formatted.csv
    ↓
6. prepare_for_stata.py → deal_level_analysis.csv/.dta (Stata-ready)
```

### Core Scripts

#### 1. **Data Merging & Master File Creation**

**`create_master_file.py`**
- Merges multiple core data tables (Company, Deal, Investor, Person, Education)
- Creates a comprehensive master dataset with 60 columns
- Handles one-to-many relationships through proper table joins
- Generates 4,974,015 records linking companies, deals, investors, and people

---

#### 2. **Founder-VC Analysis Dataset**

**`create_founder_vc_analysis.py`**
- **Purpose**: Creates a focused dataset of founders and their first VC deals
- **Key Logic**:
  - Filters for VC deals (excludes accelerators, grants, crowdfunding)
  - Identifies founders using `Person_PrimaryPositionLevel == "Founder"`
  - Finds the first VC deal for each company
  - Prioritizes deals with complete size information
  - One row per founder (handles multiple education records)
- **Validation**: Ensures `Deal_DealClass` contains "Venture Capital"
- **Output**: Founder-level dataset ready for education analysis

---

#### 3. **Filtering for Complete Records**

**`filter_founder_vc_final.py`**
- **Purpose**: Filters for founders with complete deal size AND education data
- **Filters Applied**:
  - Must have `Investor_DealSize` OR `Deal_DealSize` (VC funding amount)
  - Must have `Education_Institute` (university/college information)
- **Rationale**: Ensures analysis only includes founders with observable funding outcomes and verifiable education backgrounds
- **Output**: Clean dataset for statistical analysis

---

#### 4. **Data Cleaning & Normalization**

**`clean_founder_vc_final.py`**
- **Purpose**: Applies rigorous data quality standards
- **Cleaning Steps**:
  1. **Remove founders with blank `Person_Gender`** (required for gender analysis)
  2. **Remove unwanted deal types**:
     - Accelerator/Incubator deals
     - Equity Crowdfunding
     - Grants
  3. **Normalize all dates to `dd/mm/yyyy` format**
     - Handles multiple input formats (dots, slashes, ISO)
     - Ensures consistent date handling
- **Validation**: Verifies no unwanted deal types remain
- **Output**: High-quality dataset for analysis

---

#### 5. **Education Categorization & Currency Formatting**

**`categorize_and_format.py`**
- **Purpose**: Standardizes education degrees and formats deal sizes
- **Education Categorization**:
  - **ASC**: Associate degrees
  - **BSC**: Bachelor's degrees (BA, BS, BBA, etc.)
  - **MSC**: Master's degrees (MS, MA, ME, MPA, etc.) - excludes MBA
  - **MBA**: Master of Business Administration specifically
  - **JD**: Juris Doctor (law degrees)
  - **PHD**: Doctoral degrees (PhD, MD, DDS, EdD, Postdoc, etc.)
  - **CHA**: Chartered/Certified professional certifications (CPA, CFA, CA, CMA, ACCA)
  - **Other**: Vague or unclassifiable degrees
- **Pattern Matching**: Uses comprehensive regex patterns to catch variations
  - Example: "Harvard" vs "Harvard University" vs "Harvard Business School"
- **Currency Formatting**:
  - Converts `Deal_DealSize` from millions to full USD amounts
  - Format: `$XX,XXX,XXX.XX`
- **Output**: Analysis-ready dataset with standardized categories

---

#### 6. **Stata Preparation & Deal-Level Aggregation**

**`prepare_for_stata.py`**
- **Purpose**: Transforms founder-level data into deal-level analysis file ready for Stata regression analysis
- **Key Transformations**:
  - **Geography**: Filters to US companies only (50 states + DC)
  - **Date Filtering**: Excludes deals with missing Deal_Year (ensures temporal controls)
  - **Amount Parsing**: Converts deal sizes to numeric, creates log transformations
  - **Collapse to Deal-Level**: Aggregates multiple founders per deal into team composition variables
- **Team Composition Variables Created**:
  - **University Pedigree** (multiple approaches):
    - `Share_Ivy`, `Share_Top8`, `Share_Other` (continuous 0-1)
    - `Any_Ivy`, `Any_Top8` (binary indicators)
    - `Team_Education_Group` (categorical: Ivy/Top8/Other, mutually exclusive hierarchy)
    - `Max_Pedigree` (numeric ranking: 3=Ivy, 2=Top8, 1=Other)
  - **Gender Composition**:
    - `Female_Share` (continuous 0-1)
    - `Any_Female` (binary)
    - `Team_Gender` (5 categories: Single_Male, Single_Female, All_Male, All_Female, Mixed)
  - **Major/Field Composition**: Maps 1,918 unique majors → 8 broad categories
    - CS_Engineering, Natural_Sciences, Medicine_Health, Business_Econ, Social_Sciences, Humanities_Arts, Law, Other
    - Creates `Team_STEM_Share`, `Team_Business_Share`, `Any_CS`
  - **Education Level**: `Max_Education` (highest degree on team: PhD > MD > JD > MBA > MSC > BSC)
  - **Team Metrics**: TeamSize, SyndicateSize (investor count)
- **Fixed Effects Identifiers**:
  - `Deal_Year` (for year FE)
  - `Company_PrimaryIndustryGroup` (38 categories for industry FE)
  - `Company_HQState_Province` (US states for geography FE)
  - `Region` (4 regions: Northeast, South, Midwest, West)
  - `Company_YearFounded` (for founding cohort FE)
- **Outcome Variables**:
  - `log_DealSize` (primary continuous outcome)
  - Stage indicators: `Stage_Seed`, `Stage_Early`, `Stage_Later`
  - `Stage_Order` (ordered: 1=Seed, 2=Early, 3=Later)
- **Company Controls**:
  - `log_Employees` with `Employees_Missing` indicator
  - `Age_at_Deal` (years from founding to deal)
- **Validation**:
  - Confirms 1:1 CompanyID ↔ DealID mapping
  - Verifies share variables sum to 1.0
  - Documents all filtering decisions with retention rates
- **Output**:
  - `deal_level_analysis.csv` (7,800-7,900 rows, ~47 columns)
  - `deal_level_analysis.dta` (Stata format with labels)
  - `data_preparation_log.md` (comprehensive documentation)
- **Stata-Ready**: Designed for `reghdfe` with high-dimensional fixed effects and clustered standard errors

---

### Supporting Scripts

#### Data Exploration & Validation

**`analyze_data.py`**
- Analyzes data dictionary and HTML analysis files
- Extracts table metadata and column information
- Generates summary reports

**`data_quality_check.py`**
- Comprehensive data quality validation
- Checks relationship integrity (companies → deals → investors → people)
- Validates data completeness for key fields
- Assesses name consistency

**`examine_degrees.py`**
- Examines unique `Education_Degree` values
- Provides frequency counts for degree types
- Used to develop categorization logic

**`preview_master_file.py`**
- Quick preview of master file structure
- Shows sample records with complete data
- Displays basic statistics

**`simple_explorer.py`**
- Interactive data exploration tool
- Suggests research opportunities
- Provides quick data checks for specific tables

---

## 🎯 Research Design

### Variables

#### Dependent Variable
- **TotalRaised**: Total venture capital raised (continuous, USD millions)

#### Independent Variable (Primary)
- **HasIvyLeagueFounder**: Binary (1 = at least one founder has Ivy League degree, 0 = none)
- Alternative: **PercentIvyLeagueFounders**: Proportion of founders with Ivy degree (0-1)

#### Moderator Variables

1. **Founder Gender**
   - `HasFemaleFounder`: Binary indicator
   - `PercentFemaleFounders`: Proportion (0-1)

2. **Industry Sector**
   - `PrimaryIndustrySector`: Broad classification (IT, Healthcare, etc.)
   - `PrimaryIndustryGroup`: Granular classification (Software, Biotech, etc.)

3. **Geographic Context**
   - `HQState_Province`: State-level location
   - `HQCity`: City-level location
   - Derived: `IsInTechHub` (Silicon Valley, NYC, Boston, etc.)

4. **Year Founded**
   - `YearFounded`: Continuous year variable
   - Derived: `FoundedEra` (Pre-2000, 2000-2010, 2010-2015, Post-2015)

#### Control Variables
- `NumberOfFounders`: Count of founders per company
- `BusinessStatus`: Current operational status
- `Employees`: Company size
- `YearsSinceFirstFunding`: Time since first funding round

---

### Ivy League Institutions

The analysis identifies founders educated at the following 8 institutions:

1. Harvard University
2. Yale University  
3. Princeton University
4. Columbia University
5. University of Pennsylvania (Penn/Wharton)
6. Brown University
7. Dartmouth College
8. Cornell University

**Note**: Uses partial string matching to capture variations:
- "Harvard" vs "Harvard University" vs "Harvard Business School"
- "Penn" vs "University of Pennsylvania" vs "UPenn" vs "Wharton"

---

## 📁 Data Dictionary

### Source Tables

The analysis uses 6 core tables from the PE/VC database:

| Table | Records | Columns | Description |
|-------|---------|---------|-------------|
| **Company.csv** | 57,751 | 121 | Company profiles, locations, industries, funding status |
| **Deal.csv** | 145,894 | 108 | Funding deals, valuations, dates, types |
| **Investor.csv** | 58,736 | varies | Investor profiles and preferences |
| **Person.csv** | 557,995 | 35 | Individual profiles, positions, demographics |
| **PersonEducationRelation.csv** | 586,031 | 6 | Education backgrounds (institute, degree, major, year) |
| **PersonPositionRelation.csv** | 561,080 | 11 | Person-company relationships, titles, founder identification |

### Key Linkages

```
Company (CompanyID)
    ↕
PersonPositionRelation (EntityID ↔ CompanyID, PersonID)
    ↕
Person (PersonID)
    ↕
PersonEducationRelation (PersonID)
    ↕
Company (CompanyID) ← Deal (CompanyID, DealID)
```

---

## 🚀 Getting Started

### Prerequisites

```bash
pip install pandas numpy
```

### Basic Usage

#### 1. Set Up Your Data

Place your CSV data files in a folder (e.g., `core_tables/`):
- Company.csv
- Deal.csv
- Investor.csv
- Person.csv
- PersonEducationRelation.csv
- PersonPositionRelation.csv

#### 2. Run the Data Pipeline

```bash
# Step 1: Create master file (merge all tables)
python create_master_file.py

# Step 2: Create founder-VC analysis dataset
python create_founder_vc_analysis.py

# Step 3: Filter for complete records (deal size + education)
python filter_founder_vc_final.py

# Step 4: Clean data (remove blank genders, unwanted deal types)
python clean_founder_vc_final.py

# Step 5: Categorize education and format currency
python categorize_and_format.py
```

#### 3. Explore the Data

```python
# Quick exploration
python simple_explorer.py

# Preview master file
python preview_master_file.py

# Check data quality
python data_quality_check.py
```

---

## 🔍 Key Insights from Data

### Dataset Characteristics

**Industry Distribution** (Top 3):
- Information Technology: 21.78% (1,083,368 records)
- Healthcare: 11.24% (558,863 records)
- Consumer Products & Services: 7.40% (368,027 records)

**Geographic Concentration** (Top 5 Cities):
1. San Francisco: 376,682 companies (7.57%)
2. New York: 343,306 companies (6.90%)
3. Boston: 92,449 companies (1.86%)
4. Los Angeles: 64,664 companies (1.30%)
5. Austin: 58,114 companies (1.17%)

**Founding Year Distribution**:
- Peak years: 2013-2015 (heaviest startup activity)
- Dataset focuses on post-2010 companies

**Deal Types** (Most Common):
1. Early Stage VC: 16.96%
2. Later Stage VC: 14.37%
3. Seed Round: 11.11%

**Gender Distribution** (Founders):
- Male: 78.13%
- Female: 21.20%

**Education Background** (Top Institutions):
1. Stanford University: 107,780 records (2.17%)
2. UC Berkeley: 69,683 records (1.40%)
3. Harvard University: 60,273 records (1.21%)
4. Harvard Business School: 56,428 records (1.13%)
5. UPenn/Wharton: 47,032 records (0.95%)

---

## 📊 Recommended Analysis Approach

### Model Specification

```
TotalRaised ~ HasIvyLeagueFounder + HasFemaleFounder + 
              HasIvyLeagueFounder × HasFemaleFounder +
              PrimaryIndustrySector + HQState_Province + YearFounded +
              NumberOfFounders + (other controls)
```

### Alternative Specifications

1. **Main effects only** (no interactions)
2. **Two-way interactions**:
   - Ivy × Gender
   - Ivy × Industry
   - Ivy × Geography
   - Ivy × Year
3. **Three-way interactions**:
   - Ivy × Gender × Industry
4. **Robustness checks** with different dependent variables:
   - LastFinancingSize
   - LastKnownValuation

### Hypotheses to Test

1. **Main Effect**: Ivy League founders raise more VC funding (H1)
2. **Gender Moderation**: The Ivy League advantage is stronger for male founders (H2)
3. **Industry Moderation**: The Ivy League advantage is stronger in tech sectors (H3)
4. **Geographic Moderation**: The Ivy League advantage is stronger in major tech hubs (H4)
5. **Time Moderation**: The Ivy League advantage has changed over time (H5)

---

## 📝 Data Quality Considerations

### Strengths
✅ **ID-based matching**: 100% success on direct relationships (no fuzzy matching needed)  
✅ **High coverage**: Most key variables have >50% non-null rates  
✅ **Comprehensive**: All entity types (companies, deals, investors, people) included  
✅ **Validated**: Multiple quality checks ensure data integrity  

### Limitations
⚠️ **Missing education data**: Not all founders have education records (~40% missing)  
⚠️ **Self-reported data**: Education and biographical data may have inconsistencies  
⚠️ **Survivorship bias**: Dataset may over-represent successful companies  
⚠️ **U.S.-centric**: Analysis focuses exclusively on U.S.-based companies  

### Missing Data Handling
- **Gender**: Rows with missing gender are explicitly removed
- **Education**: Only founders with education institute data are included
- **Deal Size**: Only deals with size information are analyzed
- **Documentation**: All filtering decisions are logged with retention rates

---

## 🛠️ Technical Details

### File Formats
- **Input**: CSV files with various delimiters (`,` `;` `\t`)
- **Output**: UTF-8 encoded CSV files with comma delimiters
- **Encoding**: UTF-8-sig (handles special characters and BOM)

### Performance Considerations
- **Chunked reading**: Large files processed in 100,000-row chunks
- **Memory efficiency**: Low-memory mode for pandas
- **Multiple encodings tried**: Handles various source file formats

### Data Validation
- Relationship integrity checks (deals → companies, investors → deals)
- Null value monitoring
- Duplicate detection and removal
- Value consistency verification

---

## 📚 Documentation Files

| File | Description |
|------|-------------|
| `variable_selection.md` | Complete variable documentation for research question |
| `column_frequency_analysis.md` | Frequency distributions for all 60 columns |
| `changelog.md` | Project change log and version history |
| `README.md` | This file |

---

## 🎓 Academic Context

**Course**: Empirical Methods  
**Institution**: Bocconi University  
**Semester**: Fall 2024  

### Research Opportunities Identified

This dataset supports multiple research questions:

1. **💰 Deal Performance Analysis** (recommended for class projects)
   - What factors drive successful PE/VC deals?
   - Clear variables, straightforward analysis

2. **🌍 Geographic Investment Patterns**
   - How does geography shape PE/VC investment patterns?
   - Great visualizations, policy implications

3. **🎓 Elite Networks & Success** (current focus)
   - Do elite educational backgrounds drive PE/VC success?
   - Network analysis, novel insights

4. **📈 Fund Strategy & Performance**
   - What investment strategies lead to superior fund performance?
   - High academic impact, practical insights

---

## 🤝 Contributing

This is an academic research project. For questions or collaboration:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/analysis`)
3. Commit your changes (`git commit -m 'Add new analysis'`)
4. Push to the branch (`git push origin feature/analysis`)
5. Open a Pull Request

---

## ⚠️ Data Privacy

**Important**: This repository contains **CODE ONLY**. Raw data files (`.csv`, `.xlsx`) are excluded via `.gitignore` to protect privacy and comply with data usage agreements.

To run the analysis:
1. Obtain your own PE/VC dataset
2. Place files in the appropriate directory
3. Run the scripts following the pipeline sequence

---

## 📄 License

This project is for academic purposes. The code is open source, but data access requires proper permissions from the data provider.

---

## 🙏 Acknowledgments

- Bocconi University Empirical Methods Course
- PitchBook (or relevant data provider) for PE/VC data access
- Python data science community (pandas, numpy)

---

**Last Updated**: October 31, 2024  
**Author**: Master's Student, Bocconi University  
**Contact**: See GitHub profile

---

## 💡 Quick Tips

### For Students Using This Code

1. **Understand the pipeline**: Each script builds on the previous one
2. **Check intermediate outputs**: Each step saves a summary CSV
3. **Validate your data**: Run `data_quality_check.py` before analysis
4. **Customize filters**: Modify filtering logic for different research questions
5. **Document changes**: Update `changelog.md` when you modify scripts

### For Researchers

1. **Adapt to your data**: Column names may differ in your dataset
2. **Modify Ivy League list**: Add international universities if needed
3. **Extend categories**: Add more education or deal type categories
4. **Export for Stata/R**: Final CSV works in any statistical software
5. **Scale up**: Scripts handle millions of records efficiently

---

*"The best research combines rigorous methodology with practical insight. This project aims to do both."*
