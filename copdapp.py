import streamlit as st

st.set_page_config(page_title="COPD 完整指引與 ABE 綜合計算器", layout="wide")

st.title("🫁 COPD 慢性阻塞性肺病 - 全方位 GOLD 臨床評估與決策系統")
st.markdown("完全依據最新 GOLD 指引與臨床圖表，整合 **ABE 分組用藥（含嗜酸性球判斷）**、**追蹤頻率**以及**急性惡化嚴重度分級**。")
st.markdown("---")

# 建立左右分欄，讓操作更像專業醫療工具
col_left, col_right = st.columns([1, 1])

with col_left:
    st.header("1. 肺功能與確診評估")
    fev1_fvc = st.number_input(
        "支氣管擴張劑後 FEV1/FVC 數值",
        min_value=0.10, max_value=1.00, value=0.62, step=0.01,
        help="正常成人通常大於 0.7；若小於 0.7 代表有氣流受阻（阻塞性病變）。"
    )
    is_obstructed = fev1_fvc < 0.7
    if is_obstructed:
        st.success("✅ 符合 COPD 確診先決條件：FEV1/FVC < 0.7 （有阻塞性通氣障礙）")
    else:
        st.warning("⚠️ 數值 ≥ 0.7：未達傳統 COPD 阻塞標準。")

    fev1_percent = st.slider(
        "支氣管擴張劑後 FEV1 佔預測值百分比 (% predicted)",
        min_value=10, max_value=120, value=75, step=1
    )
    if fev1_percent >= 80:
        gold_grade = "GOLD 1 (輕度)"
        track_freq = "至少每年追蹤一次[cite: 6]"
    elif fev1_percent >= 50:
        gold_grade = "GOLD 2 (中度)"
        track_freq = "至少每年追蹤一次[cite: 6]"
    elif fev1_percent >= 30:
        gold_grade = "GOLD 3 (重度)"
        track_freq = "至少每年追蹤一次[cite: 6]"
    else:
        gold_grade = "GOLD 4 (極重度)"
        track_freq = "至少每半年追蹤一次，需評估血氧及氧氣治療[cite: 6]"

    st.info(f"**嚴重度判定**：{gold_grade} | **追蹤建議**：{track_freq}")

    st.markdown("---")
    st.header("2. 症狀評估 (mMRC 或 CAT)")
    symptom_mode = st.radio("選擇評估量表", ["mMRC 呼吸困難量表", "CAT 評估測試 (8大題)"], horizontal=True)

    is_high_symptoms = False
    if symptom_mode == "mMRC 呼吸困難量表":
        mmrc_score = st.selectbox("mMRC 分級 (0-4分)：", [0, 1, 2, 3, 4], format_func=lambda x: f"{x}分 - " + ["僅劇烈運動會喘", "平地快走或爬微坡會喘", "平地走比同齡慢需休息", "平地走約百公尺需喘氣", "無法離開房間/穿脫衣物會喘"][x])
        is_high_symptoms = mmrc_score >= 2
    else:
        c1 = st.slider("1. 咳嗽 (0-5)", 0, 5, 1)
        c2 = st.slider("2. 有痰 (0-5)", 0, 5, 1)
        c3 = st.slider("3. 胸悶 (0-5)", 0, 5, 1)
        c4 = st.slider("4. 爬樓梯會喘 (0-5)", 0, 5, 1)
        c5 = st.slider("5. 日常活動受限 (0-5)", 0, 5, 1)
        c6 = st.slider("6. 外出信心 (0-5)", 0, 5, 1)
        c7 = st.slider("7. 睡眠品質 (0-5)", 0, 5, 1)
        c8 = st.slider("8. 體力狀況 (0-5)", 0, 5, 1)
        cat_total = c1+c2+c3+c4+c5+c6+c7+c8
        st.write(f"**CAT 總分**：{cat_total} 分（≥ 10 分為高症狀）")
        is_high_symptoms = cat_total >= 10

with col_right:
    st.header("3. ABE 風險分組與用藥細節")
    exacerbations = st.number_input("過去一年中度惡化次數", min_value=0, max_value=10, value=0, step=1)
    hospitalization = st.selectbox("過去一年是否因惡化住院？", [0, 1], format_func=lambda x: "是 (≥1次住院)" if x == 1 else "否")
    
    # E 組血中嗜酸性球數輸入（對應第一張圖細節）
    eos_count = 150
    if exacerbations >= 2 or hospitalization >= 1:
        eos_count = st.number_input("血液中嗜酸性白血球數 (Eosinophils, 顆/ul)", min_value=0, max_value=2000, value=150, step=10, help="對應圖表：若 >= 300 顆/ul 可考慮加用 ICS[cite: 5]")

    # ABE 判定與用藥
    if exacerbations >= 2 or hospitalization >= 1:
        abe_group = "E 組 (高惡化風險)"
        if eos_count >= 300:
            abe_treatment = "LABA + LAMA + ICS (因血中嗜酸性球 ≥ 300 顆/ul)[cite: 5]"
        else:
            abe_treatment = "LABA + LAMA （若惡化持續可評估其他選項）[cite: 5]"
    elif is_high_symptoms:
        abe_group = "B 組 (高症狀、低風險)"
        abe_treatment = "LABA + LAMA (雙支氣管擴張劑)[cite: 5]"
    else:
        abe_group = "A 組 (低症狀、低風險)"
        abe_treatment = "單一長效支氣管擴張劑 (LABA 或 LAMA)[cite: 5]"

    st.markdown("---")
    st.header("4. 急性惡化嚴重度評估 (進階)")
    with st.expander("點此展開：評估本次/近期惡化嚴重度（輕/中/重度）"):
        vas = st.slider("呼吸困難 VAS 分數 (0-10)", 0, 10, 3)
        rr = st.number_input("呼吸頻率 RR (次/分鐘)", 10, 40, 20)
        hr = st.number_input("心跳 HR (次/分鐘)", 50, 150, 80)
        spo2 = st.slider("靜止血氧 SaO2 (%)", 70, 100, 95)
        crp = st.number_input("CRP (mg/L)", 0.0, 100.0, 5.0)
        
        # 依照第三張圖中度標準（滿足5項中的至少3項）：VAS>=5, RR>=24, HR>=95, SaO2<92%且變化>3%, CRP>=10
        mid_conditions = sum([
            vas >= 5,
            rr >= 24,
            hr >= 95,
            spo2 < 92,
            crp >= 10
        ])
        
        if mid_conditions >= 3:
            ex_severity = "中度惡化（滿足多項中度指標：需使用短效支氣管擴張劑、口服類固醇 ± 抗生素，不需住院）[cite: 7]"
        elif vas < 5 and rr < 24 and hr < 95 and spo2 >= 92 and crp < 10:
            ex_severity = "輕度惡化（僅需短效支氣管擴張劑，不需全身性類固醇或抗生素）[cite: 7]"
        else:
            ex_severity = "需注意是否達到重度（若伴隨意識改變、嚴重高碳酸血症或需住院/急診）[cite: 7]"
        
        st.warning(f"**惡化嚴重度判定**：{ex_severity}")

st.markdown("---")
st.header("📊 綜合臨床評估總結")
st.markdown(f"""
- **最終 ABE 分組**：`{abe_group}`
- **建議用藥指引**：`{abe_treatment}`
- **肺功能分級**：`{gold_grade}` （{track_freq}）[cite: 6]
""")
