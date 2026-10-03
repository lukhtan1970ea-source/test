import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Perfect Pear Drop Test", layout="centered")
st.title("🍐 Идеальная лабораторная капля-груша")

st.markdown("""
### Коррекция геометрии: Плавный силуэт и большой мешок
Контур оптимизирован под реальное видео: пузо капли наливается увесистым, широким мешком, 
а изгиб шейки у самого основания стеклянной трубки стал ультра-плавным и сглаженным.
""")

# Ползунок стадии наливания
progress = st.slider("Стадия наливания капли (Ползунок объема)", 0.0, 1.0, 0.85, 0.05)

# Радиус стеклянного капилляра строго 1.0 мм (диаметр 2.0 мм)
R_capillary = 1.0  

x_left, y_left = [], []
x_right, y_right = [], []
steps = 80  # Больше точек для безупречной гладкости линий

for i in range(steps + 1):
    t = i / steps  # Параметр высоты контура (от 0 - капилляр, до 1 - вершина)
    
    # Высота провисания капли растет плавно
    total_height = 0.7 + (progress * 2.5)
    y_val = -(t * total_height) # висит строго ВНИЗ
    
    # ИСПРАВЛЕНО: Увеличили максимальный радиус пуза (мешка) для весомого объема
    max_bulb_radius = 1.0 + (progress * 0.55)
    
    # Радиус шейки плавно сужается внутри контура, оставаясь изящным
    cur_neck_radius = 1.0 - (progress * 0.10)
    
    # ИСПРАВЛЕНО: Зона шейки расширена до 0.35, чтобы сделать изгиб перетяжки ультра-плавным
    if t < 0.35:
        # Плавный, текучий косинусоидальный переход от среза стекла к талии
        k = t / 0.35
        factor = 0.5 - 0.5 * np.cos(k * np.pi)
        r_val = 1.0 - (1.0 - cur_neck_radius) * factor
    else:
        # Объёмный широкий мешок, переходящий в идеальный сферический купол
        k = (t - 0.35) / 0.65
        
        # Линия мягко наливается от шейки к широкому пузу
        r_base = cur_neck_radius + (max_bulb_radius - cur_neck_radius) * np.sin(k * np.pi / 2)
        
        # Нижняя маковка закругляется по идеальному круговому закону Пифагора
        if k > 0.4:
            edge = (k - 0.4) / 0.6
            r_val = r_base * np.sqrt(max(0.0, 1.0 - edge * edge))
        else:
            r_val = r_base

    x_left.append(-r_val)
    y_left.append(y_val)
    x_right.insert(0, r_val)
    y_right.insert(0, y_val)

total_x = np.array(x_left + x_right)
total_y = np.array(y_left + y_right)

# Отрисовка графика
fig = go.Figure()

# Срез стеклянной трубки капилляра (серая линия диаметром 2.0 мм)
fig.add_shape(type="line", x0=-1.0, y0=0, x1=1.0, y1=0, line=dict(color="silver", width=6))

fig.add_trace(go.Scatter(
    x=total_x, y=total_y,
    mode='lines',
    line=dict(color='deepskyblue', width=4),
    fill='toself',
    fillcolor='rgba(100, 200, 255, 0.35)',
    name="Контур капли"
))

fig.update_layout(
    title=f"Визуальный профиль капли (Объем: {progress:.2f})",
    xaxis=dict(range=[-1.8, 1.8], scaleanchor="y", scaleratio=1, title="Радиус капли (мм)"),
    yaxis=dict(range=[-3.6, 0.4], fixedrange=True, title="Высота капли (мм)"),
    width=550, height=550,
    template="plotly_dark"
)

st.plotly_chart(fig)

st.info(f"""
📐 **Геометрические параметры силуэта:**
* Радиус трубки капилляра: **1.00 мм** (Диаметр 2.0 мм)
* Максимальный радиус мешка (пуза): **{max_bulb_radius:.2f} мм** (Шире трубки на {max_bulb_radius - 1.0:.2f} мм)
* Истинный радиус шейки капли: **{cur_neck_radius:.3f} мм** (Шейка уже трубки всего на {1.0 - cur_neck_radius:.2f} мм)
""")
