import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="RK4 Static Pear Test", layout="centered")
st.title("🍐 Интерактивный поиск статической груши (RK4)")

st.markdown("""
Крутите слайдеры, чтобы найти параметры **физической груши**.
* Уменьшение **b** увеличивает объём и вытягивает каплю.
* Увеличение **Bond number (β)** усиливает влияние гравитации.
""")

# Правильные критические диапазоны для поиска груши
b_param = st.slider("Радиус кривизны в вершине (b)", 0.15, 1.0, 0.35, 0.01)
beta = st.slider("Параметр формы / Гравитация (Bond number / β)", 0.1, 2.0, 0.9, 0.05)
r_capillary = st.slider("Радиус капилляра для обрезки (R)", 0.2, 1.0, 0.5, 0.05)

# Почетные стартовые условия в вершине капли
x = 1e-6
y = 0.0
phi = 0.0
ds = 0.002  # Ультра-мелкий шаг для точности

x_coords = []
y_coords = []
phi_values = []

def derivatives(x_v, y_v, phi_v):
    d_x = np.cos(phi_v)
    d_y = np.sin(phi_v)
    sin_x_term = 1.0 if x_v < 1e-4 else np.sin(phi_v) / x_v
    d_phi = 2.0 / b_param - (beta * y_v) - sin_x_term # Исправлен знак для устойчивости роста
    return d_x, d_y, d_phi

# Интегрируем Рунге-Кутту с запасом
for step in range(8000):
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
    
    # Защитный останов, если метод уходит в бесконечность или закручивается в узел
    if phi > np.pi * 1.5 or x < 0 or np.isnan(x) or np.isnan(y):
        break

x_pts = np.array(x_coords)
y_pts = np.array(y_coords)

# Пытаемся найти точку обрезки на капилляре
# Ищем её после экватора (когда угол phi > 90 градусов / np.pi/2)
post_equator_indices = np.where(np.array(phi_values) > np.pi / 2)[0]

if len(post_equator_indices) > 0:
    # Ищем индекс, где координата X на этапе сужения ближе всего к заданному радиусу капилляра
    x_post = x_pts[post_equator_indices]
    sub_idx = (np.abs(x_post - r_capillary)).argmin()
    idx = post_equator_indices[sub_idx]
    status_msg = "Капля зашла за экватор и сформировала шейку!"
else:
    # Если капля маленькая и не дошла до экватора, берем последнюю точку
    idx = len(x_pts) - 1
    status_msg = "Капля слишком маленькая, шейка ещё не сформировалась. Уменьшайте 'b' или увеличивайте 'β'."

x_final = x_pts[:idx+1]
y_final = y_pts[:idx+1]

# Фиксируем верхний край на y = 0 (растём вверх для микроскопа)
base_y = y_final[-1]
adjusted_y = y_final - base_y

total_x = np.concatenate([-x_final[::-1], x_final])
total_y = np.concatenate([-adjusted_y[::-1], -adjusted_y])

# Отрисовка
fig = go.Figure()
# Серая линия капилляра
fig.add_shape(type="line", x0=-r_capillary, y0=0, x1=r_capillary, y1=0, line=dict(color="gray", width=4))

fig.add_trace(go.Scatter(
    x=total_x, y=total_y,
    mode='lines',
    line=dict(color='deepskyblue', width=4),
    fill='toself',
    fillcolor='rgba(135, 206, 250, 0.3)',
    name="RK4 Контур"
))

fig.update_layout(
    title="Поиск профиля капли-груши (Чистый RK4)",
    xaxis=dict(range=[-2.0, 2.0], scaleanchor="y", scaleratio=1, title="X"),
    yaxis=dict(range=[-0.2, 3.5], title="Y"),
    width=500, height=500,
    template="plotly_dark"
)

st.plotly_chart(fig)

if len(post_equator_indices) > 0:
    st.success(f"✅ {status_msg} Макс. радиус пуза: {np.max(x_final):.2f}")
else:
    st.info(f"💡 {status_msg}")
