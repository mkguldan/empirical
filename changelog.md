# Changelog

## 2025-10-01

### Added
- **variable_selection.md**: Comprehensive documentation of all variables selected for the research question analyzing the relationship between Ivy League-educated founders and venture capital funding
  - Identified 6 key tables: Company.csv, Person.csv, PersonEducationRelation.csv, PersonPositionRelation.csv, EntityBoardTeamRelation.csv, and Deal.csv
  - Documented dependent variable (TotalRaised), independent variable (HasIvyLeagueFounder), and four moderator variables (Gender, Industry, Geography, YearFounded)
  - Outlined data linkage strategy across tables using CompanyID, PersonID, and EntityID
  - Defined Ivy League institution list (8 universities) for binary classification
  - Included recommended analysis approach with model specifications
  - Added data quality checks and missing data handling considerations

- **extract_table_info.py**: Temporary Python script to parse comprehensive_analysis.html and extract detailed table and column information from the HTML analysis file
  - Uses BeautifulSoup to extract table metadata, column names, data types, and sample values
  - Provides structured output for 6 key tables relevant to the research question

### Analysis Summary
The variable selection analysis identified:
- **121 columns** from Company.csv (57,751 companies) - primary data source
- **35 columns** from Person.csv (557,995 individuals) - includes Gender variable
- **6 columns** from PersonEducationRelation.csv (586,031 records) - critical for Ivy League identification
- **11 columns** from PersonPositionRelation.csv (561,080 records) - identifies founders
- **108 columns** from Deal.csv (145,894 deals) - supplementary funding details

Key insight: Multiple table joins required to link companies → founders → education → Ivy League classification


