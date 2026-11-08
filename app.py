import math
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# הגדרת תצורת עמוד
st.set_page_config(
    page_title="מחשבון AC טורי",
    page_icon="🦆",
    layout="wide"
)

# עיצוב מותאם אישית: כרטיסיות, חץ מונפש והבלטת כפתור הסיידבר
st.markdown("""
    <style>
    /* עיצוב כרטיסיות התוצאות */
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
    
    /* הבלטת כפתור פתיחת ה-Sidebar של Streamlit בפינה */
    button[data-testid="baseButton-header"] {
        background-color: #0284c7 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        font-size: 20px !important;
    }

    /* תיבת הנחיה בולטת עם חץ זז */
    .input-arrow-box {
        background: linear-gradient(135deg, #0284c7, #0369a1);
        color: white;
        padding: 14px 20px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(2, 132, 199, 0.3);
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .animated-arrow {
        font-size: 24px;
        animation: pulse-arrow 1.2s infinite alternate;
    }

    @keyframes pulse-arrow {
        0% { transform: translateX(0px); }
        100% { transform: translateX(-8px); }
    }
    </style>
""", unsafe_allow_html=True)

# תיבת הנחיה בולטת בראש העמוד
st.markdown("""
    <div class="input-arrow-box">
        <span class="animated-arrow">👈</span>
        <span>לחץ על החץ בפינה / פתח את סרגל הצד כדי להזין ולשנות נתונים</span>
    </div>
""", unsafe_allow_html=True)

# כותרת ראשית עם ברווז אמבטיה בשטריימל
col_title, col_duck = st.columns([4, 1])
with col_title:
    st.title("⚡ מחשבון מעגל AC טורי (R-C)")
    st.write("גמיש לחלוטין: תמיכה בקלט מינימלי או מקסימלי מפורט לבחירתך.")

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
    ("חישוב רגיל (מזערי/מלא לפי R ו-C/Xc)", "חישוב הפוך (לפי V, I וזוויות/הפרשים)")
)

st.sidebar.subheader("📌 נתוני מקור ותדר (אופציונלי)")
V_rms = st.sidebar.number_input("מתח המקור V (וולט RMS):", min_value=0.1, value=50.0)

# זווית מופע אופציונלית למקור
use_theta_v = st.sidebar.checkbox("הוסף זווית מופע למקור המתח (θv)", value=True)
theta_v = st.sidebar.number_input("זווית מופע θv (מעלות):", value=68.0) if use_theta_v else 0.0

# תדר אופציונלי
use_frequency = st.sidebar.checkbox("הוסף תדר f (נדרש לחישוב C ב-µF)", value=True)
f = st.sidebar.number_input("תדר f (הרץ):", min_value=0.1, value=50.0) if use_frequency else None

if calc_mode == "חישוב רגיל (מזערי/מלא לפי R ו-C/Xc)":
    st.sidebar.subheader("🔌 רכיבי המעגל")
    R = st.sidebar.number_input("התנגדות הנגד R (אוהם):", min_value=0.0, value=21.865)
    
    if use_frequency:
        c_option = st.sidebar.radio(
            "איך תרצה להזין את הקבל?", ("קיבול C (במיקרו-פראד uF)", "היגוי קיבולי Xc (באוהם)")
        )
    else:
        c_option = "היגוי קיבולי Xc (באוהם)"
        st.sidebar.caption("ללא תדר, הזנת הקבל היא לפי היגוי קיבולי Xc בלבד.")
    
    if c_option == "קיבול C (במיקרו-פראד uF)":
        uF = st.sidebar.number_input("קיבול C (uF):", min_value=0.01, value=262.0)
        C = uF * 1e-6
        omega = 2 * math.pi * f
        Xc = 1 / (omega * C)
    else:
        Xc = st.sidebar.number_input("היגוי קיבולי Xc (באוהם):", min_value=0.0, value=12.15)
        if use_frequency and Xc > 0:
            omega = 2 * math.pi * f
            C = 1 / (omega * Xc)
            uF = C * 1e6
        else:
            C, uF = None, None

    # חישוב עכבה וזרם
    Z = math.sqrt(R**2 + Xc**2)
    I_rms = V_rms / Z if Z > 0 else 0
    phi_deg_circuit = math.degrees(math.atan(Xc / R)) if R > 0 else 90.0
    theta_i = theta_v + phi_deg_circuit

