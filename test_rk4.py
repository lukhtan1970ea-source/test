import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="RK4 Dynamic Test", layout="centered")
st.title("🔄 Динамічний тест каплеїди Янга-Лапласа (RK4)")

st.markdown("""
Параметр форми $\\beta$ (Bond number) зафіксовано. 
Ми плавно зменшуємо радіус вершини $b$, імітуючи приплив маси рідини та витягування груші.
""")

# Фіксуємо оптимальний параметр форми для красивої груші
beta = st.slider("Фізичний параметр форми (\\beta)", 0.1, 1.5, 0.6, 0.05)
ds = 0.02 # Оптимальний стабільний крок

# Контейнер для динамічного оновлення графіка
plot_placeholder = st.empty()

if st.button("🚀 Запустити динаміку наливання краплі", use_container_width=True):
    # Плавне зменшення b від плоского меніска (4.0) до витягнутої груші (0.7)
    for b_current in np.linspace(4.0, 0.1, 40):
        
        # Початкові умови RK4 (рівно 8 пробілів від краю для кожного рядка всередині циклу)
        x = 1e-6
        y = 0.0
        phi = 0.0
        
        x_coords = []
        y_coords = []
        
        def derivatives(x_v, y_v, phi_v):
            d_x = np.cos(phi_v)
            d_y = np.sin(phi_v)
            sin_x_term = 1.0 if x_v < 1e-4 else np.sin(phi_v) / x_v
            d_phi = 2.0 / b_current + (beta * y_v) - sin_x_term
            return d_x, d_y, d_phi

        for step in range(1500):
            x_coords.append(x)
            y_coords.append(y)
            
            # Крок інтегрування Рунге-Кутти 4-го порядку
            kx1, ky1, kphi1 = derivatives(x, y, phi)
            kx2, ky2, kphi2 = derivatives(x + 0.5*ds*kx1, y + 0.5*ds*ky1, phi + 0.5*ds*kphi1)
            kx3, ky3, kphi3 = derivatives(x + 0.5*ds*kx2, y + 0.5*ds*ky2, phi + 0.5*ds*kphi2)
            kx4, ky4, kphi4 = derivatives(x + ds*kx3, y + ds*ky3, phi + ds*kphi3)
            
            x += (ds / 6.0) * (kx1 + 2.0*kx2 + 2.0*kx3 + kx4)
            y += (ds / 6.0) * (ky1 + 2.0*ky2 + 2.0*ky3 + ky4)
            phi += (ds / 6.0) * (kphi1 + 2.0*kphi2 + 2.0*kphi3 + kphi4)
            
            # Зупиняємося, коли кут завалюється у шийку (досягає 135 градусів)
            if phi > np.pi * 0.75:
                break
                
        if len(x_coords) > 0:
            x_pts = np.array(x_coords)
            y_pts = np.array(y_coords)
            
            # Динамічне масштабування контуру під радіус капіляра R = 1.2
            scale_factor = 1.2 / x_pts[-1]
            x_scaled = x_pts * scale_factor
            y_scaled = y_pts * scale_factor
            
            # Фіксуємо основу краплі на y = 0
            final_y = y_scaled[-1]
            adjusted_y = y_scaled - final_y
            
            total_x = np.concatenate([-x_scaled[::-1], x_scaled])
            # Інвертуємо знак Y (-adjusted_y), щоб крапля росла ВГОРУ для мікроскопа
            total_y = np.concatenate([-adjusted_y[::-1], -adjusted_y])
            
            # Швидка перемальовка кадру анімації
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=total_x, y=total_y,
                mode='lines',
                line=dict(color='deepskyblue', width=3),
                fill='toself',
                fillcolor='rgba(135, 206, 250, 0.3)'
            ))
            
            fig.update_layout(
                title=dict(text=f"Наливання краплі в мікроскопі за Рунге-Куттою (b = {b_current:.2f})"),
                xaxis=dict(range=[-2.5, 2.5], scaleanchor="y", scaleratio=1, fixedrange=True),
                yaxis=dict(range=[-0.5, 4.5], fixedrange=True),
                width=500, height=500,
                template="plotly_dark",
                autosize=False
            )
            plot_placeholder.plotly_chart(fig, use_container_width=False, config={'staticPlot': True})
            time.sleep(0.06) # Швидкість кадрів анімації
            
    st.balloons()
