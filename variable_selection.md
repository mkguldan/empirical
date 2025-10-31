# Variable Selection for Research Question

## Research Question
**Do U.S.-headquartered startups with Ivy League–educated founders raise significantly more venture capital than those without, and how is this relationship influenced by founder gender, industry sector, geographic context, and the year the startup was founded?**

---

## Key Tables and Variables

### 1. **Company.csv** (Core Entity - 121 columns, 57,751 rows)
This is the primary table containing startup information.

#### Dependent Variable (Outcome):
- **TotalRaised** (float64): Total amount of venture capital raised (USD millions)
  - Alternative measures:
    - **LastFinancingSize** (float64): Size of most recent financing round
    - **LastKnownValuation** (float64): Last known company valuation

#### Control/Filter Variables:
- **CompanyID** (object): Unique identifier for linking across tables
- **CompanyName** (object): Company name
- **HQCountry** (object): Filter for U.S. headquartered companies (= "United States")
- **HQState_Province** (object): State location for geographic analysis
- **HQCity** (object): City location for geographic analysis
- **HQGlobalRegion** (object): Should be "Americas"
- **HQGlobalSubRegion** (object): Should be "North America"

#### Industry Variables (Moderators):
- **PrimaryIndustrySector** (object): Broad industry classification (e.g., "Information Technology")
- **PrimaryIndustryGroup** (object): More specific industry (e.g., "Software")
- **PrimaryIndustryCode** (object): Most granular industry classification

#### Company Characteristics:
- **YearFounded** (float64): Year company was founded (moderator variable)
- **CompanyFinancingStatus** (object): Financing backing type (e.g., "Venture Capital-Backed")
- **BusinessStatus** (object): Current operational status
- **Universe** (object): Category by ownership history (e.g., "VC-backed")
- **FirstFinancingDate** (object): Date of first financing
- **Employees** (float64): Number of employees

---

### 2. **Person.csv** (Core Entity - 35 columns, 557,995 rows)
Contains individual profiles including founders.

#### Key Variables:
- **PersonID** (object): Unique identifier for linking
- **FullName** (object): Person's full name
- **FirstName**, **LastName**, **MiddleName** (object): Name components
- **Gender** (object): Gender of the person (KEY MODERATOR)
  - Sample values: Male, Female
- **University_Institution** (object): Primary university (can help identify Ivy League)
- **PrimaryCompanyID** (object): Link to Company table
- **PrimaryCompany** (object): Company name
- **PrimaryPosition** (object): Job title
- **PrimaryPositionLevel** (object): Position level (to identify "Founder")
- **Location** (object): Person's location
- **State_Province** (object): State location
- **Country** (object): Country

---

### 3. **PersonEducationRelation.csv** (Relationship Table - 6 columns, 586,031 rows)
Links people to their educational background - CRITICAL for Ivy League identification.

#### Key Variables:
- **PersonID** (object): Links to Person.csv
- **Institute** (object): Educational institution name (KEY for Ivy League identification)
  - Ivy League schools to identify:
    - Harvard University
    - Yale University
    - Princeton University
    - Columbia University
    - University of Pennsylvania
    - Brown University
    - Dartmouth College
    - Cornell University
- **Degree** (object): Type of degree (BS, MBA, etc.)
- **Major_Concentration** (object): Field of study
- **GraduatingYear** (float64): Year of graduation

---

### 4. **PersonPositionRelation.csv** (Relationship Table - 11 columns, 561,080 rows)
Links people to their positions at companies - CRITICAL for identifying founders.

#### Key Variables:
- **PersonID** (object): Links to Person.csv
- **EntityID** (object): Links to Company via CompanyID
- **EntityName** (object): Company name
- **EntityType** (object): Type of entity
- **FullTitle** (object): Complete job title
- **PositionLevel** (object): Position classification (KEY - filter for "Founder")
- **IsCurrent** (object): Whether position is current
- **StartDate** (object): When person started position
- **EndDate** (object): When person left position

---

### 5. **EntityBoardTeamRelation.csv** (Relationship Table - 14 columns, 715,454 rows)
Alternative source for linking people to companies and identifying founders.

#### Key Variables:
- **EntityID** (object): Company identifier
- **PersonID** (object): Person identifier
- **PersonName** (object): Person's name
- **FullTitle** (object): Job title (can identify founders)
- **IsCurrent** (object): Current relationship status
- **StartDate** (object): Relationship start date

---

### 6. **Deal.csv** (Transaction Table - 108 columns, 145,894 rows)
Contains detailed deal-level funding information - can provide granular funding analysis.

#### Supplementary Variables:
- **CompanyID** (object): Links to Company.csv
- **CompanyName** (object): Company name
- **DealID** (object): Unique deal identifier
- **DealDate** (object): Date of deal
- **DealSize** (float64): Size of the deal (USD millions)
- **DealType** (object): Type of financing (e.g., "Early Stage VC", "Series B")
- **PostValuation** (float64): Post-money valuation
- **PremoneyValuation** (float64): Pre-money valuation
- **VCRound** (object): Which round of funding
- **DealClass** (object): Classification of deal
- **Investors** (float64): Number of investors in the deal

---

## Data Linkage Strategy

### Primary Analysis Dataset Construction:

1. **Start with Company.csv**
   - Filter: `HQCountry == "United States"`
   - Filter: `CompanyFinancingStatus` contains "Venture Capital" or `Universe` contains "Venture Capital"
   - Extract: CompanyID, TotalRaised, YearFounded, Industry variables, Geographic variables

2. **Link to PersonPositionRelation.csv**
   - Match: EntityID = CompanyID
   - Filter: `PositionLevel == "Founder"` or `FullTitle` contains "Founder"
   - Extract: PersonID for each founder

