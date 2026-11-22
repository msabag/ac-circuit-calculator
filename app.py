import base64
import json
import math
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# הגדרת תצורת עמוד
st.set_page_config(
    page_title="מחשבון AC טורי RLC",
    page_icon="🦆",
    layout="wide"
)

# --- מנגנון שמירה וטעינה מכתובת ה-URL (לכל משתמש בנפרד) ---
DEFAULT_STATE = {
    "calc_mode": "חישוב רגיל (לפי רכיבים דינמיים)",
    "V_rms": 50.0,
    "use_theta_v": True,
    "theta_v": 68.0,
    "use_frequency": True,
    "f": 50.0,
    "resistors": [{"val": 21.865, "unit": "Ω"}],
    "inductors": [],
    "capacitors": [{"type": "C (קיבול)", "val": 262.0, "unit": "µF"}],
    "I_rms": 2.0,
    "angle_input_mode": "זווית זרם ישירה (θi)",
    "theta_i": 97.0,
    "phi_deg_input": 29.0,
}

def load_state_from_url():
    if "state" in st.query_params:
        try:
            encoded = st.query_params["state"]
            decoded_json = base64.urlsafe_b64decode(encoded.encode("utf-8")).decode("utf-8")
            loaded = json.loads(decoded_json)
            merged = DEFAULT_STATE.copy()
            merged.update(loaded)
            return merged
        except Exception:
            return DEFAULT_STATE.copy()
    return DEFAULT_STATE.copy()

def save_state_to_url(state_dict):
    try:
        json_str = json.dumps(state_dict, ensure_ascii=False)
        encoded = base64.urlsafe_b64encode(json_str.encode("utf-8")).decode("utf-8")
        if st.query_params.get("state") != encoded:
            st.query_params["state"] = encoded
    except Exception:
        pass

# טעינה ראשונית ל-Session State
if "initialized" not in st.session_state:
    saved = load_state_from_url()
    for k, v in saved.items():
        st.session_state[k] = v
    st.session_state.initialized = True

# עיצוב מותאם אישית
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
        <span>לחץ על החץ בפינה להזנת נתונים • הנתונים נשמרים אוטומטית בכתובת האתר עבורך</span>
    </div>
