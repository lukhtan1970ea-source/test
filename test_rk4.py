import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="RK4 True Pear Test", layout="centered")
st.title("🍐 Истинная каплеида Янга-Лапласа (RK4)")

st.markdown("""
В этой модели радиус капилляра жестко зафиксирован ($R=1.0$). 
Шейка формируется строго **внутри** контура и она **уже**, чем диаметр трубки!
""")

# Слайдеры для управления формой капли
b_param = st.slider("Радиус кривизны в вершине (b)", 0.2, 1.2, 0.45, 0.01)
beta = st.slider("Параметр формы / Гравитация (β)", 0.1, 1.5, 0.55, 0.05)

# Фиксированные стартовые параметры ОДУ в вершине перевернутой капли
x = 1e-6
y = 0.0
phi = 0.0
ds = 0.002 # Сверхмелкий шаг

x_coords = []
y_coords = []
phi_values = []

def derivatives(x_v, y_v, phi_v):
    d_x = np.cos(phi_v)
    d_y = np.sin(phi_v)
    sin_x_term = 1.0 if x_v < 1e-4 else np.sin(phi_v) / x_v
    # Минус перед beta обеспечивает правильное направление силы тяжести в перевернутом мире
    d_phi = 2.0 / b_param - (beta * y_v) - sin_x_term
    return d_x, d_y, d_phi

# Интегрируем Рунге-Кутту до тех пор, пока контур не сформирует шейку и не пойдет расширяться к стеклу
for step in range(9000):
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
    
    # Аварийный останов, если численный метод зациклился или ушел в NaN
    if phi > np.pi * 1.6 or x < 0 or np.isnan(x) or np.isnan(y):
        break

x_pts = np.array(x_coords)
y_pts = np.array(y_coords)
phi_pts = np.array(phi_values)

# Ищем индекс первой настоящей шейки (где радиус x минимален ПОСЛЕ экватора)
post_equator_idx = np.where(phi_pts > np.pi / 2)[0]

if len(post_equator_idx) > 0:
    # Ищем точку локального минимума x (самое узкое место капли)
    x_post = x_pts[post_equator_idx]
    min_x_sub_idx = x_post.argmin()
    neck_idx = post_equator_idx[min_x_sub_idx]
    
    # Чтобы показать, как капля крепится к широкому капилляру, 
    # мы берем контур чуть дальше этой шейки — на этапе расширения к стеклу
    idx = min(len(x_pts) - 1, neck_idx + 180)
    status_msg = "Физическая шейка капли успешно сформирована внутри контура!"
else:
    idx = len(x_pts) - 1
    status_msg = "Увеличьте гравитацию или уменьшите b, чтобы капля вытянулась."

x_final = x_pts[:idx+1]
y_final = y_pts[:idx+1]

# МАСШТАБИРОВАНИЕ: Конечная точка контура жестко привязывается к радиусу капилляра R = 1.0
scale_factor = 1.0 / x_final[-1]
x_scaled = x_final * scale_factor
y_scaled = y_final * scale_factor

# Вычисляем истинный радиус шейки в этом масштабе
neck_radius_scaled = x_scaled[neck_idx] if len(post_equator_idx) > 0 else 1.0

# Фиксируем основание на y = 0
base_y = y_scaled[-1]
adjusted_y = y_scaled - base_y

total_x = np.concatenate([-x_scaled[::-1], x_scaled])
total_y = np.concatenate([-adjusted_y[::-1], -adjusted_y])

# Отрисовка
fig = go.Figure()

# Рисуем серую линию капилляра шириной ровно 1.0 (от -1.0 до 1.0)
fig.add_shape(type="line", x0=-1.0, y0=0, x1=1.0, y1=0, line=dict(color="gray", width=6))

fig.add_trace(go.Scatter(
    x=total_x, y=total_y,
    mode='lines',
    line=dict(color='deepskyblue', width=4),
    fill='toself',
    fillcolor='rgba(135, 206, 250, 0.3)',
    name="Контур RK4"
))

fig.update_layout(
    title="Истинный профиль капли-груши по Янгу-Лапласу",
    xaxis=dict(range=[-1.8, 1.5], scaleanchor="y", scaleratio=1, title="X"),
    yaxis=dict(range=[-0.2, 3.0], title="Y"),
    width=500, height=500,
    template="plotly_dark"
)

st.plotly_chart(fig)
st.success(f"{status_msg} Радиус капилляра: 1.00, Истинный радиус шейки капли: {neck_radius_scaled:.2f}")
