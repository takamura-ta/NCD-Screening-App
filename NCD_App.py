import streamlit as st

st.set_page_config(page_title="NCD Clinical Dashboard", layout="centered")
st.title("🩺 NCD Clinical Dashboard Pro")

# --- 👤 ข้อมูลผู้ป่วย ---
st.subheader("👤 ข้อมูลพื้นฐาน")
age = st.number_input("อายุ (ปี)", min_value=1, max_value=120, value=60)

# --- 🍬 เบาหวาน (DM) Logic ---
st.subheader("🍬 เบาหวาน (Diabetes)")
dm_status = st.radio("สถานะโรคเบาหวาน", ["ยังไม่เป็นเบาหวาน", "เป็นเบาหวาน (กลุ่มสุขภาพดี/ควบคุมเข้มข้น)", "เป็นเบาหวาน (กลุ่มสูงอายุ/ซับซ้อนปานกลาง)", "เป็นเบาหวาน (กลุ่มสูงอายุ/ซับซ้อนสูง)"])

# --- 🩺 ความดัน (HT) Logic ---
st.subheader("🩺 ความดันโลหิต (Hypertension)")
sbp = st.number_input("SBP (ตัวบน - mmHg)", min_value=0, value=0)
dbp = st.number_input("DBP (ตัวล่าง - mmHg)", min_value=0, value=0)

# --- 🧪 ไขมัน (DLP) Logic ---
st.subheader("🧪 ไขมัน (Dyslipidemia)")
ldl = st.number_input("LDL-C (mg/dL)", min_value=0, value=0)
tg = st.number_input("Triglyceride (mg/dL)", min_value=0, value=0)
egfr = st.number_input("eGFR (ml/min/1.73m²)", min_value=0.0, value=0.0)

dlp_risk = st.selectbox("เลือกกลุ่มความเสี่ยงไขมัน", 
                        ["ไม่มีโรคร่วม", "Baseline LDL > 190", "ASCVD risk > 10%", 
                         "เบาหวาน (อายุ < 40 ปี)", "เบาหวาน (อายุ >= 40 ปี)", 
                         "CKD Stage 3-5ND", "CKD on dialysis", 
                         "Coronary Artery Disease", "Stroke"])

# --- 🩸 ผล Lab เพิ่มเติม ---
fpg = st.number_input("FPG (mg/dL)", min_value=0, value=0)
hba1c = st.number_input("HbA1c (%)", min_value=0.0, value=0.0)

# --- 🚀 ประมวลผล ---
if st.button("ประเมินผล (Evaluate)", use_container_width=True):
    st.markdown("---")
    
    # DM Eval
    st.write("### 🍬 สรุปการควบคุม DM")
    if dm_status == "ยังไม่เป็นเบาหวาน":
        if fpg >= 126 or hba1c >= 6.5: st.error("🔴 โรคเบาหวาน (FPG ≥ 126 หรือ HbA1c ≥ 6.5%)")
        elif (100 <= fpg <= 125) or (5.7 <= hba1c <= 6.4): st.warning("🟡 ภาวะก่อนเบาหวาน")
        else: st.success("🟢 ปกติ")
    elif dm_status == "เป็นเบาหวาน (กลุ่มสุขภาพดี/ควบคุมเข้มข้น)":
        if (80 <= fpg <= 130) and (6.5 <= hba1c <= 7.5): st.success("🟢 อยู่ในเกณฑ์เป้าหมายเข้มข้น")
        else: st.error("🔴 นอกเกณฑ์เป้าหมายเข้มข้น")
    elif dm_status == "เป็นเบาหวาน (กลุ่มสูงอายุ/ซับซ้อนปานกลาง)":
        if (90 <= fpg <= 150) and (hba1c < 8.0): st.success("🟢 อยู่ในเกณฑ์เป้าหมาย")
        else: st.error("🔴 นอกเกณฑ์เป้าหมาย")
    else: # สูงอายุซับซ้อนสูง
        if (100 <= fpg <= 180): st.success("🟢 FPG อยู่ในเกณฑ์ปลอดภัย")
        else: st.error("🔴 FPG อยู่นอกเกณฑ์")

    # HT Eval
    st.write("### 🩺 สรุปความดันโลหิต")
    if age < 65:
        if sbp < 130 and dbp < 80: st.success("🟢 อยู่ในเกณฑ์ (<130/80)")
        else: st.error("🔴 สูงกว่าเกณฑ์")
    else: # 65-79
        if sbp < 140 and dbp < 90: st.success("🟢 อยู่ในเกณฑ์ (<140/90)")
        else: st.error("🔴 สูงกว่าเกณฑ์")

    # DLP Eval
    st.write("### 🧪 สรุปไขมันในเลือด")
    target = 999
    if dlp_risk == "Baseline LDL > 190": target = 70
    elif dlp_risk == "ASCVD risk > 10%": target = 100
    elif dlp_risk == "เบาหวาน (อายุ < 40 ปี)": target = 100
    elif dlp_risk == "เบาหวาน (อายุ >= 40 ปี)": target = 100
    elif dlp_risk == "CKD Stage 3-5ND": target = 100
    elif dlp_risk == "Coronary Artery Disease": target = 55
    elif dlp_risk == "Stroke": target = 70
    
    if dlp_risk == "CKD on dialysis": st.success("🟢 No target LDL")
    elif target != 999:
        if ldl < target:
            if "เบาหวาน (อายุ >= 40 ปี)" in dlp_risk and tg >= 150: st.error("🔴 LDL ผ่าน แต่ Triglyceride สูง (>150)")
            else: st.success(f"🟢 LDL < {target}")
        else: st.error(f"🔴 LDL สูงกว่าเป้าหมาย (< {target})")

    # CKD Eval
    if egfr > 0:
        if egfr < 60: st.error("🔴 eGFR < 60 (โรคไต)")
        else: st.success("🟢 eGFR ปกติ")
