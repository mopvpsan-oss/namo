import streamlit as st
import pandas as pd

# --- การตั้งค่าพื้นฐาน ---
st.set_page_config(page_title="AI Food Personal Assistant", page_icon="🥗", layout="wide")

# --- ส่วนของการจัดการ Session State (เปรียบเสมือนฐานข้อมูลชั่วคราว) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

# --- ฟังก์ชันคำนวณพลังงาน (BMR & TDEE) ---
def calculate_tdee(weight, height, age, gender, activity):
    # สูตร Harris-Benedict
    if gender == "ชาย":
        bmr = 66 + (13.7 * weight) + (5 * height) - (6.8 * age)
    else:
        bmr = 655 + (9.6 * weight) + (1.8 * height) - (4.7 * age)
    
    activity_map = {
        "ไม่ออกกำลังกาย": 1.2,
        "ออกกำลังกายเบา (1-3 วัน/สัปดาห์)": 1.375,
        "ออกกำลังกายปานกลาง (3-5 วัน/สัปดาห์)": 1.55,
        "ออกกำลังกายหนัก (6-7 วัน/สัปดาห์)": 1.725
    }
    return bmr * activity_map[activity]

# --- ฟังก์ชันแนะนำอาหาร ---
food_recommendations = {
    "อกไก่": {"kcal": 165, "คำอธิบาย": "โปรตีนสูง น้อยไขมัน ดีต่อการสร้างกล้ามเนื้อ"},
    "ปลาแซลมอน": {"kcal": 206, "คำอธิบาย": "โอเมกา-3 สูง ดีสำหรับหัวใจและสมองจำ"},
    "ข้าวกล้อง": {"kcal": 111, "คำอธิบาย": "ใยอาหารสูง ยาวนานอิ่ม มี B-complex"},
    "บรอกโคลี": {"kcal": 34, "คำอธิบาย": "แคลอรี่ต่ำ วิตามิน C สูง ดีต่อสุขภาพ"},
    "ไข่": {"kcal": 78, "คำอธิบาย": "โปรตีนสมบูรณ์ มีลูทีน ดีสำหรับดวงตา"},
    "โยเกิร์ต": {"kcal": 59, "คำอธิบาย": "โปรไบโอติกส์ ดีต่อระบบย่อยอาหาร"},
}

menu_recommendations = [
    {"ชื่อ": "อกไก่นึ่งขิงและข้าวกล้อง", "kcal": 400, "วิธี": "นึ่งอกไก่ 20 นาที ราดน้ำปลาขิง"},
    {"ชื่อ": "สลัดปลาแซลมอนกับผักสด", "kcal": 350, "วิธี": "ย่างปลา 8 นาที ผสมผักและน้ำมันมะกอก"},
    {"ชื่อ": "ข้าวต้มไก่และผักโขม", "kcal": 320, "วิธี": "ต้มไก่กับข้าวกัน 20 นาที ใส่ผักเสริม"},
    {"ชื่อ": "ไข่ตุ๋นกับเห็ดหอม", "kcal": 280, "วิธี": "ตีไข่ คลุกเห็ด ตุ๋น 12 นาที"},
]

