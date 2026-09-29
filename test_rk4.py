import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="RK4 Dynamic Test", layout="centered")
st.title("🔄 Динамический тест каплеиды Янга-Лапласа (RK4)")

st.markdown("""
Параметр формы $\\beta$ (Bond number) зафиксирован. 
Мы плавно уменьшаем радиус вершины $b$, имитируя приток массы жидкости.
""")

# Жестко фиксируем физический параметр формы для наглядности груши
beta = st.slider("Физический параметр формы (\\beta)", 0.1, 1.5, 0.6, 0.05)
ds = 0.02 # Оптимальный стабильный шаг

# Контейнер для динамического обновления графика
plot_placeholder = st.empty()

if st.button("🚀 Запустить динамику наливания капли", use_container_width=True):
    # Плавное уменьшение b симулирует рост объема и вытягивание капли в грушу
    # Идем от плоского мениска (b=4.0) до вытянутой капли (b=1.1)
    for b_current in np.linspace(4.0, 1.1, 40):
        
        # Почетные условия RK4
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

        for step in range(1200):
            x_coords.append(x)
            y_coords.append(y)
            
            # Шаг интегрирования RK4
            kx1, ky1, kphi1 = derivatives(x, y, phi)
            kx2, ky2, kphi2 = derivatives(x + 0.5*ds*kx1, y + 0.5*ds*ky1, phi + 0.5*ds*kphi1)
            kx3, ky3, kphi3 = derivatives(x + 0.5*ds*kx2, y + 0.5*ds*ky2, phi + 0.5*ds*kphi2)
            kx4, ky4, kphi4 = derivatives(x + ds*kx3, y + ds*ky3, phi + ds*kphi3)
            
            x += (ds / 6.0) * (kx1 + 2.0*kx2 + 2.0*kx3 + kx4)
            y += (ds / 6.0) * (ky1 + 2.0*ky2 + 2.0*ky3 + ky4)
            phi += (ds / 6.0) * (kphi1 + 2.0*kphi2 + 2.0*kphi3 + kphi4)
            
            # Условие останова: интегрируем строго до фиксированного радиуса капилляра
            # Пусть радиус нашего виртуального капилляра равен 1.2 единицам
            if x >= 1.2 or phi > np.pi * 1.3:
                break
                
        if len(x_coords) > 0:
            x_pts = np.array(x_coords)
            y_pts = np.array(y_coords)
            
            # Центрируем каплю по оси Y, чтобы её верхний край (крепление) 
            # всегда оставался неподвижным на уровне y = 0
            final_y = y_pts[-1]
            adjusted_y = y_pts - final_y
            
            total_x = np.concatenate([-x_pts[::-1], x_pts])
            total_y = np.concatenate([adjusted_y[::-1], adjusted_y])
            
            # Быстрая перерисовка кадра
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=total_x, y=total_y, # капля растет вниз от y=0
                mode='lines',
                line=dict(color='deepskyblue', width=3),
                fill='toself',
                fillcolor='rgba(135, 206, 250, 0.3)'
            ))
            
            fig.update_layout(
                title=dict(text=f"Наливание капли в реальном времени (b = {b_current:.2f})"),
                xaxis=dict(range=[-2.5, 2.5], scaleanchor="y", scaleratio=1, fixedrange=True),
                yaxis=dict(range=[-3.5, 0.5], fixedrange=True),
                width=500, height=500,
                template="plotly_dark",
                autosize=False
            )
            # Выводим текущий кадр в контейнер без перезагрузки страницы
            plot_placeholder.plotly_chart(fig, use_container_width=False, config={'staticPlot': True})
            time.sleep(0.04) # Скорость анимации
            
    st.balloons()
