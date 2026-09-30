import streamlit as st

st.set_page_config(page_title="COPD 綜合評估與 GOLD ABE 計算器", layout="centered")

st.title("🫁 COPD 慢性阻塞性肺病 - 綜合評估與 ABE 分組工具")
st.markdown("依據最新 GOLD 指引，整合 **FEV1/FVC 確診條件**、**Gold 1-4 嚴重度分級**、**mMRC**、**CAT 量表**與 **ABE 風險分組**。")
st.markdown("---")

# 1. 確診先決條件
st.header("1. 肺功能確診先決條件")
fev1_fvc = st.number_input(
    "支氣管擴張劑後 FEV1/FVC 數值",
    min_value=0.10, max_value=1.00, value=0.62, step=0.01,
    help="正常成人通常大於 0.7；若小於 0.7 代表有氣流受阻（阻塞性病變）。"
)

is_obstructed = fev1_fvc < 0.7

if is_obstructed:
    st.success("✅ 符合 COPD 確診先決條件：FEV1/FVC < 0.7 （有阻塞性通氣障礙）")
else:
    st.warning("⚠️ 數值 ≥ 0.7：未達傳統 COPD 阻塞標準，但若有臨床症狀仍建議由醫師綜合評估。")

st.markdown("---")

# 2. 肺功能嚴重度分級 (Gold 1-4)
st.header("2. 肺功能嚴重度分級 (Gold 1-4)")
fev1_percent = st.slider(
    "支氣管擴張劑後 FEV1 佔預測值百分比 (% predicted)",
    min_value=10, max_value=120, value=75, step=1,
    help="對應圖表中的 Gold 1 至 Gold 4 分級。"
)

if fev1_percent >= 80:
    gold_grade = "GOLD 1 (輕度)"
    gold_desc = "FEV1 ≥ 80% 預測值"
elif fev1_percent >= 50:
    gold_grade = "GOLD 2 (中度)"
    gold_desc = "FEV1 50% - 79% 預測值"
elif fev1_percent >= 30:
    gold_grade = "GOLD 3 (重度)"
    gold_desc = "FEV1 30% - 49% 預測值"
else:
    gold_grade = "GOLD 4 (極重度)"
    gold_desc = "FEV1 < 30% 預測值（建議至少每半年追蹤一次）"

st.info(f"**嚴重度判定**：{gold_grade} ({gold_desc})")

st.markdown("---")

# 3. 症狀評估 (mMRC 與 CAT 8大題)
st.header("3. 症狀嚴重度評估 (mMRC 或 CAT)")

symptom_tab1, symptom_tab2 = st.tabs(["mMRC 呼吸困難量表", "CAT 評估測試 (8大題)"])

with symptom_tab1:
    mmrc_score = st.selectbox(
        "請選擇 mMRC 呼吸困難分級 (0-4分)：",
        options=[0, 1, 2, 3, 4],
        format_func=lambda x: {
            0: "0分 - 僅劇烈運動會喘",
            1: "1分 - 平地快走或爬微坡會喘",
            2: "2分 - 平地走比同齡慢，或需停下來休息",
            3: "3分 - 平地走約百公尺需停下來喘氣",
            4: "4分 - 嚴重到無法離開房間，或穿脫衣物會喘"
        }[x]
    )
    is_mmrc_high = mmrc_score >= 2

with symptom_tab2:
    st.markdown("請針對以下 8 個項目評分（每題 0～5 分）：")
    cat_q1 = st.slider("1. 咳嗽：從不咳嗽 (0) ~ 整天咳嗽 (5)", 0, 5, 1)
    cat_q2 = st.slider("2. 有痰：胸部無痰 (0) ~ 胸部充滿痰 (5)", 0, 5, 1)
    cat_q3 = st.slider("3. 胸悶：完全不胸悶 (0) ~ 非常緊悶 (5)", 0, 5, 1)
    cat_q4 = st.slider("4. 爬坡/樓梯會喘：一點也不會 (0) ~ 非常嚴重 (5)", 0, 5, 1)
    cat_q5 = st.slider("5. 日常活動受限：不受影響 (0) ~ 極度受影響 (5)", 0, 5, 1)
    cat_q6 = st.slider("6. 外出信心：非常有信心 (0) ~ 完全沒信心 (5)", 0, 5, 1)
    cat_q7 = st.slider("7. 睡眠品質：品質很好 (0) ~ 品質很差 (5)", 0, 5, 1)
    cat_q8 = st.slider("8. 體力狀況：體力很好 (0) ~ 毫無體力 (5)", 0, 5, 1)
    
    cat_total = cat_q1 + cat_q2 + cat_q3 + cat_q4 + cat_q5 + cat_q6 + cat_q7 + cat_q8
    st.write(f"**CAT 總分**：{cat_total} 分（≥ 10 分視為高症狀）")
    is_cat_high = cat_total >= 10

# 綜合判定高低症狀
is_high_symptoms = is_mmrc_high or is_cat_high

st.markdown("---")

# 4. 急性惡化與住院風險 (ABE 分組)
st.header("4. 急性惡化與住院風險 (ABE 分組)")
col1, col2 = st.columns(2)

with col1:
    exacerbations = st.number_input("過去一年急性惡化發作次數", min_value=0, max_value=10, value=0, step=1)

with col2:
    hospitalization = st.selectbox("過去一年是否曾因 COPD 住院？", options=[0, 1], format_func=lambda x: "是 (曾住院)" if x == 1 else "否 (無住院)")

# 最終 ABE 判定邏輯
if exacerbations >= 2 or hospitalization >= 1:
    abe_group = "E 組 (高惡化風險)"
    abe_desc = "過去一年急性惡化 ≥ 2 次，或曾因 COPD 住院 ≥ 1 次。不論症狀多寡皆歸在此組。"
    abe_treatment = "建議使用長效抗膽鹼氣管擴張劑 (LAMA)，若惡化嚴重或血液嗜酸性球偏高可考慮 LAMA + LABA 或加上吸入性類固醇 (ICS)。"
elif is_high_symptoms:
    abe_group = "B 組 (高症狀、低風險)"
    abe_desc = "過去一年惡化 < 2 次且無住院，但症狀較多（mMRC ≥ 2 或 CAT ≥ 10）。"
    abe_treatment = "建議使用雙支氣管擴張劑合併治療 (LABA + LAMA)。"
else:
    abe_group = "A 組 (低症狀、低風險)"
    abe_desc = "過去一年惡化 < 2 次且無住院，且症狀較少（mMRC < 2 且 CAT < 10）。"
    abe_treatment = "建議使用任何一種長效型支氣管擴張劑 (LABA 或 LAMA)。"

st.markdown("---")

# 5. 綜合評估總結
st.header("📊 綜合臨床評估結果")

result_box = st.container()
with result_box:
    st.markdown(f"### 🎯 最終分組：**{abe_group}** + **{gold_grade}**")
    st.write(f"• **風險描述**：{abe_desc}")
    st.write(f"• **藥物治療方向**：{abe_treatment}")
    st.write(f"• **肺功能狀態**：{gold_desc}")
    if "GOLD 4" in gold_grade:
        st.warning("⚠️ 屬於重度/極重度肺功能下降，建議至少每半年回診追蹤一次，並評估血氧及氧氣治療需求。")
    else:
        st.info("ℹ️ 建議至少每年定期回診追蹤一次。")