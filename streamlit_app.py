import streamlit as st
import numpy as np
import scipy.signal as signal
import plotly.graph_objects as go

# Seiteneinstellung
st.set_page_config(page_title="PT2 Simulation", layout="wide")

st.title("Simulation eines Übertragungsglieds 2. Ordnung (PT2)")
st.markdown("""
Diese App simuliert die Sprungantwort eines Systems zweiter Ordnung in Abhängigkeit vom Dämpfungsgrad $d$ (Lehrbuchschreibweise oft auch $\zeta$ oder $\sigma$).
""")

# Layout: Aufteilung in Steuerung (links) und Grafik (rechts)
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Systemparameter")
    
    # Schieberegler für die Dämpfung D (-5 bis +5)
    d = st.slider(
        "Dämpfungsgrad (d)", 
        min_value=-5.0, 
        max_value=5.0, 
        value=0.5, 
        step=0.1,
        help="D > 0: stabil, D < 0: instabil (Aufschwingen)"
    )
    
    # Optionale Parameter für eine realistischere Anpassung
    omega_n = st.number_input("Eigenfrequenz (ω_n) in rad/s", min_value=0.1, max_value=10.0, value=2.0, step=0.1)
    K = st.number_input("Systemverstärkung (K)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)

    st.markdown("---")
    st.header("Einfluss von $d$ auf das Verhalten:")
    
    # Dynamische Erklärung je nach Dämpfungsbereich
    if d > 1:
        st.info(f"**d = {d} (Kriechfall / Überdämpft):**\n\nDas System ist stabil. Es gibt kein Überschwingen, aber die Antwort ist träge. Die Polstellen der Übertragungsfunktion sind reell und negativ.")
    elif d == 1:
        st.success(f"**d = {d} (Aperiodischer Grenzfall):**\n\nDas System erreicht den Endwert in der schnellstmöglichen Zeit, ohne dabei überzuschwingen.")
    elif 0 < d < 1:
        st.warning(f"**0 < d < 1 (Schwingungsfall / Unterdämpft):**\n\nDas System ist stabil, schwingt aber ein. Je kleiner $d$, desto ausgeprägter ist das Überschwingen und desto länger dauert das Abklingen.")
    elif d == 0:
        st.error(f"**d = {d} (Dauerschwingung / Ungedämpft):**\n\nDas System befindet sich an der Stabilitätsgrenze. Es schwingt mit der Eigenfrequenz $ω_n$ dauerhaft weiter. Die Polstellen liegen rein imaginär auf der J-Achse.")
    else:  # d < 0
        st.error(f"**d = {d} (Instabiles System / Entdämpft):**\n\nDa die Dämpfung negativ ist, wird dem System Energie zugeführt. Die Amplitude der Schwingung wächst exponentiell gegen unendlich (Aufschwingen).")

# Berechnung der Sprungantwort
# Übertragungsfunktion: G(s) = (K * omega_n^2) / (s^2 + 2*d*omega_n*s + omega_n^2)
num = [K * (omega_n ** 2)]
den = [1, 2 * d * omega_n, omega_n ** 2]
sys = signal.TransferFunction(num, den)

# Zeitvektor anpassen (bei Instabilität kürzer, damit der Plot nicht explodiert)
t_max = 20 if d >= -0.2 else 5
t = np.linspace(0, t_max, 1000)

# Sprungantwort berechnen
t, y = signal.step(sys, T=t)

# Plotting mit Plotly (Echtzeit-Interaktivität im Browser)
with col2:
    fig = go.Figure()
    
    # Sprungantwort
    fig.add_trace(go.Scatter(x=t, y=y, mode='lines', name='Sprungantwort', line=dict(color='#00CC96', width=3)))
    
    # Sollwert / Eingangsprung (nur sinnvoll darstellbar wenn stabil, sonst geht es unter)
    if d >= 0:
        fig.add_trace(go.Scatter(x=t, y=np.ones_like(t) * K, mode='lines', name='Sollwert (K)', line=dict(color='orange', dash='dash')))

    # Layout-Anpassungen
    fig.update_layout(
        title=f"Sprungantwort bei d = {d}",
        xaxis_title="Zeit (s)",
        yaxis_title="Ausgangssignal y(t)",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=60, b=20),
        height=550,
        hovermode="x"
    )
    
    # Y-Achse begrenzen bei extremer Instabilität, um Abstürze der Grafik zu verhindern
    if d < -1:
        fig.update_yaxes(range=[np.min(y)*1.1, np.max(y)*1.1])
        
    st.plotly_chart(fig, use_container_width=True)
