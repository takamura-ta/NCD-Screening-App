import streamlit as st
import math

# เพิ่มโค้ดส่วนนี้ไว้หลัง import
st.warning("⚠️ **นี่คือเวอร์ชันทดสอบ (Demo/Beta)** เพื่อการพัฒนาฟีเจอร์ใหม่ หากพบข้อผิดพลาดกรุณาแจ้งผู้พัฒนา")

def calculate_thai_cv_risk(age, sex, sbp, dm, smoking, chol=0, waist=0, height=0):
    """
    Calculates the 10-year Thai CV Risk Score (EGAT-based model, Version 2.5).
    Validated against Rama Thai CV risk score 2.5 (Copyright 2021).
    """
    if age < 30 or age > 70:
        return 0.0 # สูตรนี้ออกแบบมาสำหรับคนอายุ 30-70 ปีครับ

    full_score = 0
    predicted_risk = 0
    sur_root = 0.964588 # อัปเดตตามโค้ดต้นฉบับ

    if sbp >= 70:
        if chol > 0:
            # 🩸 สูตรที่ 1: ใช้ Total Cholesterol (เจาะเลือด)
            full_score = (0.08183 * age) + (0.39499 * sex) + (0.02084 * sbp) + \
                         (0.69974 * dm) + (0.00212 * chol) + (0.41916 * smoking)
            predicted_risk = 1 - (sur_root ** math.exp(full_score - 7.04423))
            
        elif waist > 0 and height > 0:
            # 📏 สูตรที่ 2: ใช้สัดส่วนรอบเอวต่อส่วนสูง (WHR)
            whr = waist / height
            full_score = (0.079 * age) + (0.128 * sex) + (0.019350987 * sbp) + \
                         (0.58454 * dm) + (3.512566 * whr) + (0.459 * smoking)
            predicted_risk = 1 - (sur_root ** math.exp(full_score - 7.712325))
            
        elif waist > 0:
            # 👖 สูตรที่ 3: ใช้แค่รอบเอว (WC) อย่างเดียว
            full_score = (0.08372 * age) + (0.05988 * sex) + (0.02034 * sbp) + \
                         (0.59953 * dm) + (0.01283 * waist) + (0.459 * smoking)
            predicted_risk = 1 - (sur_root ** math.exp(full_score - 7.31047))

    risk_pct = predicted_risk * 100
    return max(0.0, min(100.0, risk_pct))

# --- ⚙️ การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="NCD Clinical Dashboard", layout="centered")
st.title("🩺 NCD Clinical Dashboard Pro")
st.markdown("ระบบประเมินผลเลือดและเป้าหมายการรักษาผู้ป่วย พร้อมประเมิน Thai ASCVD Risk 🇹🇭📊")

# --- 👤 ข้อมูลผู้ป่วย (เพิ่มปัจจัย ASCVD) ---
st.subheader("👤 1. ข้อมูลพื้นฐานและปัจจัยเสี่ยง CVD")
col_demo1, col_demo2 = st.columns(2)
with col_demo1:
    age = st.number_input("อายุ (ปี) 🎂", min_value=1, max_value=120, value=55)
    sex_input = st.radio("เพศ 🚻", ["ชาย", "หญิง"])
    sex = 1 if sex_input == "ชาย" else 0
    smoking_input = st.radio("ประวัติสูบบุหรี่ 🚬", ["ไม่สูบ/เลิกสูบบุหรี่", "ปัจจุบันสูบบุหรี่"])
    smoking = 1 if smoking_input == "ปัจจุบันสูบปัจจุบัน" else 0

with col_demo2:
    height = st.number_input("ส่วนสูง (ซม.) 📏", value=165.0)
    waist = st.number_input("รอบเอว (ซม.) 👖", value=80.0)

# --- เลือกปัจจัยความเสี่ยงหลัก ---
st.subheader("📋 2. ปัจจัยความซับซ้อนของผู้ป่วย")
factors = st.multiselect("เลือกลักษณะที่พบในผู้ป่วย 📌:", [
    "Bed ridden", 
    "ต้องใช้ Home oxygen", 
    "มะเร็งระยะกระจาย / Palliative care",
    "Heart failure", 
    "COPD", 
    "CKD eGFR < 60", 
    "CKD on dialysis",
    "Myocardial infarction (CAD)", 
    "Stroke (ช่วยเหลือตนเองได้)",
    "ประวัติ LDL เดิม > 190"
])