else:
    # --- מצב חישוב הפוך ---
    st.sidebar.subheader("🔄 נתוני זרם וזוויות")
    I_rms = st.sidebar.number_input("זרם המעגל I (אמפר RMS):", min_value=0.01, value=2.0)
    
    angle_input_mode = st.sidebar.radio(
        "איך תרצה להזין זוויות?",
        ("זווית זרם ישירה (θi)", "הפרש מופע ישיר (φ = θi - θv)")
    )
    
    if angle_input_mode == "זווית זרם ישירה (θi)":
        theta_i = st.sidebar.number_input("זווית מופע של הזרם θi (במעלות):", value=97.0)
        phi_deg_circuit = theta_i - theta_v
    else:
        phi_deg_circuit = st.sidebar.number_input("הפרש מופע φ (במעלות, זרם מקדים):", value=29.0)
        theta_i = theta_v + phi_deg_circuit
    
    phi_rad = math.radians(phi_deg_circuit)
    Z = V_rms / I_rms if I_rms > 0 else 0
    R = Z * math.cos(phi_rad)
    Xc = Z * math.sin(phi_rad)
    
    if use_frequency and Xc > 0:
        omega = 2 * math.pi * f
        C = 1 / (omega * Xc)
        uF = C * 1e6
    else:
        C, uF = None, None

# --- חישובי זוויות ומתחים וקטוריים ---
theta_vr = theta_i
theta_vc = theta_i - 90.0

VR_rms = I_rms * R
VC_rms = I_rms * Xc
pf = math.cos(math.radians(phi_deg_circuit))

P = I_rms**2 * R
Q = I_rms**2 * Xc
S = V_rms * I_rms

# --- הצגת תוצאות ---
st.subheader("📊 תוצאות החישוב")

col1, col2, col3 = st.columns(3)
col1.metric("עכבה כוללת (Z)", f"{Z:.2f} Ω")
col2.metric("זרם במעגל (I)", f"{I_rms:.2f} A")
col3.metric("גורם הספק (cos φ)", f"{pf:.3f}")

st.write("")

col4, col5, col6 = st.columns(3)
col4.metric("התנגדות הנגד (R)", f"{R:.3f} Ω")
col5.metric("היגוי קיבולי (Xc)", f"{Xc:.2f} Ω")
if uF is not None:
    col6.metric("קיבול מחושב (C)", f"{uF:.2f} µF")
else:
    col6.metric("קיבול מחושב (C)", "לא הוגדר תדר")

st.markdown("---")

# --- פירוט נתונים וזוויות מופע ---
st.write("### 🔹 פירוט רכיבים, מתחים וזוויות מופע")
c_text = f"{uF:.2f} µF" if uF is not None else "לא מחושב (אין תדר)"
st.info(
    f"- **התנגדות הנגד ($R$):** {R:.3f} Ω\n"
    f"- **היגוי קיבולי ($X_C$):** {Xc:.2f} Ω\n"
    f"- **קיבול ($C$):** {c_text}\n"
    f"- **מתח מקור וקטורי ($V$):** {V_rms:.2f} ∠ {theta_v:.2f}° V\n"
    f"- **זרם וקטורי במעגל ($I$):** {I_rms:.2f} ∠ {theta_i:.2f}° A\n"
    f"- **הפרש מופע ($\phi = \\theta_I - \\theta_V$):** {phi_deg_circuit:.2f}°\n"
    f"- **מתח וקטורי על הנגד ($V_R$):** {VR_rms:.2f} ∠ {theta_vr:.2f}° V\n"
    f"- **מתח וקטורי על הקבל ($V_C$):** {VC_rms:.2f} ∠ {theta_vc:.2f}° V"
)

