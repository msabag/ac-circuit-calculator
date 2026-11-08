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

# אתחול רשימות רכיבים דינמיות ב-Session State
if 'resistors' not in st.session_state:
    st.session_state.resistors = [21.865]  # נגד ראשון כברירת מחדל

if 'capacitors' not in st.session_state:
    st.session_state.capacitors = [12.15]  # היגוי קיבולי ראשון (Xc)

# עיצוב מותאם אישית: כרטיסיות, הבלטת פירוט הרכיבים וחץ מונפש
st.markdown("""
    <style>
    /* עיצוב כרטיסיות התוצאות */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 12px !important;
        padding: 15px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.08) !important;
    }
    div[data-testid="stMetric"] label {
        color: #334155 !important;
        font-weight: bold !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-weight: bold !important;
    }
    
    /* הבלטת כפתור פתיחת ה-Sidebar */
    button[data-testid="baseButton-header"] {
        background-color: #0284c7 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        font-size: 20px !important;
    }

    /* תיבת הנחיה בולטת */
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

    /* עיצוב מוגדל ומאיר עיניים לבלוק פירוט הרכיבים */
    .component-details-box {
        background-color: #f8fafc;
        border-right: 6px solid #0284c7;
        border-radius: 12px;
        padding: 22px;
        margin-top: 15px;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .component-item {
        font-size: 17px;
        line-height: 1.9;
        color: #1e293b;
    }
    .component-item strong {
        color: #0369a1;
    }
    </style>
""", unsafe_allow_html=True)

# תיבת הנחיה בולטת בראש העמוד
st.markdown("""
    <div class="input-arrow-box">
        <span class="animated-arrow">👈</span>
        <span>לחץ על החץ בפינה / פתח את סרגל הצד כדי להוסיף רכיבים ולשנות נתונים</span>
    </div>
""", unsafe_allow_html=True)

# כותרת ראשית עם ברווז אמבטיה בשטריימל
col_title, col_duck = st.columns([4, 1])
with col_title:
    st.title("⚡ מחשבון מעגל AC טורי מרובה רכיבים")
    st.write("תוכל להוסיף כמה נגדים וקבלים שתרצה בלחיצה על כפתור +, ולקבל ניתוח מלא.")

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
    ("חישוב רגיל (לפי רכיבים דינמיים)", "חישוב הפוך (לפי V, I וזוויות)")
)

st.sidebar.subheader("📌 נתוני מקור ותדר (אופציונלי)")
V_rms = st.sidebar.number_input("מתח המקור V (וולט RMS):", min_value=0.1, value=50.0)

use_theta_v = st.sidebar.checkbox("הוסף זווית מופע למקור המתח (θv)", value=True)
theta_v = st.sidebar.number_input("זווית מופע θv (מעלות):", value=68.0) if use_theta_v else 0.0

use_frequency = st.sidebar.checkbox("הוסף תדר f (נדרש לחישוב C ב-µF)", value=True)
f = st.sidebar.number_input("תדר f (הרץ):", min_value=0.1, value=50.0) if use_frequency else None

if calc_mode == "חישוב רגיל (לפי רכיבים דינמיים)":
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔌 נגדים במעגל (R)")
    
    # ניהול נגדים דינמיים
    for i in range(len(st.session_state.resistors)):
        st.session_state.resistors[i] = st.sidebar.number_input(
            f"נגד R{i+1} (אוהם):", 
            min_value=0.0, 
            value=float(st.session_state.resistors[i]),
            key=f"res_{i}"
        )
    
    col_r_add, col_r_rem = st.sidebar.columns(2)
    if col_r_add.button("➕ הוסף נגד (R)", key="add_r"):
        st.session_state.resistors.append(10.0)
        st.rerun()
    if col_r_rem.button("➖ הסר נגד", key="rem_r") and len(st.session_state.resistors) > 1:
        st.session_state.resistors.pop()
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚡ קבלים במעגל (Xc / C)")
    
    # ניהול קבלים דינמיים
    for i in range(len(st.session_state.capacitors)):
        st.session_state.capacitors[i] = st.sidebar.number_input(
            f"היגוי קיבולי Xc{i+1} (אוהם):", 
            min_value=0.0, 
            value=float(st.session_state.capacitors[i]),
            key=f"cap_{i}"
        )
        
    col_c_add, col_c_rem = st.sidebar.columns(2)
    if col_c_add.button("➕ הוסף קבל (Xc)", key="add_c"):
        st.session_state.capacitors.append(10.0)
        st.rerun()
    if col_c_rem.button("➖ הסר קבל", key="rem_c") and len(st.session_state.capacitors) > 1:
        st.session_state.capacitors.pop()
        st.rerun()

    # חישוב שקולים בטור
    R_total = sum(st.session_state.resistors)
    Xc_total = sum(st.session_state.capacitors)
    
    Z = math.sqrt(R_total**2 + Xc_total**2)
    I_rms = V_rms / Z if Z > 0 else 0
    phi_deg_circuit = math.degrees(math.atan(Xc_total / R_total)) if R_total > 0 else 90.0
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
    R_total = Z * math.cos(phi_rad)
    Xc_total = Z * math.sin(phi_rad)

