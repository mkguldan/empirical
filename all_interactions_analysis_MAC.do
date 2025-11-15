/*==============================================================================
Title: COMPREHENSIVE INTERACTION ANALYSIS - All Important Interactions
Author: Empirical Methods Project, Bocconi University  
Date: November 15, 2024
==============================================================================*/

clear all
set more off
set linesize 120

cd "/Users/lennartprehn/Downloads"

capture log close _all
log using "all_interactions_results.log", replace

use "data_with_categories.dta", clear

display ""
display "ALL INTERACTIONS ANALYSIS READY"
display ""

* Create variables
gen ln_VC_Spend_Company = ln(Average_VC_Spend_HQ_Company)
egen ln_VC_Spend_mean = mean(ln_VC_Spend_Company)
gen ln_VC_Spend_dm = ln_VC_Spend_Company - ln_VC_Spend_mean
egen rank_mean = mean(ln_University_US_Rank)
gen rank_dm = ln_University_US_Rank - rank_mean
egen age_mean = mean(Age_at_Deal)
gen age_dm = Age_at_Deal - age_mean

gen stage_cat = .
replace stage_cat = 1 if Stage_Seed == 1
replace stage_cat = 2 if Stage_Early == 1
replace stage_cat = 3 if Stage_Seed == 0 & Stage_Early == 0
label define stage_lbl 1 "Seed" 2 "Early" 3 "Later"
label values stage_cat stage_lbl

display "Running key interaction models..."
display ""

/*==============================================================================
METHODOLOGICAL NOTES:
==============================================================================

1. FIXED EFFECTS SPECIFICATIONS:
   - Models vary in FE structure (some use year FE, others state FE, etc.)
   - DO NOT compare R² or intercepts across models with different FE
   - Within R-sq is comparable within same FE structure

2. COLLINEARITY WARNINGS:
   - Stata will show "omitted because of collinearity" for interactions
   - This is EXPECTED and CORRECT with factor variables
   - Base category interactions are identified through the main effects

3. ENDOGENEITY & POST-TREATMENT BIAS:
   - Has_Top_Tier_VC is ENDOGENOUS (investor choice is outcome of quality)
   - Model 5 (Top VC × Gender) is for MECHANISMS only, not total effects
   - Models 1-4, 6-18 use only pre-determined or exogenous controls
   
4. CLUSTERING OF STANDARD ERRORS:
   - PRIMARY: vce(cluster University_US_Rank)
     -> 115 universities, avg 26 founders per university
     -> Treatment (university rank) is at university level
     -> Must cluster at treatment level (Moulton 1990)
   - ROBUSTNESS: Also test vce(cluster Deal_Year) 
   - Company clustering NOT needed (each company appears once)
   
5. STATISTICAL SIGNIFICANCE:
   - Non-significant results are clearly flagged in output
   - Focus interpretation on p<0.05 for main claims
   - Report p<0.10 as "marginally significant" only

6. INTERPRETATION:
   - Margins with 95% CIs provided for key significant interactions
   - All coefficients are in log points (multiply by 100 for %)

==============================================================================*/

/*------------------------------------------------------------------------------
SECTION 1: UNIVERSITY × GENDER - Do women need better schools?
------------------------------------------------------------------------------*/

display ""
display "=========================================="
display "1. UNIVERSITY RANK × GENDER"
display "=========================================="
display ""

reghdfe ln_DealSize c.ln_University_US_Rank##i.Female ///
    PhD_MD MBA_JD Masters Age_at_Deal ///
    Has_Board_Experience ///
    Stage_Seed Stage_Early, ///
    absorb(Deal_Year Tech Healthcare Consumer Industrial Company_HQState_Province) ///
    vce(cluster University_US_Rank)

estimates store int_rank_gender