def recommend_food(user_prompt):
    """แนะนำอาหารตามคำถามของผู้ใช้"""
    response = ""
    
    if any(word in user_prompt for word in ["หิว", "เบื่อ", "กินอะไร", "แนะนำ"]):
        menu = menu_recommendations[0]
        response = f"💡 **แนะนำเมนู:** {menu['ชื่อ']}\n\n"
        response += f"⏱️ **แคลอรี่:** {menu['kcal']} kcal\n\n"
        response += f"📝 **วิธีทำ:** {menu['วิธี']}\n\n"
        response += f"✨ **เทคนิค:** ใช้วัตถุดิบสดใหม่เพื่อได้ประโยชน์สูงสุด"
    
    elif any(word in user_prompt for word in ["ไข่", "ปลา", "ไก่", "ผัก"]):
        for food, info in food_recommendations.items():
            if food.lower() in user_prompt.lower():
                response = f"🍗 **{food}**\n\n"
                response += f"🔥 **แคลอรี่ (ต่อ 100g):** {info['kcal']} kcal\n\n"
                response += f"✅ **ประโยชน์:** {info['คำอธิบาย']}\n\n"
                response += f"💪 **แนะนำ:** กินพร้อมผักและข้าวเต็มเมล็ดเพื่อความสมดุล"
                break
        else:
            response = "🤔 สามารถถามเรื่อง: ไก่, ปลา, ไข่, ผัก, ข้าวกล้อง, บรอกโคลี หรือ โยเกิร์ต ได้"
    
    elif any(word in user_prompt for word in ["แคลอรี่", "พลังงาน"]):
        tdee = st.session_state.user_data.get("tdee", 2000)
        response = f"📊 **พลังงานที่คุณต้องการต่อวัน:** {tdee:.0f} kcal\n\n"
        response += f"🍽️ **แบ่งเป็นมื้อ:**\n"
        response += f"- มื้อเช้า: {tdee*0.3:.0f} kcal\n"
        response += f"- มื้อกลางวัน: {tdee*0.4:.0f} kcal\n"
        response += f"- มื้อเย็น: {tdee*0.3:.0f} kcal"
    
    elif any(word in user_prompt for word in ["โปรตีน", "โปรไบโอ", "วิตามิน", "ประโยชน์"]):
        response = "🥗 **ความสำคัญของอาหารให้สุขภาพดี:**\n\n"
        response += "🥩 **โปรตีน:** ช่วยสร้างและซ่อมแซมกล้ามเนื้อ ทำให้อิ่มนาน\n\n"
        response += "🥬 **ผัก:** อุดมไปด้วยวิตามินและแร่ธาตุ ช่วยต้านอนุมูลอิสระ\n\n"
        response += "🌾 **ธัญพืช:** ใยอาหารสูง เสถียรระดับน้ำตาล ให้พลังงานยาวนาน\n\n"
        response += "🍨 **โปรไบโอติกส์:** ช่วยระบบย่อยอาหารและภูมิคุ้มกัน"
    
    else:
        response = "😊 ถามเรื่องอาหารเลยครับ เช่น:\n"
        response += "- 'หิวครับ แนะนำเมนูที่อร่อยและแคลอรี่พอดี'\n"
        response += "- 'ข้อมูลเกี่ยวกับโปรตีน'\n"
        response += "- 'วิธีทำให้อาหารน่าอร่อยและมีประโยชน์'\n"
        response += "- 'ปลาดีต่อสุขภาพไหม'"
    
    return response

# --- หน้า Login ---
def login_page():
    st.title("🔐 เข้าสู่ระบบผู้ช่วยอาหาร AI")
    with st.container():
        username = st.text_input("ชื่อผู้ใช้งาน")
        password = st.text_input("รหัสผ่าน", type="password")
        if st.button("เข้าสู่ระบบ"):
            if username and password: # ในระบบจริงต้องเช็ค DB
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("กรุณากรอกข้อมูลให้ครบ")

# --- หน้าหลัก (Dashboard & Chat) ---
def main_app():
    # Sidebar: ข้อมูลผู้ใช้
    with st.sidebar:
        st.title(f"👤 คุณ {st.session_state.username}")
        if st.button("Log out"):
            st.session_state.logged_in = False
            st.rerun()
        
        st.divider()
        st.header("อัปเดตข้อมูลร่างกาย")
        weight = st.number_input("น้ำหนัก (kg)", min_value=30.0, value=65.0)
        height = st.number_input("ส่วนสูง (cm)", min_value=100.0, value=170.0)
        age = st.number_input("อายุ (ปี)", min_value=1, value=25)
        gender = st.radio("เพศ", ["ชาย", "หญิง"])
        activity = st.selectbox("กิจกรรมประจำวัน", [
            "ไม่ออกกำลังกาย", "ออกกำลังกายเบา (1-3 วัน/สัปดาห์)", 
            "ออกกำลังกายปานกลาง (3-5 วัน/สัปดาห์)", "ออกกำลังกายหนัก (6-7 วัน/สัปดาห์)"
        ])
        
        tdee = calculate_tdee(weight, height, age, gender, activity)
        st.session_state.user_data = {"tdee": tdee, "weight": weight}
        
        st.metric("พลังงานที่ควรได้รับต่อวัน", f"{tdee:.0f} kcal")

    # ส่วนกลาง: Chatbot
    st.title("🥗 AI ผู้ช่วยวิเคราะห์อาหารส่วนบุคคล")
    st.write(f"สวัสดีครับคุณ {st.session_state.username} วันนี้ผมจะช่วยวางแผนการกินที่ {tdee:.0f} kcal ให้คุณเอง")

    # แสดงประวัติการสนทนา
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ช่องรับคำถาม
    if prompt := st.chat_input("สอบถามเรื่องอาหารหรือให้แนะนำเมนูได้ที่นี่..."):
        # เก็บข้อความผู้ใช้
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI ตอบโต้ (จำลอง Logic การคิด)
        with st.chat_message("assistant"):
            response = recommend_food(prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.markdown(response)


# --- เรียกใช้งานแอป ---
if st.session_state.logged_in:
    main_app()
else:
    login_page()