# --- חישוב C שקול ב-µF אם הוזן תדר ---
if use_frequency and Xc_total > 0:
    omega = 2 * math.pi * f
    C_total = 1 / (omega * Xc_total)
    uF_total = C_total * 1e6
else:
    uF_total = None

# --- חישובי זוויות ומתחים וקטוריים ---
VR_total = I_rms * R_total
VC_total = I_rms * Xc_total
theta_vr = theta_i
theta_vc = theta_i - 90.0
pf = math.cos(math.radians(phi_deg_circuit))

P = I_rms**2 * R_total
Q = I_rms**2 * Xc_total
S = V_rms * I_rms

# --- הצגת תוצאות ---
st.subheader("📊 תוצאות החישוב הכוללות")

col1, col2, col3 = st.columns(3)
col1.metric("עכבה כוללת (Z)", f"{Z:.2f} Ω")
col2.metric("זרם במעגל (I)", f"{I_rms:.2f} A")
col3.metric("גורם הספק (cos φ)", f"{pf:.3f}")

st.write("")

col4, col5, col6 = st.columns(3)
col4.metric("התנגדות שקולה (R_total)", f"{R_total:.3f} Ω")
col5.metric("היגוי קיבולי שקול (Xc_total)", f"{Xc_total:.2f} Ω")
if uF_total is not None:
    col6.metric("קיבול שקול (C_total)", f"{uF_total:.2f} µF")
else:
    col6.metric("קיבול שקול (C_total)", "לא הוגדר תדר")

st.markdown("---")

# --- פירוט רכיבים מורחב, מוגדל ומאיר עיניים ---
st.subheader("🔹 פירוט מורחב של רכיבי המעגל והמתחים")

resistors_detail = ""
if calc_mode == "חישוב רגיל (לפי רכיבים דינמיים)":
    for idx, r_val in enumerate(st.session_state.resistors):
        v_r_i = I_rms * r_val
        resistors_detail += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;• <strong>נגד R{idx+1}:</strong> {r_val:.2f} Ω (מפלי מתח: {v_r_i:.2f} V)"

capacitors_detail = ""
if calc_mode == "חישוב רגיל (לפי רכיבים דינמיים)":
    for idx, xc_val in enumerate(st.session_state.capacitors):
        v_c_i = I_rms * xc_val
        c_i_uf = (1 / (2 * math.pi * f * xc_val) * 1e6) if (use_frequency and xc_val > 0) else None
        c_i_str = f" | קיבול: {c_i_uf:.2f} µF" if c_i_uf else ""
        capacitors_detail += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;• <strong>קבל C{idx+1}:</strong> Xc = {xc_val:.2f} Ω {c_i_str} (מפלי מתח: {v_c_i:.2f} V)"

c_total_str = f"{uF_total:.2f} µF" if uF_total is not None else "לא מחושב (אין תדר)"

st.markdown(f"""
<div class="component-details-box">
    <div class="component-item">
        📌 <strong>התנגדות כוללת בטור ($R_{{total}}$):</strong> {R_total:.3f} Ω {resistors_detail}
    </div>
    <hr style="margin: 12px 0; border: 0; border-top: 1px solid #e2e8f0;">
    <div class="component-item">
        ⚡ <strong>היגוי קיבולי כולל בטור ($X_{{C,total}}$):</strong> {Xc_total:.2f} Ω {capacitors_detail}
    </div>
    <hr style="margin: 12px 0; border: 0; border-top: 1px solid #e2e8f0;">
    <div class="component-item">
        🔋 <strong>קיבול שקול מחושב ($C_{{total}}$):</strong> {c_total_str}
    </div>
    <hr style="margin: 12px 0; border: 0; border-top: 1px solid #e2e8f0;">
    <div class="component-item">
        📐 <strong>מתח מקור וקטורי ($V$):</strong> {V_rms:.2f} ∠ {theta_v:.2f}° V
    </div>
    <div class="component-item">
        🌊 <strong>זרם וקטורי במעגל ($I$):</strong> {I_rms:.2f} ∠ {theta_i:.2f}° A
    </div>
    <div class="component-item">
        🔄 <strong>הפרש מופע כולל ($\phi = \\theta_I - \\theta_V$):</strong> {phi_deg_circuit:.2f}° (הזרם מקדים את המתח)
    </div>
    <div class="component-item">
        🔴 <strong>מתח שקול על הנגדים ($V_{{R,total}}$):</strong> {VR_total:.2f} ∠ {theta_vr:.2f}° V
    </div>
    <div class="component-item">
        🔵 <strong>מתח שקול על הקבלים ($V_{{C,total}}$):</strong> {VC_total:.2f} ∠ {theta_vc:.2f}° V
    </div>
</div>
""", unsafe_allow_html=True)

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
st.subheader("📐 ייצוג ויזואלי של המשולשים השקולים")

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
st.pyplot(plot_triangle(R_total, Xc_total, "R_total", "Xc_total", "Z", "משולש עכבות (Impedance Triangle)", "Ω"))

st.write("#### 2. משולש מתחים")
st.pyplot(plot_triangle(VR_total, VC_total, "VR_total", "VC_total", "V", "משולש מתחים (Voltage Triangle)", "V"))

st.write("#### 3. משולש הספקים")
st.pyplot(plot_triangle(P, Q, "P", "Q", "S", "משולש הספקים (Power Triangle)", "VA/W/VAR"))
