import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Smooth Pear Drop Animation", layout="centered")
st.title("🎬 Фізично згладжена анімація відриву краплі")

st.markdown("""
### Оптимізована кінематика краплі:
1. **Ніякого трясіння:** Графік зафіксовано в одному статичному слоті.
2. **Ідеальна плавність відриву:** Усунено злами контуру за рахунок розділення фігур у критичній точці.
""")

plot_placeholder = st.empty()

if st.button("🚀 Запустити безкінечний цикл дозатора", use_container_width=True):
    while True:
        # ----------------------------------------------------
        # ФАЗА 1: ПЛАВНИЙ РОСТ ТА НАЛИВАННЯ ГРУШІ (45 кадрів)
        # ----------------------------------------------------
        for progress in np.linspace(0.0, 1.0, 45):
            x_left, y_left = [], []
            x_right, y_right = [], []
            steps = 90
            
            total_height = 0.5 + (progress * 2.4)
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

            fig = go.Figure()
            fig.add_shape(type="line", x0=-1.0, y0=0, x1=1.0, y1=0, line=dict(color="silver", width=6))
            fig.add_trace(go.Scatter(
                x=x_left + x_right, y=y_left + y_right, mode='lines',
                line=dict(color='deepskyblue', width=4),
                fill='toself', fillcolor='rgba(100, 200, 255, 0.35)'
            ))
            fig.update_layout(
                title=dict(text="💧 СТАДІЯ 1: Наливання та витягування груші"),
                xaxis=dict(range=[-1.8, 1.8], scaleanchor="y", scaleratio=1, fixedrange=True, title="Радіус (мм)"),
                yaxis=dict(range=[-5.5, 0.5], fixedrange=True, title="Висота (мм)"),
                width=550, height=550, template="plotly_dark"
            )
            # ФІКСАЦІЯ КЛЮЧА: Завжди один єдиний key="drop_chart" прибирає трясіння!
            plot_placeholder.plotly_chart(fig, use_container_width=False, config={'staticPlot': True}, key="drop_chart")
            time.sleep(0.04)

        # ----------------------------------------------------
        # ФАЗА 2: МОМЕНТ МИТТЄВОГО ВИТЯГУВАННЯ ШИЙКИ (Slow Mo, 6 кадрів)
        # ----------------------------------------------------
        final_bulb_r = max_bulb_radius 
        final_height = total_height
        
        for snap in np.linspace(0.0, 1.0, 6):
            x_left, y_left = [], []
            x_right, y_right = [], []
            
            # Довжина капілярної нитки (шейки) стрімко росте вниз, витягуючи мешочек
            stretch_y = final_height + (snap * 0.6)
            # Шийка стоншується абсолютно плавно, без зламів
            snap_neck = cur_neck_radius - (snap * (cur_neck_radius - 0.25))
            
            for i in range(steps + 1):
                t = i / steps
                y_val = -(t * stretch_y)
                
                # Математично згладжене стоншення: S-подібний коефіцієнт адаптується до видовження
                if t < 0.50:
                    k = t / 0.50
                    smooth_factor = 3 * (k ** 2) - 2 * (k ** 3)
                    r_val = 1.0 + (final_bulb_r * 0.95 - 1.0) * smooth_factor
                    # Формуємо летячу тонку талію нитки під капіляром
                    neck_fade = np.sin(k * np.pi)
                    r_val -= (1.0 - snap_neck) * neck_fade
                else:
                    k = (t - 0.50) / 0.50
                    r_val = final_bulb_r * 1.05 * np.sqrt(max(0.0, 1.0 - k * k))

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
                title=dict(text="⚠️ СТАДІЯ 2: Стрімке видовження шийки перед розривом"),
                xaxis=dict(range=[-1.8, 1.8], scaleanchor="y", scaleratio=1, fixedrange=True),
                yaxis=dict(range=[-5.5, 0.5], fixedrange=True),
                width=550, height=550, template="plotly_dark"
            )
            plot_placeholder.plotly_chart(fig, use_container_width=False, config={'staticPlot': True}, key="drop_chart")
            time.sleep(0.05)

        # ----------------------------------------------------
        # ФАЗА 3: ПОЛЕТ ІДЕАЛЬНОЇ СФЕРИЧНОЇ КРАПЛІ (12 кадрів)
        # ----------------------------------------------------
        sphere_r = final_bulb_r * 0.82
        start_center_y = -stretch_y + sphere_r
        
        for fall in np.linspace(0.0, 1.0, 14):
            # Залишок на капілярі плавно втягується в плоску лінзу меніска
            rest_h = 0.4 * (1.0 - fall) + 0.1
            theta = np.linspace(0, np.pi, 40)
            rest_x = list(-np.sin(theta)) + list(np.sin(theta)[::-1])
            rest_y = list(-np.cos(theta) * rest_h) + [0.0]*40
            
            # Летячий великий мешочек миттєво стягується в ідеальну сферу за законами фізики
            center_y = start_center_y - (fall * 2.6)
            phi_sphere = np.linspace(0, 2 * np.pi, 60)
            ball_x = 0.0 + sphere_r * np.cos(phi_sphere)
            ball_y = center_y + sphere_r * np.sin(phi_sphere)
            
            fig = go.Figure()
            fig.add_shape(type="line", x0=-1.0, y0=0, x1=1.0, y1=0, line=dict(color="silver", width=6))
            
            # Залишок
            fig.add_trace(go.Scatter(
                x=rest_x, y=rest_y, mode='lines',
                line=dict(color='deepskyblue', width=3),
                fill='toself', fillcolor='rgba(100, 200, 255, 0.25)', showlegend=False
            ))
            # Летяча сфера
            fig.add_trace(go.Scatter(
                x=ball_x, y=ball_y, mode='lines',
                line=dict(color='lightskyblue', width=4),
                fill='toself', fillcolor='rgba(100, 200, 255, 0.45)', name="Крапля"
            ))
            
            fig.update_layout(
                title=dict(text="💧 СТАДІЯ 3: Момент відриву фракції та політ"),
                xaxis=dict(range=[-1.8, 1.8], scaleanchor="y", scaleratio=1, fixedrange=True),
                yaxis=dict(range=[-5.5, 0.5], fixedrange=True),
                width=550, height=550, template="plotly_dark"
            )
            plot_placeholder.plotly_chart(fig, use_container_width=False, config={'staticPlot': True}, key="drop_chart")
            time.sleep(0.02)

        time.sleep(0.4) # Пауза перед наступною краплею
