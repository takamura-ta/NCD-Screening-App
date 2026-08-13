import streamlit as st

# --- ⚙️ ตั้งค่าหน้าจอ (UI/UX Configuration) ---
st.set_page_config(page_title="NCD Clinical Dashboard", page_icon="🩺", layout="centered")

# Custom CSS ตกแต่งให้ปุ่มและกรอบดูทันสมัยสไตล์แอปมือถือ
st.markdown("""
    
""", unsafe_allow_html=True)

st.title("🩺 NCD Clinical Dashboard")
st.markdown("ระบบประเมินผลเลือดและเป้าหมายการรักษาผู้ป่วย (DM, HT, DLP, CKD)")
st.markdown("---")

# --- 👤 ส่วนที่ 1: ข้อมูลผู้ป่วย (Patient Profile) ---
st.subheader("👤 1. ข้อมูลและประวัติผู้ป่วย")
col1, col2 = st.columns(2)

with col1:
    age = st.number_input("อายุ (ปี)", min_value=1, max_value=120, value=60)
    is_dm = st.toggle("เป็นโรคเบาหวาน (DM)", value=False)
    
with col2:
    st.markdown("**โรคร่วมและความซับซ้อน (Comorbidities)**")
    has_cad = st.checkbox("Coronary artery disease (MI, PCI, CABG)")
    has_stroke = st.checkbox("Ischemic หรือ Hemorrhagic stroke")
    has_ckd_nd = st.checkbox("CKD eGFR < 60 (Stage 3-5)")
    has_ckd_dialysis = st.checkbox("CKD on Dialysis")
    has_hf_copd = st.checkbox("Heart failure, COPD, ช่วยเหลือตัวเองได้")
    is_severe = st.checkbox("อายุ >75, Bed ridden, มะเร็งระยะกระจาย, Home O2")
    ascvd_high = st.checkbox("ASCVD Risk > 10% หรือ Baseline LDL > 190")

st.markdown("---")

# --- 🩸 ส่วนที่ 2: ผลการตรวจ (Lab Results) ---
st.subheader("🩸 2. ผลการตรวจทางห้องปฏิบัติการ (Labs)")
col3, col4 = st.columns(2)

with col3:
    fpg = st.number_input("FPG (mg/dL)", min_value=0, value=0)
    hba1c = st.number_input("HbA1c (%)", min_value=0.0, value=0.0, step=0.1)
    egfr = st.number_input("eGFR (ml/min/1.73m²)", min_value=0.0, value=0.0, step=0.1)

with col4:
    sbp = st.number_input("SBP (ตัวบน - mmHg)", min_value=0, value=0)
    dbp = st.number_input("DBP (ตัวล่าง - mmHg)", min_value=0, value=0)
    ldl = st.number_input("LDL-C (mg/dL)", min_value=0, value=0)
    tg = st.number_input("Triglyceride (mg/dL)", min_value=0, value=0)

st.markdown("---")

