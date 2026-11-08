import math
import matplotlib.pyplot as plt
import streamlit as st

# הגדרת תצורת עמוד
st.set_page_config(
    page_title="מחשבון AC טורי",
    page_icon="🦆",
    layout="wide"
)

# תיקון צבעים וגופנים לכרטיסיות התוצאות
st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 12px !important;
        padding: 15px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }
    div[data-testid="stMetric"] label {
        color: #334155 !important;
        font-weight: bold !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# כותרת ראשית עם ברווז אמבטיה בשטריימל
col_title, col_duck = st.columns([4, 1])
with col_title:
    st.title("⚡ מחשבון מעגל AC טורי (R-C)")
    st.write(" ניתוח חשמלי מלא, חישוב ישיר והפוך, וייצוג ויזואלי ברור.")

with col_duck:
    st.markdown("""
    <div style="text-align: center; font-size: 50px; line-height: 1;">
        🎩<br>🦆
    </div>
    <div style="text-align: center; font-weight: bold; color: #38bdf8; font-size: 13px; margin-top: 5px;">
        רב-ברווז בסיעתא דשמיא
    </div>
    """, unsafe_allow_html=True)

# --- תפריט קלט בצד (סיידבר) ---
st.sidebar.header("⚙️ מצב חישוב ופרמטרים")

calc_mode = st.sidebar.radio(
    "בחר מצב חישוב:",
    ("חישוב רגיל (לפי R ו-C/Xc)", "חישוב הפוך (לפי V, I וזווית מופע φ)")
)

f = st.sidebar.number_input("תדר f (הרץ):", min_value=0.1, value=50.0)

if calc_mode == "חישוב רגיל (לפי R ו-C/Xc)":
    V = st.sidebar.number_input("מתח המקור V (וולט):", min_value=0.1, value=12.0)
    R = st.sidebar.number_input("התנגדות הנגד R (אוהם):", min_value=0.1, value=8.0)
    
    c_option = st.sidebar.radio(
        "איך תרצה להזין את הקבל?", ("היגוי קיבולי Xc (באוהם)", "קיבול C (במיקרו-פראד uF)")
    )
    
    if c_option == "קיבול C (במיקרו-פראד uF)":
        uF = st.sidebar.number_input("קיבול C (uF):", min_value=0.01, value=795.77)
        C = uF * 1e-6
        omega = 2 * math.pi * f
        Xc = 1 / (omega * C)
    else:
        Xc = st.sidebar.number_input("היגוי קיבולי Xc (אוהם):", min_value=0.1, value=4.0)
        omega = 2 * math.pi * f
        C = 1 / (omega * Xc)
        uF = C * 1e6

    # חישובים תלויי קלט רגיל
    Z = math.sqrt(R**2 + Xc**2)
    I = V / Z
    phi_deg = -math.degrees(math.atan(Xc / R))

else:
    # --- מצב חישוב הפוך ---
    V = st.sidebar.number_input("מתח המקור V (וולט):", min_value=0.1, value=12.0)
    I = st.sidebar.number_input("זרם המעגל I (אמפר):", min_value=0.01, value=1.34)
    phi_deg_input = st.sidebar.number_input("זווית מופע φ (במעלות, זרם מקדים):", min_value=0.0, max_value=89.9, value=26.57)
    
    phi_deg = -phi_deg_input  # מעגל קיבולי: זווית עכבה שלילית
    phi_rad = math.radians(phi_deg_input)
    
    Z = V / I
    R = Z * math.cos(phi_rad)
    Xc = Z * math.sin(phi_rad)
    
    omega = 2 * math.pi * f
    C = 1 / (omega * Xc) if Xc > 0 else 0
    uF = C * 1e6

# --- חישוב רכיבים משותף ---
VR = I * R
VC = I * Xc
pf = math.cos(math.radians(phi_deg))

P = I**2 * R
Q = I**2 * Xc
S = V * I

# --- הצגת תוצאות ---
st.subheader("📊 תוצאות החישוב")

col1, col2, col3 = st.columns(3)
col1.metric("עכבה כוללת (Z)", f"{Z:.2f} Ω")
col2.metric("זרם במעגל (I)", f"{I:.2f} A")
col3.metric("גורם הספק (cos φ)", f"{pf:.3f}")

st.write("")

col4, col5, col6 = st.columns(3)
col4.metric("מתח נגד (VR)", f"{VR:.2f} V")
col5.metric("מתח קבל (VC)", f"{VC:.2f} V")
col6.metric("קיבול מחושב (C)", f"{uF:.2f} µF")

st.markdown("---")

# --- פירוט נתונים ---
st.write("### 🔹 פירוט רכיבים, מתחים וזווית")
st.info(f"""
- **התנגדות הנגד ($R$):** {R:.2f} Ω
- **היגוי קיבולי ($X_C$):** {Xc:.2f} Ω
- **קיבול הקבל ($C$):** {uF:.2f} µF (בדר f = {f:.1
