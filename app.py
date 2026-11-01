import math
import matplotlib.pyplot as plt
import streamlit as st

# הגדרת תצורת עמוד - עיצוב בהיר ונקי
st.set_page_config(
    page_title="מחשבון AC טורי",
    page_icon="🦆",
    layout="wide"
)

# סגנון CSS מותאם אישית: רקע בהיר, גופנים בולטים ועיצוב מאיר עיניים
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    h1 {
        color: #1e3a8a;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    </style>
""", unsafe_allow_html=True)

# כותרת ראשית עם ברווז אמבטיה בשטריימל
col_title, col_duck = st.columns([4, 1])
with col_title:
    st.title("⚡ מחשבון מעגל AC טורי (R-C)")
    st.write("ניתוח חשמלי מלא, חישוב מתחים וייצוג ויזואלי מאיר עיניים.")

with col_duck:
    # הצגת ברווז האמבטיה החסידי בראש העמוד
    st.markdown("""
    <div style="text-align: center; font-size: 60px; line-height: 1;">
        🎩<br>🦆
    </div>
    <div style="text-align: center; font-weight: bold; color: #1e3a8a; font-size: 12px;">
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

# --- הצגת תוצאות בערכים מודגשים ---
st.subheader("📊 תוצאות החישוב")

col1, col2, col3 = st.columns(3)
col1.metric("עכבה כוללת (Z)", f"{Z:.2f} Ω")
col2.metric("זרם במעגל (I)", f"{I:.2f} A")
col3.metric("גורם הספק (cos φ)", f"{pf:.3f}")

st.write("") # מרווח

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

# --- חלק ויזואלי: ציור המשולשים בגרף בהיר ---
st.subheader("📐 ייצוג ויזואלי של המשולשים")

# הגדרת סגנון גרף בהיר ונקי ב-Matplotlib
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 4.5), facecolor='#ffffff')

# 1. משולש עכבות
ax1.quiver(0, 0, R, 0, angles='xy', scale_units='xy', scale=1, color='#1d4ed8', label=f'R = {R:.1f} Ω')
ax1.quiver(R, 0, 0, -Xc, angles='xy', scale_units='xy', scale=1, color='#dc2626', label=f'Xc = {Xc:.1f} Ω')
ax1.quiver(0, 0, R, -Xc, angles='xy', scale_units='xy', scale=1, color='#16a34a', label=f'Z = {Z:.1f} Ω')
ax1.set_xlim(-R*0.1, R*1.2)
ax1.set_ylim(-Xc*1.2, Xc*0.2)
ax1.set_title("משולש עכבות", fontsize=12, fontweight='bold', color='#1e293b')
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend(loc='lower left')

# 2. משולש מתחים
ax2.quiver(0, 0, VR, 0, angles='xy', scale_units='xy', scale=1, color='#1d4ed8', label=f'VR = {VR:.1f} V')
ax2.quiver(VR, 0, 0, -VC, angles='xy', scale_units='xy', scale=1, color='#dc2626', label=f'VC = {VC:.1f} V')
ax2.quiver(0, 0, VR, -VC, angles='xy', scale_units='xy', scale=1, color='#16a34a', label=f'V = {V:.1f} V')
ax2.set_xlim(-VR*0.1, VR*1.2)
ax2.set_ylim(-VC*1.2, VC*0.2)
ax2.set_title("משולש מתחים", fontsize=12, fontweight='bold', color='#1e293b')
ax2.grid(True, linestyle='--', alpha=0.6)
ax2.legend(loc='lower left')

# 3. משולש הספקים
ax3.quiver(0, 0, P, 0, angles='xy', scale_units='xy', scale=1, color='#1d4ed8', label=f'P = {P:.1f} W')
ax3.quiver(P, 0, 0, -Q, angles='xy', scale_units='xy', scale=1, color='#dc2626', label=f'Q = {Q:.1f} VAR')
ax3.quiver(0, 0, P, -Q, angles='xy', scale_units='xy', scale=1, color='#16a34a', label=f'S = {S:.1f} VA')
ax3.set_xlim(-P*0.1, P*1.2)
ax3.set_ylim(-Q*1.2, Q*0.2)
ax3.set_title("משולש הספקים", fontsize=12, fontweight='bold', color='#1e293b')
ax3.grid(True, linestyle='--', alpha=0.6)
ax3.legend(loc='lower left')

plt.tight_layout()
st.pyplot(fig)
