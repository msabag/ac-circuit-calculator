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
    st.session_state.resistors = [{"val": 21.865, "unit": "Ω"}]

if 'capacitors' not in st.session_state:
    st.session_state.capacitors = [{"type": "C (קיבול)", "val": 262.0, "unit": "µF"}]

# עיצוב מותאם אישית לכרטיסיות נקיות וקומפקטיות
st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
    }
    div[data-testid="stMetric"] label {
        color: #334155 !important;
        font-weight: bold !important;
        font-size: 14px !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-weight: bold !important;
        font-size: 20px !important;
    }
    button[data-testid="baseButton-header"] {
        background-color: #0284c7 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        font-size: 20px !important;
    }
    .input-arrow-box {
        background: linear-gradient(135deg, #0284c7, #0369a1);
        color: white;
        padding: 12px 18px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(2, 132, 199, 0.25);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .animated-arrow {
        font-size: 20px;
        animation: pulse-arrow 1.2s infinite alternate;
    }
    @keyframes pulse-arrow {
        0% { transform: translateX(0px); }
        100% { transform: translateX(-8px); }
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="input-arrow-box">
        <span class="animated-arrow">👈</span>
        <span>לחץ על החץ בפינה / פתח את סרגל הצד כדי להוסיף רכיבים ולבחור יחידות (k, m, µ, n, p)</span>
    </div>
""", unsafe_allow_html=True)

col_title, col_duck = st.columns([4, 1])
with col_title:
    st.title("⚡ מחשבון מעגל AC טורי מרובה רכיבים")
    st.write("ניתוח חשמלי מלא, הספק לכל רכיב וכרטיסיות קומפקטיות.")

with col_duck:
    st.markdown("""
    <div style="text-align: center; font-size: 45px; line-height: 1;">
        🎩<br>🦆
    </div>
    <div style="text-align: center; font-weight: bold; color: #38bdf8; font-size: 12px; margin-top: 3px;">
        רב-ברווז בסיעתא דשמיא
    </div>
    """, unsafe_allow_html=True)

# --- תפריט קלט בצד (סיידבר) ---
st.sidebar.header("⚙️ מצב חישוב ופרמטרים")

calc_mode = st.sidebar.radio(
    "בחר מצב חישוב:",
    ("חישוב רגיל (לפי רכיבים דינמיים)", "חישוב הפוך (לפי V, I וזוויות)")
)

st.sidebar.subheader("📌 נתוני מקור ותדר")
V_rms = st.sidebar.number_input("מתח המקור V (וולט RMS):", min_value=0.1, value=50.0)

use_theta_v = st.sidebar.checkbox("הוסף זווית מופע למקור המתח (θv)", value=True)
theta_v = st.sidebar.number_input("זווית מופע θv (מעלות):", value=68.0) if use_theta_v else 0.0

use_frequency = st.sidebar.checkbox("הוסף תדר f (נדרש להמרת C ל-Xc)", value=True)
f = st.sidebar.number_input("תדר f (הרץ):", min_value=0.1, value=50.0) if use_frequency else None

# מקדמי המרה ליחידות
R_MULTIPLIERS = {"Ω": 1.0, "kΩ": 1e3, "MΩ": 1e6, "mΩ": 1e-3}
C_MULTIPLIERS = {"F": 1.0, "mF": 1e-3, "µF": 1e-6, "nF": 1e-9, "pF": 1e-12}
XC_MULTIPLIERS = {"Ω": 1.0, "kΩ": 1e3, "mΩ": 1e-3}

R_total = 0.0
Xc_total = 0.0
r_details_list = []
c_details_list = []

if calc_mode == "חישוב רגיל (לפי רכיבים דינמיים)":
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔌 נגדים במעגל (R)")
    
    for i in range(len(st.session_state.resistors)):
        col_r_val, col_r_unit = st.sidebar.columns([2, 1])
        r_val = col_r_val.number_input(f"נגד R{i+1}:", min_value=0.0, value=float(st.session_state.resistors[i]["val"]), key=f"r_val_{i}")
        r_unit = col_r_unit.selectbox("יחידה:", ["Ω", "kΩ", "MΩ", "mΩ"], index=["Ω", "kΩ", "MΩ", "mΩ"].index(st.session_state.resistors[i]["unit"]), key=f"r_unit_{i}")
        
        st.session_state.resistors[i] = {"val": r_val, "unit": r_unit}
        r_ohms = r_val * R_MULTIPLIERS[r_unit]
        R_total += r_ohms
        r_details_list.append((i+1, r_val, r_unit, r_ohms))
        
    col_r_add, col_r_rem = st.sidebar.columns(2)
    if col_r_add.button("➕ הוסף נגד", key="add_r"):
        st.session_state.resistors.append({"val": 10.0, "unit": "Ω"})
        st.rerun()
    if col_r_rem.button("➖ הסר נגד", key="rem_r") and len(st.session_state.resistors) > 1:
        st.session_state.resistors.pop()
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚡ קבלים במעגל (C / Xc)")
    
    for i in range(len(st.session_state.capacitors)):
        c_type = st.sidebar.radio(f"סוג קבל C{i+1}:", ["C (קיבול)", "Xc (היגוי)"], key=f"c_type_{i}")
        col_c_val, col_c_unit = st.sidebar.columns([2, 1])
        
        if c_type == "C (קיבול)":
            c_val = col_c_val.number_input(f"ערך C{i+1}:", min_value=0.01, value=float(st.session_state.capacitors[i]["val"]), key=f"c_val_{i}")
            c_unit = col_c_unit.selectbox("יחידה:", ["µF", "nF", "pF", "mF", "F"], key=f"c_unit_{i}")
            
            c_farads = c_val * C_MULTIPLIERS[c_unit]
            if use_frequency and f:
                xc_ohms = 1 / (2 * math.pi * f * c_farads)
            else:
                xc_ohms = 0.0
                st.sidebar.warning("נדרש תדר f כדי לחשב היגוי Xc מתוך קיבול C")
            c_details_list.append((i+1, "C", c_val, c_unit, xc_ohms, c_farads * 1e6))
        else:
            c_val = col_c_val.number_input(f"ערך Xc{i+1}:", min_value=0.0, value=float(st.session_state.capacitors[i]["val"]), key=f"c_val_{i}")
            c_unit = col_c_unit.selectbox("יחידה:", ["Ω", "kΩ", "mΩ"], key=f"c_unit_{i}")
            
            xc_ohms = c_val * XC_MULTIPLIERS[c_unit]
            c_uf_calc = (1 / (2 * math.pi * f * xc_ohms) * 1e6) if (use_frequency and f and xc_ohms > 0) else None
            c_details_list.append((i+1, "Xc", c_val, c_unit, xc_ohms, c_uf_calc))
            
        st.session_state.capacitors[i] = {"type": c_type, "val": c_val, "unit": c_unit}
        Xc_total += xc_ohms

    col_c_add, col_c_rem = st.sidebar.columns(2)
    if col_c_add.button("➕ הוסף קבל", key="add_c"):
        st.session_state.capacitors.append({"type": "C (קיבול)", "val": 10.0, "unit": "µF"})
        st.rerun()
    if col_c_rem.button("➖ הסר קבל", key="rem_c") and len(st.session_state.capacitors) > 1:
        st.session_state.capacitors.pop()
        st.rerun()

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

# חישוב C שקול
if use_frequency and f and Xc_total > 0:
    C_total = 1 / (2 * math.pi * f * Xc_total)
    uF_total = C_total * 1e6
else:
    uF_total = None

# חישוב מתחים והספקים
VR_total = I_rms * R_total
VC_total = I_rms * Xc_total
theta_vr = theta_i
theta_vc = theta_i - 90.0
pf = math.cos(math.radians(phi_deg_circuit))

P = I_rms**2 * R_total
Q = I_rms**2 * Xc_total
S = V_rms * I_rms

# --- הצגת תוצאות כוללות ---
st.subheader("📊 תוצאות החישוב הכוללות")

c1, c2, c3 = st.columns(3)
c1.metric("עכבה כוללת (Z)", f"{Z:.2f} Ω")
c2.metric("זרם במעגל (I)", f"{I_rms:.2f} A")
c3.metric("גורם הספק (cos φ)", f"{pf:.3f}")

st.write("")

c4, c5, c6 = st.columns(3)
c4.metric("התנגדות שקולה (R)", f"{R_total:.3f} Ω")
c5.metric("היגוי קיבולי שקול (Xc)", f"{Xc_total:.2f} Ω")
if uF_total is not None:
    c6.metric("קיבול שקול (C)", f"{uF_total:.2f} µF")
else:
    c6.metric("קיבול שקול (C)", "ללא תדר")

st.write("")

c7, c8, c9 = st.columns(3)
c7.metric("הספק אקטיבי כולל (P)", f"{P:.2f} W")
c8.metric("הספק ריאקטיבי כולל (Q)", f"{Q:.2f} VAR")
c9.metric("הספק מדומה כולל (S)", f"{S:.2f} VA")

st.markdown("---")

# --- פירוט רכיבים בכרטיסיות (Metrics) קומפקטיות ---
st.subheader("🔹 פירוט רכיבים, מתחים והספקים")

# 1. פירוט נגדים (אם קיימים)
if calc_mode == "חישוב רגיל (לפי רכיבים דינמיים)" and r_details_list:
    st.write("#### 🔴 נגדים במעגל")
    for idx, val, unit, ohms in r_details_list:
        v_r_i = I_rms * ohms
        p_r_i = (I_rms ** 2) * ohms
        rc1, rc2, rc3, rc4 = st.columns(4)
        rc1.metric(f"נגד R{idx}", f"{val} {unit}")
        rc2.metric(f"התנגדות (Ω)", f"{ohms:.2f} Ω")
        rc3.metric(f"מפל מתח (VR{idx})", f"{v_r_i:.2f} V")
        rc4.metric(f"הספק (P{idx})", f"{p_r_i:.2f} W")
        st.write("")

# 2. פירוט קבלים (אם קיימים)
if calc_mode == "חישוב רגיל (לפי רכיבים דינמיים)" and c_details_list:
    st.write("#### 🔵 קבלים במעגל")
    for idx, ctype, val, unit, xc_val, c_uf in c_details_list:
        v_c_i = I_rms * xc_val
        q_c_i = (I_rms ** 2) * xc_val
        c_str = f"{c_uf:.2f} µF" if c_uf is not None else "ללא תדר"
        cc1, cc2, cc3, cc4 = st.columns(4)
        cc1.metric(f"קבל C{idx}", f"{val} {unit}")
        cc2.metric(f"היגוי (Xc{idx})", f"{xc_val:.2f} Ω")
        cc3.metric(f"מפל מתח (VC{idx})", f"{v_c_i:.2f} V")
        cc4.metric(f"הספק ריאקטיבי (Q{idx})", f"{q_c_i:.2f} VAR")
        st.write("")

# 3. פירוט זוויות ווקטורים כרטיסיות
st.write("#### 📐 זוויות ופאזורים במעגל")
ac1, ac2, ac3 = st.columns(3)
ac1.metric("מתח מקור וקטורי (V)", f"{V_rms:.2f} ∠ {theta_v:.1f}° V")
ac2.metric("זרם וקטורי (I)", f"{I_rms:.2f} ∠ {theta_i:.1f}° A")
ac3.metric("הפרש מופע (φ)", f"{phi_deg_circuit:.2f}°")

ac4, ac5, ac6 = st.columns(3)
ac4.metric("מתח שקול נגדים (VR)", f"{VR_total:.2f} ∠ {theta_vr:.1f}° V")
ac5.metric("מתח שקול קבלים (VC)", f"{VC_total:.2f} ∠ {theta_vc:.1f}° V")
ac6.metric("מקדם הספק", f"{pf:.3f}")

st.markdown("---")

# --- חלק ויזואלי 1: גרפי סינוס בזמן ---
st.subheader("🌊 גרפי סינוס של מתח וזרם בזמן t")

V_peak = V_rms * math.sqrt(2)
I_peak = I_rms * math.sqrt(2)

f_draw = f if (use_frequency and f) else 50.0
T = 1 / f_draw
t = np.linspace(0, 2 * T, 1000)

omega_draw = 2 * np.pi * f_draw
v_t = V_peak * np.sin(omega_draw * t + math.radians(theta_v))
i_t = I_peak * np.sin(omega_draw * t + math.radians(theta_i))

fig_sine, ax_v = plt.subplots(figsize=(8, 4.2))

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
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.quiver(0, 0, x, 0, angles='xy', scale_units='xy', scale=1, color='#2563eb', label=f'{x_label} = {x:.2f} {unit}')
    ax.quiver(x, 0, 0, -y, angles='xy', scale_units='xy', scale=1, color='#dc2626', label=f'{y_label} = {y:.2f} {unit}')
    ax.quiver(0, 0, x, -y, angles='xy', scale_units='xy', scale=1, color='#16a34a', label=f'{hypotenuse_label} = {math.sqrt(x**2 + y**2):.2f} {unit}')
    
    x_min = min(0, x) * 1.25 if x < 0 else -abs(x)*0.1
    x_max = max(0, x) * 1.25 if x > 0 else abs(x)*0.1
    y_min = -abs(y)*1.25
    y_max = abs(y)*0.2
    
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_title(title, fontsize=13, fontweight='bold', pad=10)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='lower left', fontsize=10)
    plt.tight_layout()
    return fig

st.write("#### 1. משולש עכבות")
st.pyplot(plot_triangle(R_total, Xc_total, "R_total", "Xc_total", "Z", "משולש עכבות (Impedance Triangle)", "Ω"))

st.write("#### 2. משולש מתחים")
st.pyplot(plot_triangle(VR_total, VC_total, "VR_total", "VC_total", "V", "משולש מתחים (Voltage Triangle)", "V"))

st.write("#### 3. משולש הספקים")
st.pyplot(plot_triangle(P, Q, "P", "Q", "S", "משולש הספקים (Power Triangle)", "VA/W/VAR"))
