import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="RK4 Static Pear Test", layout="centered")
st.title("🍐 Поиск идеальной статичной груши (RK4)")

st.markdown("""
Мы зафиксировали параметры тяжелой капли перед отрывом ($b=0.6$, $\\beta=0.75$).
Уравнение Янга-Лапласа интегрируется с мелким шагом. 
""")

# Почетные стартовые условия в вершине капли
x = 1e-6
y = 0.0
phi = 0.0

ds = 0.005  # Сверхмелкий шаг для идеальной плавности
b_param = 0.6
beta = 0.75

x_coords = []
y_coords = []
phi_values = []

def derivatives(x_v, y_v, phi_v):
    d_x = np.cos(phi_v)
    d_y = np.sin(phi_v)
    # Раскрытие неопределенности в нуле
    sin_x_term = 1.0 if x_v < 1e-4 else np.sin(phi_v) / x_v
    # Классическое уравнение Янга-Лапласа
    d_phi = 2.0 / b_param + (beta * y_v) - sin_x_term
    return d_x, d_y, d_phi

# Интегрируем Рунге-Кутту до тех пор, пока контур не пойдет глубоко на сужение
for step in range(5000):
    x_coords.append(x)
    y_coords.append(y)
    phi_values.append(phi)
    
    kx1, ky1, kphi1 = derivatives(x, y, phi)
    kx2, ky2, kphi2 = derivatives(x + 0.5*ds*kx1, y + 0.5*ds*ky1, phi + 0.5*ds*kphi1)
    kx3, ky3, kphi3 = derivatives(x + 0.5*ds*kx2, y + 0.5*ds*ky2, phi + 0.5*ds*kphi2)
    kx4, ky4, kphi4 = derivatives(x + ds*kx3, y + ds*ky3, phi + ds*kphi3)
    
    x += (ds / 6.0) * (kx1 + 2.0*kx2 + 2.0*kx3 + kx4)
    y += (ds / 6.0) * (ky1 + 2.0*ky2 + 2.0*ky3 + ky4)
    phi += (ds / 6.0) * (kphi1 + 2.0*kphi2 + 2.0*kphi3 + kphi4)
    
    # Критический останов: когда контур прошел экватор, сузился и угол касательной стал почти вертикальным
    if phi > np.pi * 0.92:
        break

x_pts = np.array(x_coords)
y_pts = np.array(y_coords)

# Находим точку "талии" - место, где капля крепится к стеклянной трубке.
# Пусть радиус нашего стеклянного капилляра в масштабе равен ровно 0.6 единицам.
# Мы ищем эту координату на этапе сужения капли (в конце массива)
idx = (np.abs(x_pts - 0.6)).argmin()

# Обрезаем расчетный массив строго по границе капилляра
x_final = x_pts[:idx+1]
y_final = y_pts[:idx+1]

# Фиксируем верхний край на y = 0, чтобы капля росла вверх (для перевернутого микроскопа)
base_y = y_final[-1]
adjusted_y = y_final - base_y

total_x = np.concatenate([-x_final[::-1], x_final])
total_y = np.concatenate([-adjusted_y[::-1], -adjusted_y])

# Отрисовка статичного графика
fig = go.Figure()

# Линия среза капилляра (показывает границы трубки, к которой прилипла жидкость)
fig.add_shape(type="line", x0=-0.6, y0=0, x1=0.6, y1=0, line=dict(color="gray", width=4))

fig.add_trace(go.Scatter(
    x=total_x, y=total_y,
    mode='lines',
    line=dict(color='deepskyblue', width=4),
    fill='toself',
    fillcolor='rgba(135, 206, 250, 0.3)',
    name="Контур RK4"
))

fig.update_layout(
    title="Статический профиль капли-груши (Чистый RK4)",
    xaxis=dict(range=[-1.5, 1.5], scaleanchor="y", scaleratio=1, title="X"),
    yaxis=dict(range=[-0.2, 2.0], title="Y"),
    width=500, height=500,
    template="plotly_dark"
)

st.plotly_chart(fig)
st.success(f"Расчет завершен. Максимальный радиус капли: {np.max(x_final):.2f}, Радиус шейки на капилляре: {x_final[-1]:.2f}")
