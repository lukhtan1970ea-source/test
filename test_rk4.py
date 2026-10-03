import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Perfect Pear Drop Test", layout="centered")
st.title("🍐 Безупречно гладкая капля-груша")

st.markdown("""
### Полное сглаживание: устранение углов и изломов
Контур переписан на единую гладкую математическую кривую. Переход от изящной шейки
к увесистому, широкому мешочку стал абсолютно непрерывным, текучим и сглаженным.
""")

# Ползунок стадии наливания
progress = st.slider("Стадия наливания капли (Ползунок объема)", 0.0, 1.0, 0.85, 0.05)

# Радиус стеклянного капилляра строго 1.0 мм (диаметр 2.0 мм)
R_capillary = 1.0  

x_left, y_left = [], []
x_right, y_right = [], []
steps = 100  # Максимальное количество точек для идеальной плавности

for i in range(steps + 1):
    t = i / steps  # Параметр высоты контура (от 0 - капилляр, до 1 - вершина)
    
    # Высота провисания капли растет плавно
    total_height = 0.7 + (progress * 2.5)
    y_val = -(t * total_height) # висит строго ВНИЗ
    
    # Геометрические параметры, зависящие от объема
    max_bulb_radius = 1.0 + (progress * 0.55)  # Увесистый широкий мешочек
    cur_neck_radius = 1.0 - (progress * 0.08)  # Аккуратная шейка, чуть уже капилляра
    
    # СБОРКА АБСОЛЮТНО ГЛАДКОГО СИЛУЭТА:
    # Используем гладкую функцию профиля, которая убирает любые стыки и углы
    if t < 0.65:
        # Единая плавная S-образная кривая для всей верхней половины капли (шейка + переход к пузу)
        # Она гарантирует нулевой излом и идеальный перетек линий
        k = t / 0.65
        # Кубический профиль сглаживания
        smooth_factor = 3 * (k ** 2) - 2 * (k ** 3)
        r_val = 1.0 + (max_bulb_radius - 1.0) * smooth_factor
        
        # Дополнительно углубляем талию шейки в верхней четверти, делая прогиб ленивым и текучим
        if t < 0.4:
            neck_fade = np.sin((t / 0.4) * np.pi)
            r_val -= (1.0 - cur_neck_radius) * neck_fade
    else:
        # Нижний сферический купол мешочка
        k = (t - 0.65) / 0.35
        # Идеальное круговое сглаживание до оси по закону Пифагора
        r_val = max_bulb_radius * np.sqrt(max(0.0, 1.0 - k * k))

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
📐 **Параметры сглаженного силуэта:**
* Диаметр капилляра трубки: **2.00 мм** (Радиус 1.0 мм)
* Максимальный радиус мешочка: **{max_bulb_radius:.2f} мм**
* Минимальный радиус шейки: **{cur_neck_radius:.3f} мм** (Шейка плавно уходит внутрь всего на {1.0 - cur_neck_radius:.2f} мм)
""")