# --- การตัดสินใจกลุ่มเบาหวาน ---
is_high_complexity = (age > 75) or any(x in factors for x in ["Bed ridden", "ต้องใช้ Home oxygen", "มะเร็งระยะกระจาย / Palliative care"])
is_moderate_complexity = (age > 65) or any(x in factors for x in ["Heart failure", "COPD", "CKD eGFR < 60", "Myocardial infarction (CAD)", "Stroke (ช่วยเหลือตนเองได้)"])

if is_high_complexity:
    dm_group = "เป็นเบาหวาน (กลุ่มสูงอายุ/ซับซ้อนสูง)"
elif is_moderate_complexity:
    dm_group = "เป็นเบาหวาน (กลุ่มสูงอายุ/ซับซ้อนปานกลาง)"
else:
    dm_group = "เป็นเบาหวาน (กลุ่มสุขภาพดี/ควบคุมเข้มข้น)"

# เพิ่มตัวเลือกคนไข้ทั่วไป (ยังไม่เป็น DM)
is_dm_toggle = st.toggle("คนไข้ได้รับการวินิจฉัยว่าเป็นเบาหวาน (DM) แล้ว 🍬", value=True)
if not is_dm_toggle:
    dm_group = "ยังไม่เป็นเบาหวาน"
    
st.info(f"💡 ระบบจัดกลุ่ม DM: **{dm_group}**")

# --- 🩸 ผล Lab ---
st.subheader("🩸 3. ความดันโลหิตและผลการตรวจทางห้องปฏิบัติการ (Labs)")
col1, col2 = st.columns(2)
with col1:
    fpg = st.number_input("FPG (mg/dL) 🩸", value=100)
    hba1c = st.number_input("HbA1c (%) 🧪", value=6.5, step=0.1)
    tc = st.number_input("Total Cholesterol (TC) 🟡", value=200)
with col2:
    egfr = st.number_input("eGFR (ml/min) 💧", value=90.0)
    sbp = st.number_input("SBP (mmHg) 🩺", value=130)
    dbp = st.number_input("DBP (mmHg) 🩺", value=80)
    
col3, col4 = st.columns(2)
with col3:
    ldl = st.number_input("LDL-C (mg/dL) 🔴", value=110)
with col4:
    tg = st.number_input("Triglyceride (mg/dL) 🟡", value=150)

# --- 🚨 สเตป 2: คัดกรองความเสี่ยง Complications (เฉพาะ DM เข้มข้น) ---
risk_level = "ไม่ได้ประเมิน"
if dm_group == "เป็นเบาหวาน (กลุ่มสุขภาพดี/ควบคุมเข้มข้น)":
    st.markdown("---")
    st.markdown("### 🔍 ประเมินความเสี่ยงการเกิด Complications")
    col5, col6 = st.columns(2)
    with col5:
        uacr = st.selectbox("💧 ค่า UACR", ["<30", "30-300", ">300"])
        renal = st.selectbox("💧 การทำงานของไต", ["ปกติ", "CrCl < 60", "มีอาการบวม หรือ CrCl < 30"])
        eye = st.selectbox("👁️ จอประสาทตา (DR)", ["ไม่มี Diabetic retinopathy", "Mild NPDR", "Moderate NPDR / การมองเห็นลดลง", "Severe NPDR/PDR / มองไม่เห็นจนกระทบชีวิต"])
    with col6:
        foot = st.selectbox("🦶 การตรวจเท้า", ["ปกติ", "ผิดปกติ", "มีแผลที่เท้า / อาการ claudication", "Digital gangrene"])
        hypo = st.selectbox("📉 ประวัติ Hypoglycemia", ["ไม่มี / นานๆครั้ง", ">= 3 ครั้งต่อสัปดาห์", "รุนแรงจนต้องเข้านอน รพ. ในช่วง 3 เดือน"])
        cvd = st.selectbox("🫀 โรคร่วม (HT, DLP, MI, Stroke)", ["ไม่มี", "มี แต่ควบคุมได้", "มี แต่ควบคุมไม่ได้", "Chest pain/Recent stroke/Recent MI/HF"])

    # ประมวลผล Risk Level
    if (hypo == "รุนแรงจนต้องเข้านอน รพ. ในช่วง 3 เดือน") or (renal == "มีอาการบวม หรือ CrCl < 30") or (eye == "Severe NPDR/PDR / มองไม่เห็นจนกระทบชีวิต") or (cvd == "Chest pain/Recent stroke/Recent MI/HF") or (foot == "Digital gangrene"):
        risk_level = "ความเสี่ยงสูงมาก 🚨"
    elif (hba1c >= 8.0) or (hypo == ">= 3 ครั้งต่อสัปดาห์") or (uacr == ">300") or (renal == "CrCl < 60") or (eye == "Moderate NPDR / การมองเห็นลดลง") or (cvd == "มี แต่ควบคุมไม่ได้") or (foot == "มีแผลที่เท้า / อาการ claudication"):
        risk_level = "ความเสี่ยงสูง 🔴"
    elif (7.0 <= hba1c <= 7.5) or (uacr == "30-300") or (eye == "Mild NPDR") or (cvd == "มี แต่ควบคุมได้") or (foot == "ผิดปกติ"):
        risk_level = "ความเสี่ยงปานกลาง 🟡"
    else:
        risk_level = "ความเสี่ยงต่ำ 🟢"