""", unsafe_allow_html=True)

col_title, col_duck = st.columns([4, 1])
with col_title:
    st.title("⚡ מחשבון מעגל AC טורי מרובה רכיבים (R-L-C)")
    st.write("ניתוח חשמלי מלא בדיוק של 3 ספרות אחרי הנקודה, הספק לכל רכיב וייצוג ויזואלי.")

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

if st.sidebar.button("🔄 איפוס נתונים לברירת מחדל"):
    st.query_params.clear()
    for k, v in DEFAULT_STATE.items():
        st.session_state[k] = json.loads(json.dumps(v))
    st.rerun()

mode_options = ("חישוב רגיל (לפי רכיבים דינמיים)", "חישוב הפוך (לפי V, I וזוויות)")
mode_idx = mode_options.index(st.session_state.calc_mode) if st.session_state.calc_mode in mode_options else 0
calc_mode = st.sidebar.radio("בחר מצב חישוב:", mode_options, index=mode_idx)
st.session_state.calc_mode = calc_mode

st.sidebar.subheader("📌 נתוני מקור ותדר")
V_rms = st.sidebar.number_input("מתח המקור V (וולט RMS):", min_value=0.001, value=float(st.session_state.V_rms), format="%.3f")
st.session_state.V_rms = V_rms

use_theta_v = st.sidebar.checkbox("הוסף זווית מופע למקור המתח (θv)", value=bool(st.session_state.use_theta_v))
st.session_state.use_theta_v = use_theta_v
if use_theta_v:
    theta_v = st.sidebar.number_input("זווית מופע θv (מעלות):", value=float(st.session_state.theta_v), format="%.3f")
    st.session_state.theta_v = theta_v
else:
    theta_v = 0.0

use_frequency = st.sidebar.checkbox("הוסף תדר f (נדרש להמרת L ו-C)", value=bool(st.session_state.use_frequency))
st.session_state.use_frequency = use_frequency
if use_frequency:
    f = st.sidebar.number_input("תדר f (הרץ):", min_value=0.001, value=float(st.session_state.f), format="%.3f")
    st.session_state.f = f
else:
    f = None

# מקדמי המרה ליחידות
R_MULTIPLIERS = {"Ω": 1.0, "kΩ": 1e3, "MΩ": 1e6, "mΩ": 1e-3}
L_MULTIPLIERS = {"H": 1.0, "mH": 1e-3, "µH": 1e-6, "nH": 1e-9}
C_MULTIPLIERS = {"F": 1.0, "mF": 1e-3, "µF": 1e-6, "nF": 1e-9, "pF": 1e-12}
X_MULTIPLIERS = {"Ω": 1.0, "kΩ": 1e3, "mΩ": 1e-3}

R_total = 0.0
XL_total = 0.0
Xc_total = 0.0
r_details_list = []
l_details_list = []
c_details_list = []

if calc_mode == "חישוב רגיל (לפי רכיבים דינמיים)":
    # --- 1. ניהול נגדים ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔌 נגדים במעגל (R)")
    
    for i in range(len(st.session_state.resistors)):
        col_r_val, col_r_unit = st.sidebar.columns([2, 1])
        r_val = col_r_val.number_input(f"נגד R{i+1}:", min_value=0.0, value=float(st.session_state.resistors[i]["val"]), format="%.3f", key=f"r_val_{i}")
        r_units = ["Ω", "kΩ", "MΩ", "mΩ"]
        curr_r_u = st.session_state.resistors[i]["unit"] if st.session_state.resistors[i]["unit"] in r_units else "Ω"
        r_unit = col_r_unit.selectbox("יחידה:", r_units, index=r_units.index(curr_r_u), key=f"r_unit_{i}")
        
        st.session_state.resistors[i] = {"val": r_val, "unit": r_unit}
        r_ohms = r_val * R_MULTIPLIERS[r_unit]
        R_total += r_ohms
        r_details_list.append((i+1, r_val, r_unit, r_ohms))
        
    col_r_add, col_r_rem = st.sidebar.columns(2)
    if col_r_add.button("➕ הוסף נגד", key="add_r"):
        st.session_state.resistors.append({"val": 10.0, "unit": "Ω"})
        save_state_to_url({k: st.session_state[k] for k in DEFAULT_STATE})
        st.rerun()
    if col_r_rem.button("➖ הסר נגד", key="rem_r") and len(st.session_state.resistors) > 0:
        st.session_state.resistors.pop()
        save_state_to_url({k: st.session_state[k] for k in DEFAULT_STATE})
        st.rerun()

    # --- 2. ניהול סלילים ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🧲 סלילים במעגל (L / XL)")
    
    for i in range(len(st.session_state.inductors)):
        l_types = ["L (השראות)", "XL (היגוי)"]
        curr_l_t = st.session_state.inductors[i]["type"] if st.session_state.inductors[i]["type"] in l_types else "L (השראות)"
        l_type = st.sidebar.radio(f"סוג סליל L{i+1}:", l_types, index=l_types.index(curr_l_t), key=f"l_type_{i}")
        col_l_val, col_l_unit = st.sidebar.columns([2, 1])
        
        if l_type == "L (השראות)":
            l_units_list = ["mH", "µH", "H", "nH"]
            curr_unit = st.session_state.inductors[i]["unit"] if st.session_state.inductors[i]["unit"] in l_units_list else "mH"
            l_val = col_l_val.number_input(f"ערך L{i+1}:", min_value=0.0, value=float(st.session_state.inductors[i]["val"]), format="%.3f", key=f"l_val_{i}")
            l_unit = col_l_unit.selectbox("יחידה:", l_units_list, index=l_units_list.index(curr_unit), key=f"l_unit_{i}")
            
            l_henrys = l_val * L_MULTIPLIERS[l_unit]
            if use_frequency and f:
                xl_ohms = 2 * math.pi * f * l_henrys
            else:
                xl_ohms = 0.0
                st.sidebar.warning("נדרש תדר f כדי לחשב היגוי XL מתוך השראות L")
            l_details_list.append((i+1, "L", l_val, l_unit, xl_ohms, l_henrys * 1e3))
        else:
            xl_units_list = ["Ω", "kΩ", "mΩ"]
            curr_unit = st.session_state.inductors[i]["unit"] if st.session_state.inductors[i]["unit"] in xl_units_list else "Ω"
            l_val = col_l_val.number_input(f"ערך XL{i+1}:", min_value=0.0, value=float(st.session_state.inductors[i]["val"]), format="%.3f", key=f"l_val_{i}")
            l_unit = col_l_unit.selectbox("יחידה:", xl_units_list, index=xl_units_list.index(curr_unit), key=f"l_unit_{i}")
            
            xl_ohms = l_val * X_MULTIPLIERS[l_unit]
            l_mh_calc = (xl_ohms / (2 * math.pi * f) * 1e3) if (use_frequency and f and xl_ohms > 0) else None
            l_details_list.append((i+1, "XL", l_val, l_unit, xl_ohms, l_mh_calc))
            
        st.session_state.inductors[i] = {"type": l_type, "val": l_val, "unit": l_unit}
        XL_total += xl_ohms

    col_l_add, col_l_rem = st.sidebar.columns(2)
    if col_l_add.button("➕ הוסף סליל", key="add_l"):
        st.session_state.inductors.append({"type": "L (השראות)", "val": 50.0, "unit": "mH"})
        save_state_to_url({k: st.session_state[k] for k in DEFAULT_STATE})
        st.rerun()
    if col_l_rem.button("➖ הסר סליל", key="rem_l") and len(st.session_state.inductors) > 0:
        st.session_state.inductors.pop()
        save_state_to_url({k: st.session_state[k] for k in DEFAULT_STATE})
        st.rerun()

    # --- 3. ניהול קבלים ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚡ קבלים במעגל (C / Xc)")
    
    for i in range(len(st.session_state.capacitors)):
        c_types = ["C (קיבול)", "Xc (היגוי)"]
        curr_c_t = st.session_state.capacitors[i]["type"] if st.session_state.capacitors[i]["type"] in c_types else "C (קיבול)"
        c_type = st.sidebar.radio(f"סוג קבל C{i+1}:", c_types, index=c_types.index(curr_c_t), key=f"c_type_{i}")
        col_c_val, col_c_unit = st.sidebar.columns([2, 1])
        
        if c_type == "C (קיבול)":
            c_units_list = ["µF", "nF", "pF", "mF", "F"]
            curr_unit = st.session_state.capacitors[i]["unit"] if st.session_state.capacitors[i]["unit"] in c_units_list else "µF"
            c_val = col_c_val.number_input(f"ערך C{i+1}:", min_value=0.001, value=float(st.session_state.capacitors[i]["val"]), format="%.3f", key=f"c_val_{i}")
            c_unit = col_c_unit.selectbox("יחידה:", c_units_list, index=c_units_list.index(curr_unit), key=f"c_unit_{i}")
            
            c_farads = c_val * C_MULTIPLIERS[c_unit]
            if use_frequency and f:
                xc_ohms = 1 / (2 * math.pi * f * c_farads)
            else:
                xc_ohms = 0.0
                st.sidebar.warning("נדרש תדר f כדי לחשב היגוי Xc מתוך קיבול C")
            c_details_list.append((i+1, "C", c_val, c_unit, xc_ohms, c_farads * 1e6))
        else:
            xc_units_list = ["Ω", "kΩ", "mΩ"]
            curr_unit = st.session_state.capacitors[i]["unit"] if st.session_state.capacitors[i]["unit"] in xc_units_list else "Ω"
            c_val = col_c_val.number_input(f"ערך Xc{i+1}:", min_value=0.0, value=float(st.session_state.capacitors[i]["val"]), format="%.3f", key=f"c_val_{i}")
            c_unit = col_c_unit.selectbox("יחידה:", xc_units_list, index=xc_units_list.index(curr_unit), key=f"c_unit_{i}")
            
            xc_ohms = c_val * X_MULTIPLIERS[c_unit]
            c_uf_calc = (1 / (2 * math.pi * f * xc_ohms) * 1e6) if (use_frequency and f and xc_ohms > 0) else None
            c_details_list.append((i+1, "Xc", c_val, c_unit, xc_ohms, c_uf_calc))
            
        st.session_state.capacitors[i] = {"type": c_type, "val": c_val, "unit": c_unit}
        Xc_total += xc_ohms

    col_c_add, col_c_rem = st.sidebar.columns(2)
    if col_c_add.button("➕ הוסף קבל", key="add_c"):
        st.session_state.capacitors.append({"type": "C (קיבול)", "val": 10.0, "unit": "µF"})
        save_state_to_url({k: st.session_state[k] for k in DEFAULT_STATE})
        st.rerun()
    if col_c_rem.button("➖ הסר קבל", key="rem_c") and len(st.session_state.capacitors) > 0:
        st.session_state.capacitors.pop()
        save_state_to_url({k: st.session_state[k] for k in DEFAULT_STATE})
        st.rerun()

    # חישובי עכבה וזוויות למעגל RLC
    X_net = XL_total - Xc_total
    Z = math.sqrt(R_total**2 + X_net**2)
    I_rms = V_rms / Z if Z > 0 else 0
    
    theta_z_deg = math.degrees(math.atan2(X_net, R_total)) if (R_total > 0 or X_net != 0) else 0.0
    theta_i = theta_v - theta_z_deg
    phi_deg_circuit = theta_i - theta_v

else:
    # --- מצב חישוב הפוך ---
    st.sidebar.subheader("🔄 נתוני זרם וזוויות")
    I_rms = st.sidebar.number_input("זרם המעגל I (אמפר RMS):", min_value=0.001, value=float(st.session_state.I_rms), format="%.3f")
    st.session_state.I_rms = I_rms
    
    angle_modes = ("זווית זרם ישירה (θi)", "הפרש מופע ישיר (φ = θi - θv)")
    a_idx = angle_modes.index(st.session_state.angle_input_mode) if st.session_state.angle_input_mode in angle_modes else 0
    angle_input_mode = st.sidebar.radio("איך תרצה להזין זוויות?", angle_modes, index=a_idx)
    st.session_state.angle_input_mode = angle_input_mode
    
    if angle_input_mode == "זווית זרם ישירה (θi)":
        theta_i = st.sidebar.number_input("זווית מופע של הזרם θi (במעלות):", value=float(st.session_state.theta_i), format="%.3f")
        st.session_state.theta_i = theta_i
        phi_deg_circuit = theta_i - theta_v
    else:
        phi_deg_circuit = st.sidebar.number_input("הפרש מופע φ (במעלות, + מקדים / - מפגר):", value=float(st.session_state.phi_deg_input), format="%.3f")
        st.session_state.phi_deg_input = phi_deg_circuit
        theta_i = theta_v + phi_deg_circuit
    
    theta_z_deg = -phi_deg_circuit
    theta_z_rad = math.radians(theta_z_deg)
    
    Z = V_rms / I_rms if I_rms > 0 else 0
    R_total = Z * math.cos(theta_z_rad)
    X_net = Z * math.sin(theta_z_rad)
    
    if X_net >= 0:
        XL_total = X_net
        Xc_total = 0.0
    else:
        XL_total = 0.0
        Xc_total = abs(X_net)

# שמירה אוטומטית של המצב העדכני ל-URL
save_state_to_url({k: st.session_state[k] for k in DEFAULT_STATE})

# זיהוי אופי המעגל
if abs(X_net) < 1e-6:
    circuit_nature = "התנגדותי טהור / תהודה (Resonance)"
elif X_net > 0:
    circuit_nature = "השראי (Inductive - זרם מפגר)"
else:
    circuit_nature = "קיבולי (Capacitive - זרם מקדים)"

# חישוב L ו-C שקולים
mH_total = (XL_total / (2 * math.pi * f) * 1e3) if (use_frequency and f and XL_total > 0) else None
uF_total = (1 / (2 * math.pi * f * Xc_total) * 1e6) if (use_frequency and f and Xc_total > 0) else None

# חישוב מתחים והספקים
VR_total = I_rms * R_total
VL_total = I_rms * XL_total
VC_total = I_rms * Xc_total
VX_net = I_rms * X_net

theta_vr = theta_i
theta_vl = theta_i + 90.0
theta_vc = theta_i - 90.0
pf = math.cos(math.radians(phi_deg_circuit))

P = I_rms**2 * R_total
Q_net = I_rms**2 * X_net
S = V_rms * I_rms

# --- הצגת תוצאות כוללות (בדיוק של 3 ספרות אחרי הנקודה) ---
st.subheader("📊 תוצאות החישוב הכוללות")
st.info(f"**אופי המעגל:** {circuit_nature}")

c1, c2, c3 = st.columns(3)
c1.metric("עכבה כוללת (Z)", f"{Z:.3f} Ω")
c2.metric("זרם במעגל (I)", f"{I_rms:.3f} A")
c3.metric("גורם הספק (cos φ)", f"{pf:.3f}")

st.write("")

c4, c5, c6 = st.columns(3)
c4.metric("התנגדות שקולה (R)", f"{R_total:.3f} Ω")
c5.metric("היגוי השראי שקול (XL)", f"{XL_total:.3f} Ω")
c6.metric("היגוי קיבולי שקול (Xc)", f"{Xc_total:.3f} Ω")

st.write("")

c7, c8, c9 = st.columns(3)
c7.metric("הספק אקטיבי כולל (P)", f"{P:.3f} W")
c8.metric("הספק ריאקטיבי נטו (Q)", f"{Q_net:.3f} VAR")
c9.metric("הספק מדומה כולל (S)", f"{S:.3f} VA")

if mH_total is not None or uF_total is not None:
    st.write("")
    ce1, ce2, ce3 = st.columns(3)
    ce1.metric("השראות שקולה (L)", f"{mH_total:.3f} mH" if mH_total is not None else "—")
    ce2.metric("קיבול שקול (C)", f"{uF_total:.3f} µF" if uF_total is not None else "—")
    ce3.metric("היגוי שקול נטו (XL - Xc)", f"{X_net:.3f} Ω")

st.markdown("---")

# --- פירוט רכיבים בכרטיסיות קומפקטיות (בדיוק של 3 ספרות אחרי הנקודה) ---
st.subheader("🔹 פירוט רכיבים, מתחים והספקים")

if calc_mode == "חישוב רגיל (לפי רכיבים דינמיים)" and r_details_list:
    st.write("#### 🔴 נגדים במעגל")
    for idx, val, unit, ohms in r_details_list:
        v_r_i = I_rms * ohms
        p_r_i = (I_rms ** 2) * ohms
        rc1, rc2, rc3, rc4 = st.columns(4)
        rc1.metric(f"נגד R{idx}", f"{val:.3f} {unit}")
        rc2.metric("התנגדות (Ω)", f"{ohms:.3f} Ω")
        rc3.metric(f"מפל מתח (VR{idx})", f"{v_r_i:.3f} V")
        rc4.metric(f"הספק (P{idx})", f"{p_r_i:.3f} W")
        st.write("")

if calc_mode == "חישוב רגיל (לפי רכיבים דינמיים)" and l_details_list:
    st.write("#### 🟠 סלילים במעגל")
    for idx, ltype, val, unit, xl_val, l_mh in l_details_list:
        v_l_i = I_rms * xl_val
        q_l_i = (I_rms ** 2) * xl_val
        lc1, lc2, lc3, lc4 = st.columns(4)
        lc1.metric(f"סליל L{idx}", f"{val:.3f} {unit}")
        lc2.metric(f"היגוי (XL{idx})", f"{xl_val:.3f} Ω")
        lc3.metric(f"מפל מתח (VL{idx})", f"{v_l_i:.3f} V")
        lc4.metric(f"הספק השראי (QL{idx})", f"{q_l_i:.3f} VAR")
        st.write("")

if calc_mode == "חישוב רגיל (לפי רכיבים דינמיים)" and c_details_list:
    st.write("#### 🔵 קבלים במעגל")
    for idx, ctype, val, unit, xc_val, c_uf in c_details_list:
        v_c_i = I_rms * xc_val
        q_c_i = (I_rms ** 2) * xc_val
        cc1, cc2, cc3, cc4 = st.columns(4)
        cc1.metric(f"קבל C{idx}", f"{val:.3f} {unit}")
        cc2.metric(f"היגוי (Xc{idx})", f"{xc_val:.3f} Ω")
        cc3.metric(f"מפל מתח (VC{idx})", f"{v_c_i:.3f} V")
        cc4.metric(f"הספק קיבולי (QC{idx})", f"{q_c_i:.3f} VAR")
        st.write("")

st.write("#### 📐 זוויות ופאזורים במעגל")
ac1, ac2, ac3 = st.columns(3)
ac1.metric("מתח מקור וקטורי (V)", f"{V_rms:.3f} ∠ {theta_v:.3f}° V")
ac2.metric("זרם וקטורי (I)", f"{I_rms:.3f} ∠ {theta_i:.3f}° A")
ac3.metric("הפרש מופע (φ = θi - θv)", f"{phi_deg_circuit:.3f}°")

st.write("")

ac4, ac5, ac6 = st.columns(3)
ac4.metric("מתח שקול נגדים (VR)", f"{VR_total:.3f} ∠ {theta_vr:.3f}° V")
ac5.metric("מתח שקול סלילים (VL)", f"{VL_total:.3f} ∠ {theta_vl:.3f}° V")
ac6.metric("מתח שקול קבלים (VC)", f"{VC_total:.3f} ∠ {theta_vc:.3f}° V")

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

ax_v.set_xlabel('זמן t (מילי-שניות)', fontsize=11)
ax_v.set_ylabel('מתח v(t) [V]', color=color_v, fontsize=11, fontweight='bold')
line1 = ax_v.plot(t * 1000, v_t, color=color_v, linewidth=2, label=f'v(t) [Vm={V_peak:.3f}V, θv={theta_v:.2f}°]')
ax_v.tick_params(axis='y', labelcolor=color_v)
ax_v.grid(True, linestyle='--', alpha=0.5)

ax_i = ax_v.twinx()
ax_i.set_ylabel('זרם i(t) [A]', color=color_i, fontsize=11, fontweight='bold')
line2 = ax_i.plot(t * 1000, i_t, color=color_i, linewidth=2, linestyle='--', label=f'i(t) [Im={I_peak:.3f}A, θi={theta_i:.2f}°]')
ax_i.tick_params(axis='y', labelcolor=color_i)

lines = line1 + line2
labels = [l.get_label() for l in lines]
ax_v.legend(lines, labels, loc='upper right', fontsize=10)

plt.title(f"אותות סינוס בזמן (הפרש מופע φ = {phi_deg_circuit:.3f}°)", fontsize=13, fontweight='bold', pad=10)
plt.tight_layout()
st.pyplot(fig_sine)

st.markdown("---")

# --- חלק ויזואלי 2: משולשים ---
st.subheader("📐 ייצוג ויזואלי של המשולשים השקולים")

def plot_triangle(x, y_net, x_label, y_label, hypotenuse_label, title, unit):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.quiver(0, 0, x, 0, angles='xy', scale_units='xy', scale=1, color='#2563eb', label=f'{x_label} = {x:.3f} {unit}')
    ax.quiver(x, 0, 0, y_net, angles='xy', scale_units='xy', scale=1, color='#dc2626', label=f'{y_label} = {y_net:.3f} {unit}')
    ax.quiver(0, 0, x, y_net, angles='xy', scale_units='xy', scale=1, color='#16a34a', label=f'{hypotenuse_label} = {math.sqrt(x**2 + y_net**2):.3f} {unit}')
    
    x_min = min(0, x) * 1.25 if x < 0 else -max(abs(x), 1)*0.1
    x_max = max(0, x) * 1.25 if x > 0 else max(abs(x), 1)*0.1
    
    y_abs = max(abs(y_net), 1)
    if y_net >= 0:
        y_min = -y_abs * 0.2
        y_max = y_abs * 1.25
        legend_loc = 'upper left'
    else:
        y_min = -y_abs * 1.25
        y_max = y_abs * 0.2
        legend_loc = 'lower left'
        
    ax.axhline(0, color='black', linewidth=0.8)
    ax.axvline(0, color='black', linewidth=0.8)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_title(title, fontsize=13, fontweight='bold', pad=10)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc=legend_loc, fontsize=10)
    plt.tight_layout()
    return fig

st.write("#### 1. משולש עכבות (R, X_net, Z)")
st.pyplot(plot_triangle(R_total, X_net, "R_total", "X_net (XL-Xc)", "Z", "משולש עכבות (Impedance Triangle)", "Ω"))

st.write("#### 2. משולש מתחים (VR, VL-VC, V)")
st.pyplot(plot_triangle(VR_total, VX_net, "VR_total", "VX_net (VL-VC)", "V", "משולש מתחים (Voltage Triangle)", "V"))

st.write("#### 3. משולש הספקים (P, Q_net, S)")
st.pyplot(plot_triangle(P, Q_net, "P", "Q_net (QL-QC)", "S", "משולש הספקים (Power Triangle)", "VA/W/VAR"))