3. **Link to Person.csv**
   - Match: PersonID from step 2
   - Extract: Gender (KEY MODERATOR VARIABLE)

4. **Link to PersonEducationRelation.csv**
   - Match: PersonID from step 2
   - Create binary variable: `IvyLeague = 1` if Institute is in Ivy League list, else 0
   - Group by CompanyID to create: `HasIvyLeagueFounder` (1 if any founder has Ivy degree)

5. **Company-level aggregation:**
   - For companies with multiple founders:
     - Create: `PercentIvyLeagueFounders` (proportion with Ivy League education)
     - Create: `NumberOfFounders` (count)
     - Create: `PercentFemaleFounders` (proportion female)
     - Create: `HasFemaleFounder` (binary: 1 if any founder is female)
     - Create: `HasIvyLeagueFounder` (binary: 1 if any founder has Ivy League degree)

---

## Variable Definitions for Analysis

### Dependent Variable:
- **TotalRaised**: Total venture capital raised (continuous, USD millions)

### Independent Variable (Primary):
- **HasIvyLeagueFounder**: Binary (1 = at least one founder has Ivy League degree, 0 = none)
- Alternative: **PercentIvyLeagueFounders**: Continuous (0-1, proportion of founders with Ivy degree)

### Moderator Variables:
1. **Founder Gender**:
   - **HasFemaleFounder**: Binary (1 = at least one female founder, 0 = all male)
   - **PercentFemaleFounders**: Continuous (0-1, proportion of female founders)
   - **AllFemaleFounders**: Binary (1 = all founders are female, 0 = otherwise)

2. **Industry Sector**:
   - **PrimaryIndustrySector**: Categorical (e.g., Information Technology, Healthcare, etc.)
   - **PrimaryIndustryGroup**: More granular categorical classification

3. **Geographic Context**:
   - **HQState_Province**: State-level location
   - **HQCity**: City-level location
   - Create binary: **IsInTechHub** (1 = Silicon Valley, NYC, Boston, Austin, Seattle; 0 = other)
   - Create categorical: **Region** (West Coast, East Coast, Midwest, South, etc.)

4. **Year Founded**:
   - **YearFounded**: Continuous year variable
   - Create categorical: **FoundedEra** (e.g., Pre-2000, 2000-2010, 2010-2015, Post-2015)

### Control Variables:
- **NumberOfFounders**: Count of founders per company
- **BusinessStatus**: Current operational status
- **Employees**: Company size
- **FirstFinancingDate**: When company first raised funding
- Create: **YearsSinceFirstFunding**: Time since first funding round

---

## Ivy League Institution List

To create the `IvyLeague` indicator, filter `PersonEducationRelation.Institute` for:

1. Harvard University
2. Yale University
3. Princeton University
4. Columbia University
5. University of Pennsylvania (Penn)
6. Brown University
7. Dartmouth College
8. Cornell University

**Note**: Consider variations in naming:
- "Harvard" vs "Harvard University" vs "Harvard Business School"
- "Penn" vs "University of Pennsylvania" vs "UPenn" vs "Wharton" (business school)
- Use partial string matching or regex to capture all variations

---

## Additional Considerations

### Missing Data Handling:
- **Gender**: May have missing values - decide on exclusion vs. imputation
- **Education**: Not all founders may have education records
- **TotalRaised**: Some companies may have zero or missing values
- Document all missing data patterns

### Potential Additional Variables from Deal.csv:
- **Number of funding rounds**: Count of deals per company
- **Average deal size**: Mean of all DealSize for company
- **Latest deal characteristics**: Most recent funding details
- **Time to first funding**: Days/years from founding to first deal

### Sample Size Considerations:
- After filtering for U.S.-based VC-backed companies with founder information, estimate final N
- Check for sufficient observations in each moderator category
- Assess power for interaction effects

---

## Recommended Analysis Approach

### Model Specification:
```
TotalRaised ~ HasIvyLeagueFounder + HasFemaleFounder + 
              HasIvyLeagueFounder × HasFemaleFounder +
              PrimaryIndustrySector + HQState_Province + YearFounded +
              NumberOfFounders + (other controls)
```

### Alternative specifications to test:
1. Main effects only (no interactions)
2. Two-way interactions (Ivy × Gender, Ivy × Industry, Ivy × Geography, Ivy × Year)
3. Three-way interactions (Ivy × Gender × Industry)
4. Robustness checks with different DV measures (LastFinancingSize, LastKnownValuation)

---

## Data Quality Checks

Before analysis, verify:
1. ✅ All U.S. companies correctly filtered (HQCountry = "United States")
2. ✅ Founder identification is accurate (check PositionLevel patterns)
3. ✅ Ivy League matching captures all variations of institution names
4. ✅ Gender data quality and missingness
5. ✅ TotalRaised has reasonable values (no extreme outliers without justification)
6. ✅ YearFounded is reasonable (e.g., 1900-2024)
7. ✅ No duplicate Company-Founder pairs

---

## Summary

**Core Tables**: Company.csv, Person.csv, PersonEducationRelation.csv, PersonPositionRelation.csv

**Key Linkages**: 
- Company ← PersonPositionRelation (via CompanyID/EntityID) → Person (via PersonID) → PersonEducationRelation (via PersonID)

**Critical Variables**:
- **DV**: TotalRaised
- **IV**: HasIvyLeagueFounder (derived from PersonEducationRelation.Institute)
- **Moderators**: Gender, Industry, Geography, YearFounded

**Sample**: U.S.-based, VC-backed companies with identifiable founders and education records