# --- 🚀 ประมวลผลและสรุป ---
st.markdown("---")
if st.button("ประมวลผลการรักษา (Evaluate) 📊", use_container_width=True):
    st.header("📋 สรุปผลการประเมิน (Assessment)")
    need_doctor_consult = False 
    
    # คำนวณ ASCVD Risk 🫀
    is_dm_num = 1 if is_dm_toggle else 0
    ascvd_risk = 0.0
    if sbp > 0:
        if tc > 0:
            ascvd_risk = calculate_thai_cv_risk(age, sex, sbp, is_dm_num, smoking, chol=tc)
        else:
            ascvd_risk = calculate_thai_cv_risk(age, sex, sbp, is_dm_num, smoking, waist=waist, height=height)
            
    st.write("### 🫀 ความเสี่ยงหลอดเลือดหัวใจและสมอง (Thai ASCVD Risk)")
    if ascvd_risk > 10.0:
        st.error(f"🔴 **10-Year ASCVD Risk = {ascvd_risk:.2f}%** (ความเสี่ยงสูง > 10%)")
    else:
        st.success(f"🟢 **10-Year ASCVD Risk = {ascvd_risk:.2f}%** (ความเสี่ยง < 10%)")

    # DM Eval 🍬
    st.write("### 🍬 การควบคุมเบาหวาน (Diabetes)")
    if not is_dm_toggle:
        if fpg >= 126 or hba1c >= 6.5: 
            st.error("🔴 เข้าเกณฑ์โรคเบาหวาน")
            need_doctor_consult = True
        elif (100 <= fpg <= 125) or (5.7 <= hba1c <= 6.4): 
            st.warning("🟡 ภาวะก่อนเบาหวาน (Prediabetes)")
        else: 
            st.success("🟢 ปกติ")
    else:
        if dm_group == "เป็นเบาหวาน (กลุ่มสุขภาพดี/ควบคุมเข้มข้น)":
            if (80 <= fpg <= 130) and (6.5 <= hba1c <= 7.5): st.success("🟢 ระดับน้ำตาลอยู่ในเกณฑ์เป้าหมายเข้มข้น")
            else: 
                st.error("🔴 ระดับน้ำตาลไม่เป็นไปตามเป้าหมายควบคุมเข้มข้น")
                need_doctor_consult = True
            st.write(f"**ระดับความเสี่ยง Complications:** {risk_level}")
            if "ความเสี่ยงสูง" in risk_level: need_doctor_consult = True
        elif dm_group == "เป็นเบาหวาน (กลุ่มสูงอายุ/ซับซ้อนปานกลาง)":
            if (90 <= fpg <= 150) and (hba1c < 8.0): st.success("🟢 ระดับน้ำตาลอยู่ในเกณฑ์เป้าหมาย")
            else: 
                st.error("🔴 ระดับน้ำตาลสูงกว่าเป้าหมายควบคุม")
                need_doctor_consult = True
        else: 
            if (100 <= fpg <= 180): st.success("🟢 FPG อยู่ในเกณฑ์ป้องกันวิกฤต")
            else: 
                st.error("🔴 FPG อยู่นอกเกณฑ์ความปลอดภัย")
                need_doctor_consult = True

    # HT Eval 🩺
    st.write("### 🩺 ความดันโลหิต (Hypertension)")
    if age < 65:
        if sbp < 130 and dbp < 80: st.success("🟢 ความดันอยู่ในเกณฑ์ (<130/80)")
        else: 
            st.error("🔴 ความดันสูงกว่าเกณฑ์ (<130/80)")
            need_doctor_consult = True
    else: 
        if sbp < 140 and dbp < 90: st.success("🟢 ความดันอยู่ในเกณฑ์ (<140/90)")
        else: 
            st.error("🔴 ความดันสูงกว่าเกณฑ์ (<140/90)")
            need_doctor_consult = True

    # DLP Eval 🧪 (อัปเดตตาม ASCVD Risk)
    st.write("### 🧪 ไขมันในเลือด (Dyslipidemia)")
    
    has_cad = "Myocardial infarction (CAD)" in factors
    has_stroke = "Stroke (ช่วยเหลือตนเองได้)" in factors
    has_high_baseline = "ประวัติ LDL เดิม > 190" in factors
    has_ckd = "CKD eGFR < 60" in factors
    is_dialysis = "CKD on dialysis" in factors

    dlp_target = 999
    target_text = ""
    
    if is_dialysis:
        dlp_target = 9999
        target_text = "On Dialysis (No target LDL)"
    elif has_cad:
        dlp_target = 55
        target_text = "Coronary Artery Disease (เป้า LDL < 55)"
    elif has_stroke or has_high_baseline:
        dlp_target = 70
        target_text = "Stroke หรือ Baseline LDL > 190 (เป้า LDL < 70)"
    elif (ascvd_risk > 10.0) or is_dm_toggle or has_ckd:
        dlp_target = 100
        reasons = []
        if ascvd_risk > 10.0: reasons.append("Thai ASCVD Risk > 10%")
        if is_dm_toggle: reasons.append("DM")
        if has_ckd: reasons.append("CKD Stage 3-5")
        target_text = " / ".join(reasons) + " (เป้า LDL < 100)"

    if ldl > 0:
        if dlp_target == 9999:
            st.success(f"🟢 {target_text}")
        elif dlp_target != 999:
            if ldl < dlp_target:
                # เช็คเงื่อนไข DM พิเศษ: อายุ > 40 ต้องดู TG < 150 ด้วย
                if is_dm_toggle and age >= 40 and tg >= 150:
                    st.error("🔴 LDL ผ่านเกณฑ์ แต่ Triglyceride สูง (เป้าผู้ป่วย DM >40 ปี: LDL <100 และ TG <150)")
                    need_doctor_consult = True
                else:
                    st.success(f"🟢 LDL ตามเป้าหมาย {target_text}")
            else:
                st.error(f"🔴 LDL สูงกว่าเป้าหมาย {target_text}")
                need_doctor_consult = True
        else:
            st.write("ไม่มีเกณฑ์โรคร่วมที่ต้องคุม LDL เป็นพิเศษ")

    # CKD Eval 💧
    st.write("### 💧 การทำงานของไต (CKD)")
    if egfr > 0:
        if egfr < 60: 
            st.error("🔴 พบความเสี่ยงโรคไต (eGFR < 60)")
            need_doctor_consult = True
        else: st.success("🟢 eGFR ปกติ (≥ 60)")
        
    # --- 🚨 คำแนะนำสุดท้าย ---
    st.markdown("---")
    st.subheader("📝 แนวทางการดูแล")
    if need_doctor_consult:
        st.warning("⚠️ **ส่งปรึกษาแพทย์เพื่อปรับการรักษา**")
    else:
        st.success("✅ **ดูแลต่อเนื่องตามแผนการรักษาเดิมได้ (ตามนัด)**")