# --- 📊 ส่วนที่ 3: ระบบประมวลผล (Processing Logic) ---
if st.button("ประเมินผลการรักษา (Evaluate)", use_container_width=True):
    st.header("📋 สรุปผลการประเมิน (Assessment)")
    
    # 1. 🍬 ระบบประเมินเบาหวาน (DM Logic)
    st.markdown("### 🍬 การควบคุมเบาหวาน (Diabetes)")
    if not is_dm: # กลุ่มที่ยังไม่เป็นเบาหวาน
        if fpg >= 126 or hba1c >= 6.5:
            st.error("🔴 เข้าเกณฑ์โรคเบาหวาน (FPG ≥ 126 หรือ HbA1c ≥ 6.5%)")
        elif (100 <= fpg <= 125) or (5.7 <= hba1c <= 6.4):
            st.warning("🟡 ภาวะก่อนเบาหวาน (Prediabetes: FPG 100-125 หรือ HbA1c 5.7-6.4%)")
        else:
            st.success("🟢 ผลน้ำตาลปกติ (Normal)")
    else: # กลุ่มที่เป็นเบาหวานแล้ว
        if is_severe or age > 75:
            st.info("🟡 กลุ่มสูงอายุและซับซ้อนสูง (เป้า FPG 100-180 | HbA1c No target)")
            if 100 <= fpg <= 180:
                st.success("🟢 FPG อยู่ในเกณฑ์ป้องกันวิกฤต (100-180)")
            else:
                st.error("🔴 FPG อยู่นอกเกณฑ์ความปลอดภัย (100-180)")
        elif age > 65 or has_hf_copd or has_ckd_nd or has_cad or has_stroke:
            st.info("🟡 กลุ่มสูงอายุ/ซับซ้อนปานกลาง (เป้า FPG 90-150 | HbA1c < 8%)")
            if (90 <= fpg <= 150 or fpg == 0) and (hba1c < 8.0 or hba1c == 0.0):
                st.success("🟢 ระดับน้ำตาลตามเป้าหมายควบคุม")
            else:
                st.error("🔴 น้ำตาลสูงกว่าเป้าหมายควบคุม")
        else:
            st.info("🟡 กลุ่มสุขภาพดีต้องการควบคุมเข้มข้น (เป้า FPG 80-130 | HbA1c 6.5-7.5%)")
            if (80 <= fpg <= 130 or fpg == 0) and (6.5 <= hba1c <= 7.5 or hba1c == 0.0):
                st.success("🟢 ระดับน้ำตาลตามเป้าหมายควบคุม")
            else:
                st.error("🔴 น้ำตาลไม่เป็นไปตามเป้าหมายเข้มข้น")

    # 2. 🩺 ระบบประเมินความดันโลหิต (HT Logic)
    st.markdown("### 🩺 ความดันโลหิต (Hypertension)")
    if sbp > 0 and dbp > 0:
        if age < 65:
            if sbp < 130 and dbp < 80:
                st.success("🟢 ความดันอยู่ในเกณฑ์เป้าหมาย (<130/80)")
            else:
                st.error("🔴 ความดันสูงกว่าเป้าหมาย (เป้าอายุ <65 คือ <130/80)")
        else:
            if sbp < 140 and dbp < 90:
                st.success("🟢 ความดันอยู่ในเกณฑ์เป้าหมาย (<140/90)")
            else:
                st.error("🔴 ความดันสูงกว่าเป้าหมาย (เป้าอายุ ≥65 คือ <140/90)")
    else:
        st.write("➖ ไม่ได้ระบุข้อมูลความดันโลหิต")

    # 3. 🧪 ระบบประเมินไขมันในเลือด (DLP Logic)
    st.markdown("### 🧪 ไขมันในเลือด (Dyslipidemia)")
    if ldl > 0:
        target_ldl = 1000
        target_txt = ""
        
        if has_cad:
            target_ldl, target_txt = 55, "CAD (<55)"
        elif has_stroke:
            target_ldl, target_txt = 70, "Stroke (<70)"
        elif ascvd_high:
            target_ldl, target_txt = 70, "ASCVD Risk >10% หรือ LDL เดิม >190 (<70)"
        elif has_ckd_dialysis:
            target_ldl, target_txt = 9999, "On Dialysis (No target)"
        elif has_ckd_nd:
            target_ldl, target_txt = 100, "CKD Stage 3-5 (<100)"
        elif is_dm:
            target_ldl, target_txt = 100, "DM (<100)"
            
        if target_ldl == 9999:
            st.success("🟢 ไม่ตั้งเป้าหมาย LDL (ผู้ป่วย On Dialysis)")
        elif target_ldl == 1000: # ไม่มีโรคร่วม
            st.write("➖ กรุณาระบุประวัติโรคร่วมเพื่อตั้งเป้าหมาย LDL")
        else:
            if ldl < target_ldl:
                if is_dm and age > 40 and tg >= 150:
                    st.error("🔴 LDL ผ่านเกณฑ์ แต่ Triglyceride สูง (เป้าผู้ป่วย DM >40 ปี: LDL <100 และ TG <150)")
                else:
                    st.success(f"🟢 LDL ตามเป้าหมายเฉพาะโรค {target_txt}")
            else:
                st.error(f"🔴 LDL สูงกว่าเป้าหมายเฉพาะโรค {target_txt}")
    else:
        st.write("➖ ไม่ได้ระบุข้อมูลไขมันในเลือด")

    # 4. 💧 ระบบประเมินโรคไต (CKD Logic)
    st.markdown("### 💧 การทำงานของไต (CKD)")
    if egfr > 0:
        if egfr < 60:
            st.error("🔴 พบความเสี่ยงโรคไตเรื้อรัง: eGFR < 60 (พิจารณาส่งพบแพทย์/ติดตามใกล้ชิด)")
        else:
            st.success("🟢 eGFR ปกติ (≥60)")
    else:
        st.write("➖ ไม่ได้ระบุข้อมูล eGFR")