st.markdown("---")

# --- חלק ויזואלי 1: גרפי סינוס בזמן ---
st.subheader("🌊 גרפי סינוס של מתח וזרם בזמן t")

V_peak = V_rms * math.sqrt(2)
I_peak = I_rms * math.sqrt(2)

f_draw = f if use_frequency else 50.0
T = 1 / f_draw
t = np.linspace(0, 2 * T, 1000)

omega_draw = 2 * np.pi * f_draw
v_t = V_peak * np.sin(omega_draw * t + math.radians(theta_v))
i_t = I_peak * np.sin(omega_draw * t + math.radians(theta_i))

fig_sine, ax_v = plt.subplots(figsize=(8, 4.5))

color_v = '#2563eb'
color_i = '#dc2626'

ax_v.set_xlabel('זמן t (שניות)', fontsize=11)
ax_v.set_ylabel(f'מתח v(t) [V]', color=color_v, fontsize=11, fontweight='bold')
line1 = ax_v.plot(t * 1000, v_t, color=color_v, linewidth=2, label=f'v(t) [Vm={V_peak:.1f}V, θv={theta_v:.1f}°]')
ax_v.tick_params(axis='y', labelcolor=color_v)
ax_v.grid(True, linestyle='--', alpha=0.5)

ax_i = ax_v.twinx()
ax_i.set_ylabel(f'זרם i(t) [A]', color=color_i, fontsize=11, fontweight='bold')
line2 = ax_i.plot(t * 1000, i_t, color=color_i, linewidth=2, linestyle='--', label=f'i(t) [Im={I_peak:.1f}A, θi={theta_i:.1f}°]')
ax_i.tick_params(axis='y', labelcolor=color_i)

lines = line1 + line2
labels = [l.get_label() for l in lines]
ax_v.legend(lines, labels, loc='upper right', fontsize=10)

plt.title(f"אותות סינוס בזמן (הפרש מופע φ = {phi_deg_circuit:.1f}°)", fontsize=13, fontweight='bold', pad=10)
plt.tight_layout()
st.pyplot(fig_sine)

st.markdown("---")

# --- חלק ויזואלי 2: משולשים ---
st.subheader("📐 ייצוג ויזואלי של המשולשים")

def plot_triangle(x, y, x_label, y_label, hypotenuse_label, title, unit):
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.quiver(0, 0, x, 0, angles='xy', scale_units='xy', scale=1, color='#2563eb', label=f'{x_label} = {x:.2f} {unit}')
    ax.quiver(x, 0, 0, -y, angles='xy', scale_units='xy', scale=1, color='#dc2626', label=f'{y_label} = {y:.2f} {unit}')
    ax.quiver(0, 0, x, -y, angles='xy', scale_units='xy', scale=1, color='#16a34a', label=f'{hypotenuse_label} = {math.sqrt(x**2 + y**2):.2f} {unit}')
    
    x_min = min(0, x) * 1.25 if x < 0 else -abs(x)*0.1
    x_max = max(0, x) * 1.25 if x > 0 else abs(x)*0.1
    y_min = -abs(y)*1.25
    y_max = abs(y)*0.2
    
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=10)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='lower left', fontsize=11)
    plt.tight_layout()
    return fig

st.write("#### 1. משולש עכבות")
st.pyplot(plot_triangle(R, Xc, "R", "Xc", "Z", "משולש עכבות (Impedance Triangle)", "Ω"))

st.write("#### 2. משולש מתחים")
st.pyplot(plot_triangle(VR_rms, VC_rms, "VR", "VC", "V", "משולש מתחים (Voltage Triangle)", "V"))

st.write("#### 3. משולש הספקים")
st.pyplot(plot_triangle(P, Q, "P", "Q", "S", "משולש הספקים (Power Triangle)", "VA/W/VAR"))
