import streamlit as st

st.set_page_config(page_title="NCD Clinical Dashboard", layout="centered")
st.title("🩺 NCD Clinical Dashboard Pro")

# --- 👤 ข้อมูลผู้ป่วย ---
st.subheader("👤 ข้อมูลพื้นฐาน")
age = st.number_input("อายุ (ปี)", min_value=1, max_value=120, value=60)

# --- เลือกปัจจัยความเสี่ยง (Logic อัตโนมัติ) ---
st.subheader("📋 เลือกปัจจัยความเสี่ยงของผู้ป่วย")
factors = st.multiselect("เลือกปัจจัยที่พบ (เลือกได้หลายข้อ):", [
    "Bed ridden", 
    "ต้องใช้ Home oxygen", 
    "มะเร็งระยะกระจาย / Palliative care",
    "Heart failure", 
    "COPD", 
    "CKD eGFR < 60", 
    "Myocardial infarction", 
    "Stroke (ช่วยเหลือตนเองได้)"
])

# --- การตัดสินใจกลุ่ม (Logic Calculation) ---
# Logic: ถ้ามีปัจจัยกลุ่มซับซ้อนสูง ให้เข้ากลุ่ม 3 ก่อน ถ้าไม่มีค่อยไปดูกลุ่ม 2 ถ้าไม่มีเลยคือกลุ่ม 1
is_high_complexity = (age > 75) or any(x in factors for x in ["Bed ridden", "ต้องใช้ Home oxygen", "มะเร็งระยะกระจาย / Palliative care"])
is_moderate_complexity = (age > 65) or any(x in factors for x in ["Heart failure", "COPD", "CKD eGFR < 60", "Myocardial infarction", "Stroke (ช่วยเหลือตนเองได้)"])

if is_high_complexity:
    dm_group = "เป็นเบาหวาน (กลุ่มสูงอายุ/ซับซ้อนสูง)"
elif is_moderate_complexity:
    dm_group = "เป็นเบาหวาน (กลุ่มสูงอายุ/ซับซ้อนปานกลาง)"
else:
    dm_group = "เป็นเบาหวาน (กลุ่มสุขภาพดี/ควบคุมเข้มข้น)"

st.info(f"ระบบจัดกลุ่มผู้ป่วยให้ท่าน: **{dm_group}**")

# --- 🩺 ความดันและไขมัน ---
st.subheader("🩺 ความดันโลหิตและไขมัน")
col_ht, col_ldl = st.columns(2)
with col_ht:
    sbp = st.number_input("SBP (mmHg)", value=120)
    dbp = st.number_input("DBP (mmHg)", value=80)
with col_ldl:
    ldl = st.number_input("LDL-C (mg/dL)", value=100)
    tg = st.number_input("TG (mg/dL)", value=150)

# --- 🩸 ผล Lab ---
st.subheader("🩸 ผล Lab อื่นๆ")
fpg = st.number_input("FPG (mg/dL)", value=100)
hba1c = st.number_input("HbA1c (%)", value=6.0, step=0.1)
egfr = st.number_input("eGFR (ml/min)", value=90.0)

# --- 🚀 ประมวลผล ---
if st.button("ประเมินผล (Evaluate)", use_container_width=True):
    st.markdown("---")
    
    # DM Eval
    st.write("### 🍬 สรุปการควบคุม DM")
    if dm_group == "เป็นเบาหวาน (กลุ่มสุขภาพดี/ควบคุมเข้มข้น)":
        if (80 <= fpg <= 130) and (6.5 <= hba1c <= 7.5): st.success("🟢 อยู่ในเกณฑ์เป้าหมายเข้มข้น")
        else: st.error("🔴 นอกเกณฑ์เป้าหมายเข้มข้น")
    elif dm_group == "เป็นเบาหวาน (กลุ่มสูงอายุ/ซับซ้อนปานกลาง)":
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
    else: 
        if sbp < 140 and dbp < 90: st.success("🟢 อยู่ในเกณฑ์ (<140/90)")
        else: st.error("🔴 สูงกว่าเกณฑ์")

    # DLP & CKD Eval
    st.write("### 🧪 สรุปไขมันและไต")
    if egfr < 60: st.error("🔴 พบความเสี่ยงโรคไต (eGFR < 60)")
    else: st.success("🟢 eGFR ปกติ")
    
    # Simple logic for LDL target (can be expanded)
    st.write(f"ผลประเมินไขมัน: LDL ของคุณคือ {ldl} mg/dL")
