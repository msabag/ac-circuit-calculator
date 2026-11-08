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
    st.write("ניתוח חשמלי מלא, כולל זוויות מופע של המתח והזרם, וייצוג ויזואלי ברור.")

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

V = st.sidebar.number_input("מתח המקור V (וולט):", min_value=0.1, value=12.0)
theta_v = st.sidebar.number_input("זווית מופע של מקור המתח θv (במעלות):", value=0.0)
f = st.sidebar.number_input("תדר f (הרץ):", min_value=0.1, value=50.0)

if calc_mode == "חישוב רגיל (לפי R ו-C/Xc)":
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
        Xc = st.sidebar.number_input("היגוי קיבולי Xc (באוהם):", min_value=0.1, value=4.0)
        omega = 2 * math.pi * f
        C = 1 / (omega * Xc)
        uF = C * 1e6

    Z = math.sqrt(R**2 + Xc**2)
    I = V / Z
    phi_deg_circuit = math.degrees(math.atan(Xc / R))  # זווית עכבה אבסולוטית

else:
    # --- מצב חישוב הפוך ---
    I = st.sidebar.number_input("זרם המעגל I (אמפר):", min_value=0.01, value=1.34)
    phi_deg_circuit = st.sidebar.number_input("הפרש מופע φ בין מתח לזרם (במעלות, זרם מקדים):", min_value=0.0, max_value=89.9, value=26.57)
    
    phi_rad = math.radians(phi_deg_circuit)
    Z = V / I
    R = Z * math.cos(phi_rad)
    Xc = Z * math.sin(phi_rad)
    
    omega = 2 * math.pi * f
    C = 1 / (omega * Xc) if Xc > 0 else 0
    uF = C * 1e6

# --- חישובי זוויות ומתחים וקטוריים ---
# במעגל קיבולי, הזרם מקדים את המתח ב-phi_deg_circuit
theta_i = theta_v + phi_deg_circuit
theta_vr = theta_i
theta_vc = theta_i - 90.0

VR = I * R
VC = I * Xc
pf = math.cos(math.radians(phi_deg_circuit))

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

# --- פירוט נתונים וזוויות מופע ---
st.write("### 🔹 פירוט רכיבים, מתחים וזוויות מופע")
st.info(
    f"- **מתח מקור וקטורי ($V$):** {V:.2f} ∠ {theta_v:.2f}° V\n"
    f"- **זרם וקטורי במעגל ($I$):** {I:.2f} ∠ {theta_i:.2f}° A\n"
    f"- **מתח וקטורי על הנגד ($V_R$):** {VR:.2f} ∠ {theta_vr:.2f}° V\n"
    f"- **מתח וקטורי על הקבל ($V_C$):** {VC:.2f} ∠ {theta_vc:.2f}° V\n"
    f"- **הפרש מופע ($\phi = \\theta_I - \\theta_V$):** {phi_deg_circuit:.2f}° (הזרם מקדים את המתח)\n"
    f"- **התנגדות ($R$):** {R:.2f} Ω  |  **היגוי קיבולי ($X_C$):** {Xc:.2f} Ω"
)

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

# הצגת המשולשים
st.write("#### 1. משולש עכבות")
st.pyplot(plot_triangle(R, Xc, "R", "Xc", "Z", "משולש עכבות (Impedance Triangle)", "Ω"))

st.write("#### 2. משולש מתחים")
st.pyplot(plot_triangle(VR, VC, "VR", "VC", "V", "משולש מתחים (Voltage Triangle)", "V"))

st.write("#### 3. משולש הספקים")
st.pyplot(plot_triangle(P, Q, "P", "Q", "S", "משולש הספקים (Power Triangle)", "VA/W/VAR"))
