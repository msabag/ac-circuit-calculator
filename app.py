import math
import matplotlib.pyplot as plt
import streamlit as st

st.title("⚡ מחשבון מעגל AC טורי (R-C)")
st.write("הזן את נתוני המעגל כדי לקבל ניתוח מלא וייצוג ויזואלי של המשולשים.")

# תפריט קלט בצד
st.sidebar.header("פרמטרים של המעגל")
V = st.sidebar.number_input("מתח המקור V (וולט):", min_value=0.1, value=220.0)
f = st.sidebar.number_input("תדר f (הרץ):", min_value=0.1, value=50.0)
R = st.sidebar.number_input("התנגדות הנגד R (אוהם):", min_value=0.1, value=100.0)

c_option = st.sidebar.radio(
    "איך תרצה להזין את הקבל?", ("קיבול C (במיקרו-פראד uF)", "היגוי קיבולי Xc (באוהם)")
)

if c_option == "קיבול C (במיקרו-פראד uF)":
    uF = st.sidebar.number_input("קיבול C (uF):", min_value=0.01, value=31.83)
    C = uF * 1e-6
    omega = 2 * math.pi * f
    Xc = 1 / (omega * C)
else:
    Xc = st.sidebar.number_input("היגוי קיבולי Xc (אוהם):", min_value=0.1, value=100.0)

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

st.markdown("---")

# --- חלק ויזואלי: ציור המשולשים ---
st.subheader("📐 משולש עכבות ומשולש הספקים")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

# 1. משולש עכבות
ax1.quiver(0, 0, R, 0, angles='xy', scale_units='xy', scale=1, color='b', label=f'R = {R:.1f} Ω')
ax1.quiver(R, 0, 0, -Xc, angles='xy', scale_units='xy', scale=1, color='r', label=f'Xc = {Xc:.1f} Ω')
ax1.quiver(0, 0, R, -Xc, angles='xy', scale_units='xy', scale=1, color='g', label=f'Z = {Z:.1f} Ω')

ax1.set_xlim(-R*0.1, R*1.2)
ax1.set_ylim(-Xc*1.2, Xc*0.2)
ax1.axhline(0, color='black', linewidth=0.5)
ax1.axvline(0, color='black', linewidth=0.5)
ax1.set_title("משולש עכבות (Impedance Triangle)")
ax1.grid(True, linestyle='--', alpha=0.5)
ax1.legend(loc='lower left')

# 2. משולש הספקים
ax2.quiver(0, 0, P, 0, angles='xy', scale_units='xy', scale=1, color='b', label=f'P = {P:.1f} W')
ax2.quiver(P, 0, 0, -Q, angles='xy', scale_units='xy', scale=1, color='r', label=f'Q = {Q:.1f} VAR')
ax2.quiver(0, 0, P, -Q, angles='xy', scale_units='xy', scale=1, color='g', label=f'S = {S:.1f} VA')

ax2.set_xlim(-P*0.1, P*1.2)
ax2.set_ylim(-Q*1.2, Q*0.2)
ax2.axhline(0, color='black', linewidth=0.5)
ax2.axvline(0, color='black', linewidth=0.5)
ax2.set_title("משולש הספקים (Power Triangle)")
ax2.grid(True, linestyle='--', alpha=0.5)
ax2.legend(loc='lower left')

plt.tight_layout()
st.pyplot(fig)

st.markdown("---")
st.write(f"**זווית מופע ($\phi$):** {phi_deg:.2f}°")
