import streamlit as st

st.set_page_config(page_title="NCD Clinical Dashboard", layout="centered")
st.title("🩺 NCD Clinical Dashboard Pro")
st.markdown("ระบบประเมินผลเลือดและเป้าหมายการรักษาผู้ป่วย (DM, HT, DLP, CKD) 📊")

# --- 👤 ข้อมูลผู้ป่วย ---
st.subheader("👤 1. ข้อมูลพื้นฐาน")
age = st.number_input("อายุ (ปี) 🎂", min_value=1, max_value=120, value=60)

# --- เลือกปัจจัยความเสี่ยงหลัก (Logic จัดกลุ่มเบาหวาน) ---
st.subheader("📋 2. ปัจจัยความซับซ้อนของผู้ป่วย")
factors = st.multiselect("เลือกลักษณะที่พบในผู้ป่วย (เพื่อจัดกลุ่มเป้าหมาย DM) 📌:", [
    "Bed ridden", 
    "ต้องใช้ Home oxygen", 
    "มะเร็งระยะกระจาย / Palliative care",
    "Heart failure", 
    "COPD", 
    "CKD eGFR < 60", 
    "Myocardial infarction", 
    "Stroke (ช่วยเหลือตนเองได้)"
])

# --- การตัดสินใจกลุ่มเบาหวาน ---
is_high_complexity = (age > 75) or any(x in factors for x in ["Bed ridden", "ต้องใช้ Home oxygen", "มะเร็งระยะกระจาย / Palliative care"])
is_moderate_complexity = (age > 65) or any(x in factors for x in ["Heart failure", "COPD", "CKD eGFR < 60", "Myocardial infarction", "Stroke (ช่วยเหลือตนเองได้)"])

if is_high_complexity:
    dm_group = "เป็นเบาหวาน (กลุ่มสูงอายุ/ซับซ้อนสูง)"
elif is_moderate_complexity:
    dm_group = "เป็นเบาหวาน (กลุ่มสูงอายุ/ซับซ้อนปานกลาง)"
else:
    dm_group = "เป็นเบาหวาน (กลุ่มสุขภาพดี/ควบคุมเข้มข้น)"

st.info(f"💡 ระบบจัดกลุ่มผู้ป่วยให้อัตโนมัติ: **{dm_group}**")

# --- 🩸 ผล Lab ---
st.subheader("🩸 3. ผลการตรวจทางห้องปฏิบัติการ (Labs)")
col1, col2 = st.columns(2)
with col1:
    fpg = st.number_input("FPG (mg/dL) 🩸", value=100)
    hba1c = st.number_input("HbA1c (%) 🧪", value=6.5, step=0.1)
with col2:
    egfr = st.number_input("eGFR (ml/min) 💧", value=90.0)
    sbp = st.number_input("SBP (mmHg) 🩺", value=120)

# --- 🚨 คัดกรองความเสี่ยงสำหรับกลุ่ม "ควบคุมเข้มข้น" ---
risk_level = "ไม่ได้ประเมิน"
if dm_group == "เป็นเบาหวาน (กลุ่มสุขภาพดี/ควบคุมเข้มข้น)":
    st.markdown("---")
    st.markdown("### 🔍 ประเมินความเสี่ยงการเกิด Complications")
    st.markdown("*(ฟอร์มนี้แสดงเฉพาะกลุ่มผู้ป่วยที่ต้องการการควบคุมอย่างเข้มข้น)*")
    
    col3, col4 = st.columns(2)
    with col3:
        uacr = st.selectbox("💧 ค่า UACR", ["<30", "30-300", ">300"])
        renal = st.selectbox("💧 การทำงานของไต", ["ปกติ", "CrCl < 60", "มีอาการบวม หรือ CrCl < 30"])
        eye = st.selectbox("👁️ จอประสาทตา (DR)", ["ไม่มี Diabetic retinopathy", "Mild NPDR", "Moderate NPDR / การมองเห็นลดลง", "Severe NPDR/PDR / มองไม่เห็นจนกระทบชีวิต"])
    with col4:
        foot = st.selectbox("🦶 การตรวจเท้า", ["ปกติ", "ผิดปกติ", "มีแผลที่เท้า / อาการ claudication", "Digital gangrene"])
        hypo = st.selectbox("📉 ประวัติ Hypoglycemia", ["ไม่มี / นานๆครั้ง", ">= 3 ครั้งต่อสัปดาห์", "รุนแรงจนต้องเข้านอน รพ. ในช่วง 3 เดือน"])
        cvd = st.selectbox("🫀 โรคร่วม (HT, DLP, MI, Stroke)", ["ไม่มี", "มี แต่ควบคุมได้ (ตามเกณฑ์)", "มี แต่ควบคุมไม่ได้ (ตามเกณฑ์)", "Chest pain/Recent stroke <1 ปี/Recent MI <1 ปี/HF <3 เดือน"])

    # ประมวลผล Risk Level
    if (hypo == "รุนแรงจนต้องเข้านอน รพ. ในช่วง 3 เดือน") or (renal == "มีอาการบวม หรือ CrCl < 30") or (eye == "Severe NPDR/PDR / มองไม่เห็นจนกระทบชีวิต") or (cvd == "Chest pain/Recent stroke <1 ปี/Recent MI <1 ปี/HF <3 เดือน") or (foot == "Digital gangrene"):
        risk_level = "ความเสี่ยงสูงมาก / มีโรคแทรกซ้อนรุนแรง 🚨"
    elif (hba1c >= 8.0) or (hypo == ">= 3 ครั้งต่อสัปดาห์") or (uacr == ">300") or (renal == "CrCl < 60") or (eye == "Moderate NPDR / การมองเห็นลดลง") or (cvd == "มี แต่ควบคุมไม่ได้ (ตามเกณฑ์)") or (foot == "มีแผลที่เท้า / อาการ claudication"):
        risk_level = "ความเสี่ยงสูง 🔴"
    elif (7.0 <= hba1c <= 7.5) or (uacr == "30-300") or (eye == "Mild NPDR") or (cvd == "มี แต่ควบคุมได้ (ตามเกณฑ์)") or (foot == "ผิดปกติ"):
        risk_level = "ความเสี่ยงปานกลาง 🟡"
    else:
        risk_level = "ความเสี่ยงต่ำ 🟢"

