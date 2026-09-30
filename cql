library COPD_Comprehensive_Assessment version '1.0.0'

using FHIR version '4.0.1'

include FHIRHelpers version '4.0.1'

// ==========================================
// 1. 資料擷取層 (Data Retrievals)
// ==========================================

define "Post_Bronchodilator_FEV1_FVC":
  Last(
    [Observation: code in "FEV1_FVC_Ratio_Codes"] O
      sort by effective
  ).value as Quantity

define "FEV1_Percent_Predicted":
  Last(
    [Observation: code in "FEV1_Percent_Predicted_Codes"] O
      sort by effective
  ).value as Quantity

define "Moderate_Exacerbation_Count_Past_Year":
  Count(
    [Encounter: code in "COPD_Exacerbation_Encounter_Codes"] E
      where E.period during Interval[Now() - 1 years, Now()]
  )

define "Hospitalized_Exacerbation_Count_Past_Year":
  Count(
    [Encounter: class = 'IMP'] E
      with [Condition: code in "COPD_Exacerbation_Codes"] C
      such that C.encounter ref = E.id
        and E.period during Interval[Now() - 1 years, Now()]
  )

define "mMRC_Score":
  Last(
    [Observation: code in "mMRC_Score_Codes"] O
      sort by effective
  ).value as Integer

define "CAT_Score":
  Last(
    [Observation: code in "CAT_Score_Codes"] O
      sort by effective
  ).value as Integer

define "Blood_Eosinophils_Count":
  Last(
    [Observation: code in "Blood_Eosinophils_Codes"] O
      sort by effective
  ).value as Quantity

// 惡化嚴重度評估指標
define "Dyspnea_VAS": Last([Observation: code in "Dyspnea_VAS_Codes"] O sort by effective).value as Decimal
define "Respiratory_Rate": Last([Observation: code in "Respiratory_Rate_Codes"] O sort by effective).value as Integer
define "Heart_Rate": Last([Observation: code in "Heart_Rate_Codes"] O sort by effective).value as Integer
define "Resting_SaO2": Last([Observation: code in "Resting_SaO2_Codes"] O sort by effective).value as Decimal
define "SaO2_Change": Last([Observation: code in "SaO2_Change_Codes"] O sort by effective).value as Decimal
define "CRP_Level": Last([Observation: code in "CRP_Codes"] O sort by effective).value as Decimal
define "ABG_PaCO2": Last([Observation: code in "ABG_PaCO2_Codes"] O sort by effective).value as Decimal
define "ABG_pH": Last([Observation: code in "ABG_pH_Codes"] O sort by effective).value as Decimal
define "Requires_Hospitalization_Or_ED": false
define "Used_Systemic_Steroids_Or_Antibiotics": false


// ==========================================
// 2. 核心邏輯規則 (Clinical Rules)
// ==========================================

// 先決條件：氣流阻塞判定[cite: 5]
define "Has_COPD_Obstruction":
  "Post_Bronchodilator_FEV1_FVC" < 0.7

// GOLD 嚴重度分級 (1 ~ 4)[cite: 7]
define "GOLD_Grade":
  Case
    when not "Has_COPD_Obstruction" then '無阻塞'
    when "FEV1_Percent_Predicted" >= 80 then 'GOLD 1 (輕度)'
    when "FEV1_Percent_Predicted" >= 50 and "FEV1_Percent_Predicted" < 80 then 'GOLD 2 (中度)'
    when "FEV1_Percent_Predicted" >= 30 and "FEV1_Percent_Predicted" < 50 then 'GOLD 3 (重度)'
    when "FEV1_Percent_Predicted" < 30 then 'GOLD 4 (極重度)'
    else null
  end

// ABE 治療分群風險與症狀判定[cite: 7]
define "Is_High_Risk_E":
  "Moderate_Exacerbation_Count_Past_Year" >= 2 
  or "Hospitalized_Exacerbation_Count_Past_Year" >= 1

define "Is_Low_Risk_AB":
  "Moderate_Exacerbation_Count_Past_Year" between 0 and 1
  and "Hospitalized_Exacerbation_Count_Past_Year" = 0

define "Is_Less_Symptoms_A":
  "mMRC_Score" between 0 and 1 and "CAT_Score" < 10

define "Is_More_Symptoms_B":
  "mMRC_Score" >= 2 or "CAT_Score" >= 10

// ABE 治療處置與建議藥物[cite: 7]
define "ABE_Treatment_Group":
  Case
    when not "Has_COPD_Obstruction" then '不適用'
    when "Is_Low_Risk_AB" and "Is_Less_Symptoms_A" then 'Group A (建議：支氣管擴張劑)'[cite: 7]
    when "Is_Low_Risk_AB" and "Is_More_Symptoms_B" then 'Group B (建議：LABA + LAMA)'[cite: 7]
    when "Is_High_Risk_E" and "Blood_Eosinophils_Count" >= 300 then 'Group E (建議：LABA + LAMA + ICS，因血液嗜酸性白血球 >= 300 顆/ul)'[cite: 7]
    when "Is_High_Risk_E" then 'Group E (建議：LABA + LAMA)'[cite: 7]
    else null
  end

// 急性惡化嚴重度定義[cite: 8]
define "Moderate_Criteria_Count":
  (if "Dyspnea_VAS" >= 5 then 1 else 0)
    + (if "Respiratory_Rate" >= 24 then 1 else 0)
    + (if "Heart_Rate" >= 95 then 1 else 0)
    + (if "Resting_SaO2" < 92 and "SaO2_Change" > 3 then 1 else 0)
    + (if "CRP_Level" >= 10 then 1 else 0)

define "Exacerbation_Severity":
  Case
    when "Requires_Hospitalization_Or_ED" or ("ABG_PaCO2" > 45 and "ABG_pH" < 7.35) then '重度惡化 (需住院/急診，伴隨高碳酸血症與酸中毒)'[cite: 8]
    when not "Requires_Hospitalization_Or_ED" and "Used_Systemic_Steroids_Or_Antibiotics" and "Moderate_Criteria_Count" >= 3 then '中度惡化 (需口服類固醇/抗生素，滿足至少3項指標)'[cite: 8]
    when not "Used_Systemic_Steroids_Or_Antibiotics" then '輕度惡化 (僅用短效支氣管擴張劑)'[cite: 8]
    else '未分類'
  end

// 追蹤評估頻率與方案 (對應表 4-4)[cite: 9]
define "Follow_Up_Schedule":
  Case
    when "GOLD_Grade" = 'GOLD 4 (極重度)' then '至少每半年一次 (測量：肺功能、BMI、mMRC/CAT、SpO2；評估：吸菸、症狀、共病、藥物技巧、遵囑性、營養、肺復原、氧氣治療與介入性治療)'[cite: 9]
    when "GOLD_Grade" in {'GOLD 1 (輕度)', 'GOLD 2 (中度)', 'GOLD 3 (重度)'} then '至少每年一次 (測量：肺功能、BMI、mMRC/CAT；評估：吸菸、症狀、共病、藥物技巧、遵囑性、營養、肺復原需求)'[cite: 9]
    else '不適用'
  end
