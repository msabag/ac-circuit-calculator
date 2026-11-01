import math
import matplotlib.pyplot as plt
import streamlit as st

# הגדרת תצורת עמוד
st.set_page_config(
    page_title="מחשבון AC טורי",
    page_icon="🦆",
    layout="wide"
)

# תיקון צבעים וגופנים לכרטיסיות
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
    st.write("ניתוח חשמלי מלא, חישוב מתחים וייצוג ויזואלי ברור.")

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
st.sidebar.header("⚙️ פרמטרים של המעגל")
V = st.sidebar.number_input("מתח המקור V (וולט):", min_value=0.1, value=12.0)
f = st.sidebar.number_input("תדר f (הרץ):", min_value=0.1, value=50.0)
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

# --- חישובים חשמליים ---
Z = math.sqrt(R**2 + Xc**2)
I = V / Z
VR = I * R
VC = I * Xc
phi_rad = math.atan(-Xc / R)
phi_deg = math.degrees(phi_rad)
pf = math.cos(phi_rad)

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
col4.metric("מתח מקור (V)", f"{V:.2f} V")
col5.metric("מתח נגד (VR)", f"{VR:.2f} V")
col6.metric("מתח קבל (VC)", f"{VC:.2f} V")

st.markdown("---")

# --- פירוט נתונים ---
st.write("### 🔹 פירוט רכיבים ומתחים")
st.info(f"""
- **מתח על הנגד ($V_R$):** {VR:.2f} V
- **מתח על הקבל ($V_C$):** {VC:.2f} V
- **בדיקת סכום וקטורי ($V = \\sqrt{{V_R^2 + V_C^2}}$):** {math.sqrt(VR**2 + VC**2):.2f} V
- **זווית מופע ($\phi$):** {phi_deg:.2f}°
""")

st.markdown("---")
st.subheader("📐 ייצוג ויזואלי של המשולשים")

# פונקציית עזר לציור גרף בודד וגדול
def plot_triangle(x, y, x_label, y_label, hypotenuse_label, title, unit):
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.quiver(0, 0, x, 0, angles='xy', scale_units='xy', scale=1, color='#2563eb', label=f'{x_label} = {x:.2f} {unit}')
    ax.quiver(x, 0, 0, -y, angles='xy', scale_units='xy', scale=1, color='#dc2626', label=f'{y_label} = {y:.2f} {unit}')
    ax.quiver(0, 0, x, -y, angles='xy', scale_units='xy', scale=1, color='#16a34a', label=f'{hypotenuse_label} = {math.sqrt(x**2 + y**2):.2f} {unit}')
    
    ax.set_xlim(-x*0.1, x*1.25)
    ax.set_ylim(-y*1.25, y*0.2)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=10)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='lower left', fontsize=11)
    plt.tight_layout()
    return fig

# הצגת המשולשים אחד מתחת לשני (מוגדלים ומותאמים לטלפון)
st.write("#### 1. משולש עכבות")
st.pyplot(plot_triangle(R, Xc, "R", "Xc", "Z", "משולש עכבות (Impedance Triangle)", "Ω"))

st.write("#### 2. משולש מתחים")
st.pyplot(plot_triangle(VR, VC, "VR", "VC", "V", "משולש מתחים (Voltage Triangle)", "V"))

st.write("#### 3. משולש הספקים")
st.pyplot(plot_triangle(P, Q, "P", "Q", "S", "משולש הספקים (Power Triangle)", "VA/W/VAR"))