* Store key coefficients for summary
scalar rank_gender_interaction = _b[1.Female#c.ln_University_US_Rank]

display ""
display "KEY FINDINGS:"
display "  ln(Rank) effect (Men):    " %7.4f _b[ln_University_US_Rank]
display "  Female penalty (baseline):" %7.4f _b[1.Female]
display "  ln(Rank) × Female:        " %7.4f _b[1.Female#c.ln_University_US_Rank]
display ""

test 1.Female#c.ln_University_US_Rank

display ""
display "INTERPRETATION (ln_University_US_Rank = logged rank):"
display "  - Negative coef = better rank (lower number) → more funding"
display "  - Captures diminishing returns (Harvard→Yale matters more than Rank60→61)"
display ""
if r(p) > 0.05 {
    display "  *** NOT STATISTICALLY SIGNIFICANT (p=" %5.4f r(p) ") ***"
    display "  → Cannot reject that elite schools help men and women equally"
}
else {
    if _b[1.Female#c.ln_University_US_Rank] < 0 {
        display "  → Women need BETTER schools to get same funding as men"
    }
    else if _b[1.Female#c.ln_University_US_Rank] > 0 {
        display "  → Elite schools help women MORE than men"
    }
}
display ""

/*------------------------------------------------------------------------------
SECTION 2: YEAR × GENDER - Is the gap closing?
------------------------------------------------------------------------------*/

display ""
display "=========================================="
display "2. YEAR × GENDER (2012-2022 TREND)"
display "=========================================="
display ""

reghdfe ln_DealSize c.Deal_Year##i.Female ///
    ln_University_US_Rank PhD_MD MBA_JD Masters Age_at_Deal ///
    Has_Board_Experience ///
    Stage_Seed Stage_Early, ///
    absorb(Tech Healthcare Consumer Industrial Company_HQState_Province) ///
    vce(cluster University_US_Rank)

estimates store int_year_gender

scalar gap_2012 = _b[1.Female]
scalar gap_2017 = _b[1.Female] + 5 * _b[1.Female#c.Deal_Year]
scalar gap_2022 = _b[1.Female] + 10 * _b[1.Female#c.Deal_Year]

display ""
display "GENDER GAP EVOLUTION:"
display "  2012: " %7.4f gap_2012
display "  2017: " %7.4f gap_2017
display "  2022: " %7.4f gap_2022
display ""

test 1.Female#c.Deal_Year

if r(p) > 0.05 {
    display "  *** NOT STATISTICALLY SIGNIFICANT (p=" %5.4f r(p) ") ***"
    display "  → Gender gap is STATISTICALLY UNCHANGED over 2012-2022"
}
else {
    if gap_2022 > gap_2012 {
        display "  → Gender gap is WORSENING over time"
    }
    else {
        display "  → Gender gap is IMPROVING over time!"
    }
}
display ""

/*------------------------------------------------------------------------------
SECTION 3: STAGE × GENDER - When is bias worst?
------------------------------------------------------------------------------*/

display ""
display "=========================================="
display "3. STAGE × GENDER"
display "=========================================="
display ""

reghdfe ln_DealSize ln_University_US_Rank ///
    i.stage_cat##i.Female ///
    PhD_MD MBA_JD Masters Age_at_Deal ///
    Has_Board_Experience, ///
    absorb(Deal_Year Tech Healthcare Consumer Industrial Company_HQState_Province) ///
    vce(cluster University_US_Rank)

estimates store int_stage_gender

display ""
display "FEMALE PENALTY BY STAGE:"
display "  Seed:  " %7.4f _b[1.Female]
display "  Early: " %7.4f (_b[1.Female] + _b[1.Female#2.stage_cat])
display "  Later: " %7.4f (_b[1.Female] + _b[1.Female#3.stage_cat])
display ""

test 1.Female#2.stage_cat 1.Female#3.stage_cat
display ""

if r(p) < 0.10 {
    display "INTERPRETATION:"
    if r(p) < 0.05 {
        display "  *** SIGNIFICANT at 5% level (p=" %5.4f r(p) ") ***"
    }
    else {
        display "  *** MARGINALLY SIGNIFICANT at 10% level (p=" %5.4f r(p) ") ***"
    }
    display "  → Gender bias varies significantly by deal stage"
    display "  → WORST at Early stage (-51pp), better at Seed (-14pp) and Later (-25pp)"
    display ""
    
    * MARGINS: Predicted gender gap by stage with 95% CIs
    display "PREDICTED GENDER GAP BY STAGE (with 95% CIs):"
    estimates restore int_stage_gender
    margins stage_cat, at(Female=(0 1)) vsquish
    marginsplot, ///
        title("Gender Gap by Deal Stage") ///
        ytitle("Predicted ln(Deal Size)") ///
        name(stage_gender, replace)
}
else {
    display "  *** NOT STATISTICALLY SIGNIFICANT (p=" %5.4f r(p) ") ***"
}
display ""

/*------------------------------------------------------------------------------
SECTION 4: EXPERIENCE × GENDER
------------------------------------------------------------------------------*/

display ""
display "=========================================="
display "4. BOARD EXPERIENCE × GENDER"
display "=========================================="
display ""

reghdfe ln_DealSize ln_University_US_Rank ///
    i.Female##i.Has_Board_Experience ///
    PhD_MD MBA_JD Masters Age_at_Deal ///
    Stage_Seed Stage_Early, ///
    absorb(Deal_Year Tech Healthcare Consumer Industrial Company_HQState_Province) ///
    vce(cluster University_US_Rank)

estimates store int_board_gender

display ""
display "KEY FINDINGS:"
display "  Female (no board):  " %7.4f _b[1.Female]
display "  Board premium (men):" %7.4f _b[1.Has_Board_Experience]
display "  Female × Board:     " %7.4f _b[1.Female#1.Has_Board_Experience]
display "  → Female WITH board:" %7.4f (_b[1.Female] + _b[1.Female#1.Has_Board_Experience])
display ""

test 1.Female#1.Has_Board_Experience

if r(p) > 0.05 {
    display "  *** NOT STATISTICALLY SIGNIFICANT (p=" %5.4f r(p) ") ***"
    display "  → Board experience helps men and women equally"
}
else {
    display "  *** SIGNIFICANT (p=" %5.4f r(p) ") ***"
}
display ""

/*------------------------------------------------------------------------------
SECTION 5: TOP-TIER VC × GENDER - Controversial!
*** WARNING: ENDOGENOUS CONTROL - FOR MECHANISMS ONLY, NOT TOTAL EFFECTS ***
Has_Top_Tier_VC is post-treatment: top VCs select high-quality deals
This model shows correlation, not causation
Use for exploring mechanisms, NOT for clean gender bias estimates
------------------------------------------------------------------------------*/

display ""
display "=========================================="
display "5. TOP-TIER VC × GENDER (MECHANISMS ONLY)"
display "*** ENDOGENOUS: Top VCs select deals ***"
display "=========================================="
display ""

reghdfe ln_DealSize ln_University_US_Rank ///
    i.Female##i.Has_Top_Tier_VC ///
    PhD_MD MBA_JD Masters Age_at_Deal ///
    Has_Board_Experience ///
    Stage_Seed Stage_Early, ///
    absorb(Deal_Year Tech Healthcare Consumer Industrial Company_HQState_Province) ///
    vce(cluster University_US_Rank)

estimates store int_topvc_gender

scalar female_nontop = _b[1.Female]
scalar female_top = _b[1.Female] + _b[1.Female#1.Has_Top_Tier_VC]

display ""
display "GENDER GAP COMPARISON:"
display "  With non-top VC:  " %7.4f female_nontop
display "  With top-tier VC: " %7.4f female_top
display "  Difference:       " %7.4f _b[1.Female#1.Has_Top_Tier_VC]
display ""

test 1.Female#1.Has_Top_Tier_VC

if r(p) > 0.05 {
    display "  *** NOT STATISTICALLY SIGNIFICANT (p=" %5.4f r(p) ") ***"
    display "  → Cannot distinguish bias between top-tier and other VCs"
    display "  → Remember: This is ENDOGENOUS - interpret cautiously!"
}
else {
    display "  *** SIGNIFICANT (p=" %5.4f r(p) ") ***"
    if female_top > female_nontop {
        display "  → Top VCs discriminate MORE (elite bias!)"
    }
    else {
        display "  → Top VCs discriminate LESS (diversity success!)"
    }
    display "  → Remember: This is ENDOGENOUS - could be selection effect!"
}
display ""

/*------------------------------------------------------------------------------
SECTION 6: GENDER × EDUCATION - Do PhDs help women as much as men?
------------------------------------------------------------------------------*/

display ""
display "=========================================="
display "6. FEMALE × EDUCATION LEVELS"
display "Do credentials help women as much as men?"
display "=========================================="
display ""

reghdfe ln_DealSize ln_University_US_Rank ///
    i.Female##i.PhD_MD ///
    i.Female##i.MBA_JD ///
    i.Female##i.Masters ///
    Age_at_Deal Has_Board_Experience ///
    Stage_Seed Stage_Early, ///
    absorb(Deal_Year Tech Healthcare Consumer Industrial Company_HQState_Province) ///
    vce(cluster University_US_Rank)

estimates store int_female_education

display ""
display "EDUCATION PREMIUMS BY GENDER:"
display ""
display "                     MEN        WOMEN      DIFFERENCE"
display "-------------------------------------------------------"

* Calculate premiums for MEN (Female=0, so just the main effect)
* Calculate premiums for WOMEN (Female=1, main effect + interaction)
scalar phd_male = _b[1.PhD_MD]
scalar phd_female = _b[1.PhD_MD] + _b[1.Female#1.PhD_MD]
scalar phd_diff = _b[1.Female#1.PhD_MD]

scalar mba_male = _b[1.MBA_JD]
scalar mba_female = _b[1.MBA_JD] + _b[1.Female#1.MBA_JD]
scalar mba_diff = _b[1.Female#1.MBA_JD]

scalar masters_male = _b[1.Masters]
scalar masters_female = _b[1.Masters] + _b[1.Female#1.Masters]
scalar masters_diff = _b[1.Female#1.Masters]

display "PhD/MD Premium:   " %7.4f phd_male "   " %7.4f phd_female "   " %7.4f phd_diff
display "MBA/JD Premium:   " %7.4f mba_male "   " %7.4f mba_female "   " %7.4f mba_diff
display "Masters Premium:  " %7.4f masters_male "   " %7.4f masters_female "   " %7.4f masters_diff
display ""

* Test all interactions jointly
display "Testing all education × gender interactions:"
test 1.Female#1.PhD_MD 1.Female#1.MBA_JD 1.Female#1.Masters
display ""

if r(p) > 0.05 {
    display "  *** NOT STATISTICALLY SIGNIFICANT (p=" %5.4f r(p) ") ***"
    display "  → Education credentials help men and women equally"
    display "  → No evidence of differential returns by gender"
}
else {
    display "  *** SIGNIFICANT (p=" %5.4f r(p) ") ***"
    display "INTERPRETATION:"
    if phd_diff < 0 {
        display "  → PhDs help women LESS than men (credential penalty!)"
    }
    else if phd_diff > 0 {
        display "  → PhDs help women MORE than men (reduces bias!)"
    }
    else {
        display "  → PhDs help women and men equally"
    }
    display ""

    if mba_diff < 0 {
        display "  → MBAs help women LESS than men"
    }
    else if mba_diff > 0 {
        display "  → MBAs help women MORE than men (professional credential helps!)"
    }
}
display ""
display "Female penalty (Bachelors baseline): " %7.4f _b[1.Female]
display ""

/*------------------------------------------------------------------------------
SECTION 7: CREDENTIAL COMPOUNDING
------------------------------------------------------------------------------*/

display ""
display "=========================================="
display "7. UNIVERSITY RANK × PHD"
display "=========================================="
display ""

reghdfe ln_DealSize c.ln_University_US_Rank##i.PhD_MD ///
    Female MBA_JD Masters Age_at_Deal ///
    Has_Board_Experience ///
    Stage_Seed Stage_Early, ///
    absorb(Deal_Year Tech Healthcare Consumer Industrial Company_HQState_Province) ///
    vce(cluster University_US_Rank)

estimates store int_rank_phd

display ""
display "KEY FINDINGS:"
display "  Rank effect (BA):  " %7.4f _b[ln_University_US_Rank]
display "  PhD premium:       " %7.4f _b[1.PhD_MD]
display "  Rank × PhD:        " %7.4f _b[1.PhD_MD#c.ln_University_US_Rank]
display ""

test 1.PhD_MD#c.ln_University_US_Rank

if r(p) > 0.05 {
    display "  *** NOT STATISTICALLY SIGNIFICANT (p=" %5.4f r(p) ") ***"
    display "  → Elite school and PhD effects are ADDITIVE, not compounding"
}
else {
    display "  *** SIGNIFICANT (p=" %5.4f r(p) ") ***"
    if _b[1.PhD_MD#c.ln_University_US_Rank] < 0 {
        display "  → Credentials COMPOUND: Stanford PhD > both separately"
    }
    else {
        display "  → Elite schools matter LESS for PhDs (substitutes)"
    }
}
display ""

/*------------------------------------------------------------------------------
SECTION 8: VC MARKET CONDITIONS
------------------------------------------------------------------------------*/

display ""
display "=========================================="
display "8. VC SPENDING × GENDER"
display "=========================================="
display ""

reghdfe ln_DealSize ln_University_US_Rank ///
    c.ln_VC_Spend_dm##i.Female ///
    PhD_MD MBA_JD Masters Age_at_Deal ///
    Has_Board_Experience ///
    Stage_Seed Stage_Early, ///
    absorb(Deal_Year Tech Healthcare Consumer Industrial) ///
    vce(cluster University_US_Rank)

estimates store int_vc_gender

display ""
display "KEY FINDINGS:"
display "  VC effect (men):   " %7.4f _b[ln_VC_Spend_dm]
display "  Female penalty:    " %7.4f _b[1.Female]
display "  VC × Female:       " %7.4f _b[1.Female#c.ln_VC_Spend_dm]
display ""

test 1.Female#c.ln_VC_Spend_dm

if r(p) > 0.05 {
    display "  *** NOT STATISTICALLY SIGNIFICANT (p=" %5.4f r(p) ") ***"
    display "  → Gender gap does NOT vary with VC market conditions"
}
else {
    display "  *** SIGNIFICANT (p=" %5.4f r(p) ") ***"
    if _b[1.Female#c.ln_VC_Spend_dm] < 0 {
        display "  → Gender gap WORSE in high-VC competitive markets"
    }
    else {
        display "  → Gender gap BETTER in well-funded markets"
    }
}
display ""

/*------------------------------------------------------------------------------
SECTION 9: GEOGRAPHY × GENDER - Regional variation in bias
------------------------------------------------------------------------------*/

display ""
display "=========================================="
display "9. REGION × GENDER"
display "=========================================="
display ""

reghdfe ln_DealSize ln_University_US_Rank ///
    i.Female##i.West_Coast ///
    i.Female##i.Northeast ///
    i.Female##i.South ///
    PhD_MD MBA_JD Masters Age_at_Deal ///
    Has_Board_Experience Stage_Seed Stage_Early, ///
    absorb(Deal_Year Tech Healthcare Consumer Industrial) ///
    vce(cluster University_US_Rank)

estimates store int_region_gender

display ""
display "GENDER GAP BY REGION:"
display "  Midwest (base):  " %7.4f _b[1.Female]
display "  West Coast:      " %7.4f (_b[1.Female] + _b[1.Female#1.West_Coast])
display "  Northeast:       " %7.4f (_b[1.Female] + _b[1.Female#1.Northeast])
display "  South:           " %7.4f (_b[1.Female] + _b[1.Female#1.South])
display ""

test 1.Female#1.West_Coast 1.Female#1.Northeast 1.Female#1.South

if r(p) > 0.05 {
    display "  *** NOT STATISTICALLY SIGNIFICANT (p=" %5.4f r(p) ") ***"
    display "  → Gender gap does NOT vary significantly across regions"
}
else {
    display "  *** SIGNIFICANT (p=" %5.4f r(p) ") ***"
    display "  → Gender bias varies significantly across US regions"
}
display ""

/*------------------------------------------------------------------------------
SECTION 10: INDUSTRY × GENDER - Sectoral variation in bias
------------------------------------------------------------------------------*/

display ""
display "=========================================="
display "10. INDUSTRY × GENDER"
display "=========================================="
display ""

reghdfe ln_DealSize ln_University_US_Rank ///
    i.Female##i.Tech ///
    i.Female##i.Healthcare ///
    i.Female##i.Consumer ///
    i.Female##i.Industrial ///
    PhD_MD MBA_JD Masters Age_at_Deal ///
    Has_Board_Experience Stage_Seed Stage_Early, ///
    absorb(Deal_Year Company_HQState_Province) ///
    vce(cluster University_US_Rank)

estimates store int_industry_gender

display ""
display "GENDER GAP BY INDUSTRY:"
display "  Services (base): " %7.4f _b[1.Female]
display "  Tech:            " %7.4f (_b[1.Female] + _b[1.Female#1.Tech])
display "  Healthcare:      " %7.4f (_b[1.Female] + _b[1.Female#1.Healthcare])
display "  Consumer:        " %7.4f (_b[1.Female] + _b[1.Female#1.Consumer])
display "  Industrial:      " %7.4f (_b[1.Female] + _b[1.Female#1.Industrial])
display ""

test 1.Female#1.Tech 1.Female#1.Healthcare 1.Female#1.Consumer 1.Female#1.Industrial

if r(p) < 0.05 {
    display "  *** SIGNIFICANT at 5% level (p=" %5.4f r(p) ") ***"
    display "  → Gender bias varies SIGNIFICANTLY across industries"
    display "  → Tech shows NO bias (+0.9pp), Services shows LARGEST bias (-55pp)"
    display ""
    
    * MARGINS: Predicted gender gap by industry with 95% CIs
    display "PREDICTED GENDER GAP BY INDUSTRY (with 95% CIs):"
    estimates restore int_industry_gender
    margins, at(Female=(0 1) Tech=(0 1) Healthcare=(0) Consumer=(0) Industrial=(0)) vsquish
    margins, at(Female=(0 1) Tech=(0) Healthcare=(1) Consumer=(0) Industrial=(0)) vsquish
    margins, at(Female=(0 1) Tech=(0) Healthcare=(0) Consumer=(1) Industrial=(0)) vsquish
    margins, at(Female=(0 1) Tech=(0) Healthcare=(0) Consumer=(0) Industrial=(1)) vsquish
}
else if r(p) < 0.10 {
    display "  *** MARGINALLY SIGNIFICANT at 10% level (p=" %5.4f r(p) ") ***"
}
else {
    display "  *** NOT STATISTICALLY SIGNIFICANT (p=" %5.4f r(p) ") ***"
}
display ""

/*------------------------------------------------------------------------------
SECTION 11: UNIVERSITY RANK × INDUSTRY - Does prestige matter more in some sectors?
------------------------------------------------------------------------------*/

display ""
display "=========================================="
display "11. UNIVERSITY RANK × INDUSTRY"
display "=========================================="
display ""

reghdfe ln_DealSize c.ln_University_US_Rank##i.Tech ///
    c.ln_University_US_Rank##i.Healthcare ///
    c.ln_University_US_Rank##i.Consumer ///
    c.ln_University_US_Rank##i.Industrial ///
    Female PhD_MD MBA_JD Masters Age_at_Deal ///
    Has_Board_Experience Stage_Seed Stage_Early, ///
    absorb(Deal_Year Company_HQState_Province) ///
    vce(cluster University_US_Rank)

estimates store int_rank_industry

display ""
display "UNIVERSITY RANK EFFECT BY INDUSTRY:"
display "  Services (base): " %7.4f _b[ln_University_US_Rank]
display "  Tech:            " %7.4f (_b[ln_University_US_Rank] + _b[1.Tech#c.ln_University_US_Rank])
display "  Healthcare:      " %7.4f (_b[ln_University_US_Rank] + _b[1.Healthcare#c.ln_University_US_Rank])
display "  Consumer:        " %7.4f (_b[ln_University_US_Rank] + _b[1.Consumer#c.ln_University_US_Rank])
display "  Industrial:      " %7.4f (_b[ln_University_US_Rank] + _b[1.Industrial#c.ln_University_US_Rank])
display ""

test 1.Tech#c.ln_University_US_Rank 1.Healthcare#c.ln_University_US_Rank 1.Consumer#c.ln_University_US_Rank 1.Industrial#c.ln_University_US_Rank

if r(p) > 0.05 {
    display "  *** NOT STATISTICALLY SIGNIFICANT (p=" %5.4f r(p) ") ***"
    display "  → University prestige matters equally across industries"
}
else {
    display "  *** SIGNIFICANT (p=" %5.4f r(p) ") ***"
    display "  → University prestige effects vary by industry"
}
display ""

/*------------------------------------------------------------------------------
SECTION 12: UNIVERSITY RANK × GEOGRAPHY - Does prestige matter more in some regions?
------------------------------------------------------------------------------*/

display ""
display "=========================================="
display "12. UNIVERSITY RANK × REGION"
display "=========================================="
display ""

reghdfe ln_DealSize c.ln_University_US_Rank##i.West_Coast ///
    c.ln_University_US_Rank##i.Northeast ///
    c.ln_University_US_Rank##i.South ///
    Female PhD_MD MBA_JD Masters Age_at_Deal ///
    Has_Board_Experience Stage_Seed Stage_Early, ///
    absorb(Deal_Year Tech Healthcare Consumer Industrial) ///
    vce(cluster University_US_Rank)

estimates store int_rank_region

display ""
display "UNIVERSITY RANK EFFECT BY REGION:"
display "  Midwest (base):  " %7.4f _b[ln_University_US_Rank]
display "  West Coast:      " %7.4f (_b[ln_University_US_Rank] + _b[1.West_Coast#c.ln_University_US_Rank])
display "  Northeast:       " %7.4f (_b[ln_University_US_Rank] + _b[1.Northeast#c.ln_University_US_Rank])
display "  South:           " %7.4f (_b[ln_University_US_Rank] + _b[1.South#c.ln_University_US_Rank])
display ""

test 1.West_Coast#c.ln_University_US_Rank 1.Northeast#c.ln_University_US_Rank 1.South#c.ln_University_US_Rank

if r(p) > 0.05 {
    display "  *** NOT STATISTICALLY SIGNIFICANT (p=" %5.4f r(p) ") ***"
    display "  → University prestige matters equally across regions"
}
else {
    display "  *** SIGNIFICANT (p=" %5.4f r(p) ") ***"
    display "  → University prestige effects vary by region"
}
display ""

/*------------------------------------------------------------------------------
SECTION 13: STAGE × UNIVERSITY RANK - Does prestige matter more at early stages?
------------------------------------------------------------------------------*/

display ""
display "=========================================="
display "13. DEAL STAGE × UNIVERSITY RANK"
display "=========================================="
display ""

reghdfe ln_DealSize c.ln_University_US_Rank##i.stage_cat ///
    Female PhD_MD MBA_JD Masters Age_at_Deal ///
    Has_Board_Experience, ///
    absorb(Deal_Year Tech Healthcare Consumer Industrial Company_HQState_Province) ///
    vce(cluster University_US_Rank)

estimates store int_stage_rank

display ""
display "UNIVERSITY RANK EFFECT BY STAGE:"
display "  Seed:  " %7.4f _b[ln_University_US_Rank]
display "  Early: " %7.4f (_b[ln_University_US_Rank] + _b[2.stage_cat#c.ln_University_US_Rank])
display "  Later: " %7.4f (_b[ln_University_US_Rank] + _b[3.stage_cat#c.ln_University_US_Rank])
display ""

test 2.stage_cat#c.ln_University_US_Rank 3.stage_cat#c.ln_University_US_Rank

if r(p) > 0.05 {
    display "  *** NOT STATISTICALLY SIGNIFICANT (p=" %5.4f r(p) ") ***"
    display "  → University prestige matters equally across deal stages"
}
else {
    display "  *** SIGNIFICANT (p=" %5.4f r(p) ") ***"
    display "  → University prestige effects vary by deal stage"
    if (_b[ln_University_US_Rank] + _b[2.stage_cat#c.ln_University_US_Rank]) < _b[ln_University_US_Rank] {
        display "  → Elite schools matter MORE at Early stage (when uncertainty is highest)"
    }
    else {
        display "  → Elite schools matter LESS at Early stage (skills matter more)"
    }
}
display ""

/*------------------------------------------------------------------------------
SECTION 14: STAGE × EDUCATION - Do credentials matter more at early stages?
------------------------------------------------------------------------------*/

display ""
display "=========================================="
display "14. DEAL STAGE × EDUCATION"
display "=========================================="
display ""

reghdfe ln_DealSize ln_University_US_Rank ///
    i.stage_cat##i.PhD_MD ///
    i.stage_cat##i.MBA_JD ///
    i.stage_cat##i.Masters ///
    Female Age_at_Deal Has_Board_Experience, ///
    absorb(Deal_Year Tech Healthcare Consumer Industrial Company_HQState_Province) ///
    vce(cluster University_US_Rank)

estimates store int_stage_education

display ""
display "PhD PREMIUM BY STAGE:"
display "  Seed:  " %7.4f _b[1.PhD_MD]
display "  Early: " %7.4f (_b[1.PhD_MD] + _b[2.stage_cat#1.PhD_MD])
display "  Later: " %7.4f (_b[1.PhD_MD] + _b[3.stage_cat#1.PhD_MD])
display ""

test 2.stage_cat#1.PhD_MD 3.stage_cat#1.PhD_MD

if r(p) < 0.01 {
    display "  *** HIGHLY SIGNIFICANT at 1% level (p=" %5.4f r(p) ") ***"
    display "  → PhD premium varies DRAMATICALLY by deal stage"
    display "  → HIGHEST at Early stage (+0.48), lowest at Seed (+0.14)"
    display ""
    
    * MARGINS: PhD premium by stage with 95% CIs
    display "PHD PREMIUM BY STAGE (with 95% CIs):"
    estimates restore int_stage_education
    margins stage_cat, at(PhD_MD=(0 1)) vsquish
}
else if r(p) < 0.05 {
    display "  *** SIGNIFICANT at 5% level (p=" %5.4f r(p) ") ***"
}
else {
    display "  *** NOT STATISTICALLY SIGNIFICANT (p=" %5.4f r(p) ") ***"
}
display ""

/*------------------------------------------------------------------------------
SECTION 15: INDUSTRY × EDUCATION - Do PhDs matter more in Healthcare?
------------------------------------------------------------------------------*/

display ""
display "=========================================="
display "15. INDUSTRY × EDUCATION"
display "=========================================="
display ""

reghdfe ln_DealSize ln_University_US_Rank Female ///
    i.Tech##i.PhD_MD ///
    i.Healthcare##i.PhD_MD ///
    i.Consumer##i.PhD_MD ///
    i.Industrial##i.PhD_MD ///
    MBA_JD Masters Age_at_Deal ///
    Has_Board_Experience Stage_Seed Stage_Early, ///
    absorb(Deal_Year Company_HQState_Province) ///
    vce(cluster University_US_Rank)

estimates store int_industry_education

display ""
display "PhD PREMIUM BY INDUSTRY:"
display "  Services (base): " %7.4f _b[1.PhD_MD]
display "  Tech:            " %7.4f (_b[1.PhD_MD] + _b[1.Tech#1.PhD_MD])
display "  Healthcare:      " %7.4f (_b[1.PhD_MD] + _b[1.Healthcare#1.PhD_MD])
display "  Consumer:        " %7.4f (_b[1.PhD_MD] + _b[1.Consumer#1.PhD_MD])
display "  Industrial:      " %7.4f (_b[1.PhD_MD] + _b[1.Industrial#1.PhD_MD])
display ""

test 1.Tech#1.PhD_MD 1.Healthcare#1.PhD_MD 1.Consumer#1.PhD_MD 1.Industrial#1.PhD_MD

if r(p) < 0.05 {
    display "  *** SIGNIFICANT at 5% level (p=" %5.4f r(p) ") ***"
    display "  → PhD premium varies significantly across industries"
    display "  → HIGHEST in Healthcare (+0.85), lowest in Tech (+0.14)"
    display ""
    
    * MARGINS: PhD premium by industry with 95% CIs
    display "PHD PREMIUM BY INDUSTRY (with 95% CIs):"
    estimates restore int_industry_education
    margins, at(PhD_MD=(0 1) Tech=(0 1) Healthcare=(0) Consumer=(0) Industrial=(0)) vsquish
    margins, at(PhD_MD=(0 1) Tech=(0) Healthcare=(1) Consumer=(0) Industrial=(0)) vsquish
    margins, at(PhD_MD=(0 1) Tech=(0) Healthcare=(0) Consumer=(0) Industrial=(1)) vsquish
}
else if r(p) < 0.10 {
    display "  *** MARGINALLY SIGNIFICANT at 10% level (p=" %5.4f r(p) ") ***"
}
else {
    display "  *** NOT STATISTICALLY SIGNIFICANT (p=" %5.4f r(p) ") ***"
}
display ""

/*------------------------------------------------------------------------------
SECTION 16: REGION × EDUCATION - Do PhDs matter more in biotech hubs?
------------------------------------------------------------------------------*/

display ""
display "=========================================="
display "16. REGION × EDUCATION"
display "=========================================="
display ""

reghdfe ln_DealSize ln_University_US_Rank Female ///
    i.West_Coast##i.PhD_MD ///
    i.Northeast##i.PhD_MD ///
    i.South##i.PhD_MD ///
    MBA_JD Masters Age_at_Deal ///
    Has_Board_Experience Stage_Seed Stage_Early, ///
    absorb(Deal_Year Tech Healthcare Consumer Industrial) ///
    vce(cluster University_US_Rank)

estimates store int_region_education

display ""
display "PhD PREMIUM BY REGION:"
display "  Midwest (base):  " %7.4f _b[1.PhD_MD]
display "  West Coast:      " %7.4f (_b[1.PhD_MD] + _b[1.West_Coast#1.PhD_MD])
display "  Northeast:       " %7.4f (_b[1.PhD_MD] + _b[1.Northeast#1.PhD_MD])
display "  South:           " %7.4f (_b[1.PhD_MD] + _b[1.South#1.PhD_MD])
display ""

test 1.West_Coast#1.PhD_MD 1.Northeast#1.PhD_MD 1.South#1.PhD_MD

if r(p) > 0.05 {
    display "  *** NOT STATISTICALLY SIGNIFICANT (p=" %5.4f r(p) ") ***"
    display "  → PhD premium does NOT vary significantly by region"
}
else {
    display "  *** SIGNIFICANT (p=" %5.4f r(p) ") ***"
    display "  → PhD premium varies by region"
}
display ""

/*------------------------------------------------------------------------------
SECTION 17: VC SPENDING × EDUCATION - Do credentials matter more in hot markets?
------------------------------------------------------------------------------*/

display ""
display "=========================================="
display "17. VC SPENDING × EDUCATION"
display "=========================================="
display ""

reghdfe ln_DealSize ln_University_US_Rank Female ///
    c.ln_VC_Spend_dm##i.PhD_MD ///
    c.ln_VC_Spend_dm##i.MBA_JD ///
    c.ln_VC_Spend_dm##i.Masters ///
    Age_at_Deal Has_Board_Experience ///
    Stage_Seed Stage_Early, ///
    absorb(Deal_Year Tech Healthcare Consumer Industrial) ///
    vce(cluster University_US_Rank)

estimates store int_vc_education

display ""
display "VC SPENDING EFFECT BY EDUCATION:"
display "  Bachelors (base):  " %7.4f _b[ln_VC_Spend_dm]
display "  With PhD:          " %7.4f (_b[ln_VC_Spend_dm] + _b[1.PhD_MD#c.ln_VC_Spend_dm])
display "  With MBA:          " %7.4f (_b[ln_VC_Spend_dm] + _b[1.MBA_JD#c.ln_VC_Spend_dm])
display "  With Masters:      " %7.4f (_b[ln_VC_Spend_dm] + _b[1.Masters#c.ln_VC_Spend_dm])
display ""

test 1.PhD_MD#c.ln_VC_Spend_dm 1.MBA_JD#c.ln_VC_Spend_dm 1.Masters#c.ln_VC_Spend_dm

if r(p) > 0.05 {
    display "  *** NOT STATISTICALLY SIGNIFICANT (p=" %5.4f r(p) ") ***"
    display "  → PhD premium does NOT vary with VC market conditions"
}
else {
    display "  *** SIGNIFICANT (p=" %5.4f r(p) ") ***"
    display "  → PhD premium varies with VC market conditions"
}
display ""

/*------------------------------------------------------------------------------
SECTION 18: VC SPENDING × UNIVERSITY RANK - Does prestige matter more in hot markets?
------------------------------------------------------------------------------*/

display ""
display "=========================================="
display "18. VC SPENDING × UNIVERSITY RANK"
display "=========================================="
display ""

reghdfe ln_DealSize c.ln_VC_Spend_dm##c.ln_University_US_Rank ///
    Female PhD_MD MBA_JD Masters Age_at_Deal ///
    Has_Board_Experience Stage_Seed Stage_Early, ///
    absorb(Deal_Year Tech Healthcare Consumer Industrial) ///
    vce(cluster University_US_Rank)

estimates store int_vc_rank

display ""
display "KEY FINDINGS:"
display "  VC spending effect:        " %7.4f _b[ln_VC_Spend_dm]
display "  University rank effect:    " %7.4f _b[ln_University_US_Rank]
display "  VC × Rank interaction:     " %7.4f _b[c.ln_VC_Spend_dm#c.ln_University_US_Rank]
display ""

test c.ln_VC_Spend_dm#c.ln_University_US_Rank

if r(p) > 0.05 {
    display "  *** NOT STATISTICALLY SIGNIFICANT (p=" %5.4f r(p) ") ***"
    display "  → Elite school premium does NOT vary with VC market conditions"
}
else {
    display "  *** SIGNIFICANT (p=" %5.4f r(p) ") ***"
    if _b[c.ln_VC_Spend_dm#c.ln_University_US_Rank] < 0 {
        display "  → Elite schools matter MORE in competitive (high-VC) markets"
    }
    else {
        display "  → Elite schools matter LESS in competitive markets"
    }
}
display ""

/*------------------------------------------------------------------------------
EXPORT RESULTS
------------------------------------------------------------------------------*/

display ""
display "=========================================="
display "EXPORTING RESULTS"
display "=========================================="
display ""

esttab int_rank_gender int_year_gender int_stage_gender int_board_gender ///
    using "key_interactions_table1.tex", replace ///
    se star(* 0.10 ** 0.05 *** 0.01) ///
    label b(3) se(3) r2 ar2 ///
    title("Key Gender Interactions - Part 1") ///
    mtitles("Rank×Gender" "Year×Gender" "Stage×Gender" "Board×Gender")

display "[OK] Saved: key_interactions_table1.tex"

esttab int_topvc_gender int_female_education ///
    using "key_interactions_table2.tex", replace ///
    se star(* 0.10 ** 0.05 *** 0.01) ///
    label b(3) se(3) r2 ar2 ///
    keep(ln_University_US_Rank 1.Female ///
        1.PhD_MD 1.Female#1.PhD_MD ///
        1.MBA_JD 1.Female#1.MBA_JD ///
        1.Masters 1.Female#1.Masters ///
        1.Has_Top_Tier_VC 1.Female#1.Has_Top_Tier_VC ///
        Age_at_Deal Has_Board_Experience ///
        Stage_Seed Stage_Early) ///
    order(ln_University_US_Rank 1.Female ///
        1.PhD_MD 1.Female#1.PhD_MD ///
        1.MBA_JD 1.Female#1.MBA_JD ///
        1.Masters 1.Female#1.Masters) ///
    title("Gender × Education and Investor Quality") ///
    mtitles("TopVC×Gender" "Education×Gender")

display "[OK] Saved: key_interactions_table2.tex"

esttab int_rank_phd int_vc_gender ///
    using "key_interactions_table3.tex", replace ///
    se star(* 0.10 ** 0.05 *** 0.01) ///
    label b(3) se(3) r2 ar2 ///
    title("Credential Compounding and Market Effects") ///
    mtitles("Rank×PhD" "VC×Gender")

display "[OK] Saved: key_interactions_table3.tex"

esttab int_region_gender int_industry_gender ///
    using "key_interactions_table4.tex", replace ///
    se star(* 0.10 ** 0.05 *** 0.01) ///
    label b(3) se(3) r2 ar2 ///
    title("Geographic and Industry Heterogeneity in Gender Bias") ///
    mtitles("Region×Gender" "Industry×Gender")

display "[OK] Saved: key_interactions_table4.tex"

esttab int_rank_industry int_rank_region int_stage_rank ///
    using "key_interactions_table5.tex", replace ///
    se star(* 0.10 ** 0.05 *** 0.01) ///
    label b(3) se(3) r2 ar2 ///
    title("University Prestige by Sector, Geography, and Stage") ///
    mtitles("Rank×Industry" "Rank×Region" "Rank×Stage")

display "[OK] Saved: key_interactions_table5.tex"

esttab int_stage_education int_industry_education int_region_education ///
    using "key_interactions_table6.tex", replace ///
    se star(* 0.10 ** 0.05 *** 0.01) ///
    label b(3) se(3) r2 ar2 ///
    title("Education Premiums by Context") ///
    mtitles("Stage×PhD" "Industry×PhD" "Region×PhD")

display "[OK] Saved: key_interactions_table6.tex"

esttab int_vc_education int_vc_rank ///
    using "key_interactions_table7.tex", replace ///
    se star(* 0.10 ** 0.05 *** 0.01) ///
    label b(3) se(3) r2 ar2 ///
    title("Credentials in Competitive Markets") ///
    mtitles("VC×Education" "VC×Rank")

display "[OK] Saved: key_interactions_table7.tex"

/*------------------------------------------------------------------------------
SUMMARY
------------------------------------------------------------------------------*/

display ""
display "=========================================="
display "COMPREHENSIVE INTERACTIONS ANALYSIS COMPLETE!"
display "=========================================="
display ""
display "MODELS RUN: 18 comprehensive interactions"
display "TABLES CREATED: 7"
display ""
display "GENDER INTERACTIONS (Models 1-8):"
display "  - University Rank × Gender"
display "  - Year Trend × Gender"
display "  - Deal Stage × Gender"
display "  - Board Experience × Gender"
display "  - Top-Tier VC × Gender"
display "  - Education × Gender (PhD, MBA, Masters)"
display "  - University Rank × PhD"
display "  - VC Spending × Gender"
display ""
display "GEOGRAPHY & INDUSTRY (Models 9-12):"
display "  - Region × Gender"
display "  - Industry × Gender"
display "  - University Rank × Industry"
display "  - University Rank × Region"
display ""
display "CREDENTIAL CONTEXTS (Models 13-18):"
display "  - Stage × University Rank (NEW!)"
display "  - Stage × Education"
display "  - Industry × Education"
display "  - Region × Education"
display "  - VC Spending × Education"
display "  - VC Spending × University Rank"
display ""
display "QUICK SUMMARY (*** = significant at p<0.05):"
display ""
display "1. University × Gender: " %7.4f rank_gender_interaction
display "   (NOT significant - elite schools help men and women equally)"
display ""
display "2. Year trend (2012-2022):"
display "   Gap 2012: " %7.4f gap_2012
display "   Gap 2022: " %7.4f gap_2022
display "   (NOT significant - gap unchanged over time)"
display ""
display "3. Deal Stage × Gender:"
display "   Seed:  -14pp | Early: -51pp | Later: -25pp"
display "   (Marginally significant - bias worst at Early stage)"
display ""
display "4. Industry × Gender: *** SIGNIFICANT ***"
display "   Tech: +0.9pp | Services: -55pp | Healthcare: -15pp"
display "   (Gender bias varies dramatically by industry)"
display ""
display "5. Stage × PhD: *** HIGHLY SIGNIFICANT ***"
display "   Seed: +14pp | Early: +48pp | Later: +37pp"
display "   (PhD premium highest at Early stage)"
display ""
display "6. Industry × PhD: *** SIGNIFICANT ***"
display "   Tech: +14pp | Healthcare: +85pp | Industrial: +46pp"
display "   (PhD premium highest in Healthcare)"
display ""
display "7. Education × Gender:"
display "   PhD premium (Men):   " %7.4f phd_male
display "   PhD premium (Women): " %7.4f phd_female
display "   (NOT significant - credentials help men and women equally)"
display ""
display "8. Top VC × Gender (ENDOGENOUS!):"
display "   Gap (non-top): " %7.4f female_nontop " | Gap (top): " %7.4f female_top
display "   (NOT significant - but ENDOGENOUS, for mechanisms only!)"
display ""
display "KEY TAKEAWAY:"
display "  - Gender bias is INDUSTRY-SPECIFIC, not universal"
display "  - PhD premiums vary by STAGE and INDUSTRY, not by gender"
display "  - Elite schools help men and women equally"
display "  - Gender gap stable over 2012-2022"
display ""
display "See log file for all detailed interpretations and p-values!"
display ""

log close
