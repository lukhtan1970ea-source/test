import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="RK4 Dynamic Pear", layout="centered")
st.title("🎬 Анімація наливання та відриву краплі-груші")

st.markdown("""
Повний гідродинамічний цикл на основі нашої згладженої геометричної моделі.
Крапля плавно росте, витягується в щільну грушу, обривається і летить вниз.
""")

# Контейнер для швидкої перемальовки кадрів
plot_placeholder = st.empty()

if st.button("🚀 Запустити безкінечну анімацію дозатора", use_container_width=True):
    frame_id = 0  # Лічильник для унікальних ID елементів Streamlit
    
    while True:
        # ----------------------------------------------------
        # ФАЗА 1: ПЛАВНИЙ РОСТ ТА НАЛИВАННЯ ГРУШІ (45 кадрів)
        # ----------------------------------------------------
        for progress in np.linspace(0.0, 1.0, 45):
            frame_id += 1
            x_left, y_left = [], []
            x_right, y_right = [], []
            steps = 80
            
            total_height = 0.5 + (progress * 2.5)
            max_bulb_radius = 1.0 + (progress * 0.55)
            cur_neck_radius = 1.0 - (progress * 0.08)
            
            for i in range(steps + 1):
                t = i / steps
                y_val = -(t * total_height)
                
                if t < 0.65:
                    k = t / 0.65
                    smooth_factor = 3 * (k ** 2) - 2 * (k ** 3)
                    r_val = 1.0 + (max_bulb_radius - 1.0) * smooth_factor
                    if t < 0.4:
                        neck_fade = np.sin((t / 0.4) * np.pi)
                        r_val -= (1.0 - cur_neck_radius) * neck_fade
                else:
                    k = (t - 0.65) / 0.35
                    r_val = max_bulb_radius * np.sqrt(max(0.0, 1.0 - k * k))

                x_left.append(-r_val)
                y_left.append(y_val)
                x_right.insert(0, r_val)
                y_right.insert(0, y_val)

            total_x = x_left + x_right
            total_y = y_left + y_right
            
            fig = go.Figure()
            fig.add_shape(type="line", x0=-1.0, y0=0, x1=1.0, y1=0, line=dict(color="silver", width=6))
            fig.add_trace(go.Scatter(
                x=total_x, y=total_y, mode='lines',
                line=dict(color='deepskyblue', width=4),
                fill='toself', fillcolor='rgba(100, 200, 255, 0.35)'
            ))
            fig.update_layout(
                title=dict(text=f"Стадія: Наливання фракції (Об'єм краплі росте)"),
                xaxis=dict(range=[-1.8, 1.8], scaleanchor="y", scaleratio=1, fixedrange=True, title="Радіус (мм)"),
                yaxis=dict(range=[-5.5, 0.5], fixedrange=True, title="Висота (мм)"),
                width=550, height=550, template="plotly_dark"
            )
            # ВИПРАВЛЕНО: Додано унікальний ключ для запобігання StreamlitDuplicateElementId
            plot_placeholder.plotly_chart(fig, use_container_width=False, config={'staticPlot': True}, key=f"f_{frame_id}")
            time.sleep(0.04)

        # ----------------------------------------------------
        # ФАЗА 2: МОМЕНТ МГНОВЕННОГО ОТРИВА (Slow Motion, 5 кадров)
        # ----------------------------------------------------
        final_bulb_r = max_bulb_radius 
        final_height = total_height
        
        for snap in np.linspace(0.0, 1.0, 5):
            frame_id += 1
            x_left, y_left = [], []
            x_right, y_right = [], []
            
            snap_neck = cur_neck_radius * (1.0 - snap) + 0.1 * snap
            
            for i in range(steps + 1):
                t = i / steps
                y_val = -(t * final_height)
                
                if t < 0.65:
                    k = t / 0.65
                    smooth_factor = 3 * (k ** 2) - 2 * (k ** 3)
                    r_val = 1.0 + (final_bulb_r - 1.0) * smooth_factor
                    if t < 0.4:
                        neck_fade = np.sin((t / 0.4) * np.pi)
                        r_val -= (1.0 - snap_neck) * neck_fade
                else:
                    k = (t - 0.65) / 0.35
                    r_val = final_bulb_r * np.sqrt(max(0.0, 1.0 - k * k))

                x_left.append(-r_val)
                y_left.append(y_val)
                x_right.insert(0, r_val)
                y_right.insert(0, y_val)

            fig = go.Figure()
            fig.add_shape(type="line", x0=-1.0, y0=0, x1=1.0, y1=0, line=dict(color="silver", width=6))
            fig.add_trace(go.Scatter(
                x=x_left + x_right, y=y_left + y_right, mode='lines',
                line=dict(color='deepskyblue', width=4),
                fill='toself', fillcolor='rgba(100, 200, 255, 0.35)'
            ))
            fig.update_layout(
                title=dict(text="⚠️ КРИТИЧНА СТАДІЯ: Стоншення шийки"),
                xaxis=dict(range=[-1.8, 1.8], scaleanchor="y", scaleratio=1, fixedrange=True),
                yaxis=dict(range=[-5.5, 0.5], fixedrange=True),
                width=550, height=550, template="plotly_dark"
            )
            # ВИПРАВЛЕНО: Додано унікальний ключ
            plot_placeholder.plotly_chart(fig, use_container_width=False, config={'staticPlot': True}, key=f"f_{frame_id}")
            time.sleep(0.03)

        # ----------------------------------------------------
        # ФАЗА 3: ПОЛЕТ СФЕРИЧЕСКОЙ КАПЛИ ВНИЗ (12 кадров)
        # ----------------------------------------------------
        sphere_r = final_bulb_r * 0.85 
        start_center_y = -final_height + sphere_r
        
        for fall in np.linspace(0.0, 1.0, 12):
            frame_id += 1
            rest_h = 0.4 * (1.0 - fall) + 0.1
            theta = np.linspace(0, np.pi, 40)
            rest_x = list(-np.sin(theta)) + list(np.sin(theta)[::-1])
            rest_y = list(-np.cos(theta) * rest_h) + [0.0]*40
            
            center_y = start_center_y - (fall * 2.8)
            phi_sphere = np.linspace(0, 2 * np.pi, 60)
            ball_x = 0.0 + sphere_r * np.cos(phi_sphere)
            ball_y = center_y + sphere_r * np.sin(phi_sphere)
            
            fig = go.Figure()
            fig.add_shape(type="line", x0=-1.0, y0=0, x1=1.0, y1=0, line=dict(color="silver", width=6))
            
            fig.add_trace(go.Scatter(
                x=rest_x, y=rest_y, mode='lines',
                line=dict(color='deepskyblue', width=3),
                fill='toself', fillcolor='rgba(100, 200, 255, 0.25)', showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=ball_x, y=ball_y, mode='lines',
                line=dict(color='lightskyblue', width=4),
                fill='toself', fillcolor='rgba(100, 200, 255, 0.45)', name="Крапля"
            ))
            
            fig.update_layout(
                title=dict(text="💧 СТАТУС: Відрив та вільне падіння"),
                xaxis=dict(range=[-1.8, 1.8], scaleanchor="y", scaleratio=1, fixedrange=True),
                yaxis=dict(range=[-5.5, 0.5], fixedrange=True),
                width=550, height=550, template="plotly_dark"
            )
            # ВИПРАВЛЕНО: Додано унікальний ключ для飛行 капли
            plot_placeholder.plotly_chart(fig, use_container_width=False, config={'staticPlot': True}, key=f"f_{frame_id}")
            time.sleep(0.02)

        time.sleep(0.3)