# --- 🚀 ประมวลผลและสรุป ---
st.markdown("---")
if st.button("ประมวลผลการรักษา (Evaluate) 📊", use_container_width=True):
    st.header("📋 สรุปผลการประเมิน (Assessment)")
    
    # 🚩 สร้างตัวแปรเช็คความผิดปกติ (ถ้าอันไหนตกเกณฑ์ จะเปลี่ยนเป็น True)
    need_doctor_consult = False 

    # DM Eval
    st.write("### 🍬 การควบคุมเบาหวาน (Diabetes)")
    if dm_group == "เป็นเบาหวาน (กลุ่มสุขภาพดี/ควบคุมเข้มข้น)":
        if (80 <= fpg <= 130) and (6.5 <= hba1c <= 7.5):
            st.success("🟢 ระดับน้ำตาลอยู่ในเกณฑ์เป้าหมายเข้มข้น (FPG 80-130, HbA1c 6.5-7.5%)")
        else:
            st.error("🔴 ระดับน้ำตาลไม่เป็นไปตามเป้าหมายควบคุมเข้มข้น")
            need_doctor_consult = True # พบความผิดปกติ
        
        st.write(f"**ระดับความเสี่ยง Complications:** {risk_level}")
        # หากความเสี่ยงสูง ก็ควรพบแพทย์เช่นกัน
        if "ความเสี่ยงสูง" in risk_level:
            need_doctor_consult = True

    elif dm_group == "เป็นเบาหวาน (กลุ่มสูงอายุ/ซับซ้อนปานกลาง)":
        if (90 <= fpg <= 150) and (hba1c < 8.0): 
            st.success("🟢 ระดับน้ำตาลอยู่ในเกณฑ์เป้าหมาย (FPG 90-150, HbA1c <8%)")
        else: 
            st.error("🔴 ระดับน้ำตาลสูงกว่าเป้าหมายควบคุม")
            need_doctor_consult = True # พบความผิดปกติ
    else: # สูงอายุซับซ้อนสูง
        if (100 <= fpg <= 180): 
            st.success("🟢 FPG อยู่ในเกณฑ์ป้องกันวิกฤต (100-180 mg%)")
        else: 
            st.error("🔴 FPG อยู่นอกเกณฑ์ความปลอดภัย")
            need_doctor_consult = True # พบความผิดปกติ

    # HT Eval
    st.write("### 🩺 ความดันโลหิต (Hypertension)")
    if age < 65:
        if sbp < 130: 
            st.success("🟢 SBP อยู่ในเกณฑ์ (<130)")
        else: 
            st.error("🔴 SBP สูงกว่าเกณฑ์")
            need_doctor_consult = True # พบความผิดปกติ
    else: 
        if sbp < 140: 
            st.success("🟢 SBP อยู่ในเกณฑ์ (<140)")
        else: 
            st.error("🔴 SBP สูงกว่าเกณฑ์")
            need_doctor_consult = True # พบความผิดปกติ

    # CKD Eval
    st.write("### 💧 การทำงานของไต (CKD)")
    if egfr < 60: 
        st.error("🔴 พบความเสี่ยงโรคไต (eGFR < 60)")
        need_doctor_consult = True # พบความผิดปกติ
    else: 
        st.success("🟢 eGFR ปกติ (≥ 60)")
        
    # --- 🚨 คำแนะนำสุดท้าย (Final Recommendation) ---
    st.markdown("---")
    st.subheader("📝 แนวทางการดูแล")
    if need_doctor_consult:
        # หากมีความผิดปกติแม้แต่ข้อเดียว จะขึ้นป้ายเตือนสีเหลือง/แดง
        st.warning("⚠️ **ส่งปรึกษาแพทย์เพื่อปรับการรักษา**")
    else:
        # หากผ่านเกณฑ์ทั้งหมด
        st.success("✅ **ดูแลต่อเนื่องตามแผนการรักษาเดิมได้ (ตามนัด)**")
