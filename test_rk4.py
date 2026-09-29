import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="RK4 Static Pear Test", layout="centered")
st.title("Pear-Shaped Drop Solver (RK4)")

st.markdown("""
Крутіть слайдери, щоб знайти параметри **фізичної груші**.
* Зменшення **b** збільшує об'єм та витягує краплю.
* Збільшення **Bond number (β)** посилює вплив гравітації.
""")

# Параметри форми для пошуку груші
b_param = st.slider("Радіус кривизни у вершині (b)", 0.15, 1.0, 0.35, 0.01)
beta = st.slider("Параметр форми / Гравітація (Bond number / β)", 0.1, 2.0, 0.9, 0.05)
r_capillary = st.slider("Радіус капіляра для обрізки (R)", 0.2, 1.0, 0.5, 0.05)

# Початкові умови у вершині краплі
x = 1e-6
y = 0.0
phi = 0.0
ds = 0.002  # Наддрібний крок для високої точності

x_coords = []
y_coords = []
phi_values = []

def derivatives(x_v, y_v, phi_v):
    d_x = np.cos(phi_v)
    d_y = np.sin(phi_v)
    sin_x_term = 1.0 if x_v < 1e-4 else np.sin(phi_v) / x_v
    d_phi = 2.0 / b_param - (beta * y_v) - sin_x_term
    return d_x, d_y, d_phi

# Інтегруємо Рунге-Кутту з великим запасом кроків
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
    
    if phi > np.pi * 1.8 or x < 0 or np.isnan(x) or np.isnan(y):
        break

x_pts = np.array(x_coords)
y_pts = np.array(y_coords)
phi_pts = np.array(phi_values)

# ІСПРАВЛЕНО: Явно витягуємо одновимірний масив індексів поза екватором за допомогою [0]
post_equator_indices = np.where(phi_pts > np.pi / 2)[0]

if len(post_equator_indices) > 0:
    # Шукаємо ПЕРШЕ пересечення з радіусом капіляра на етапі звуження шийки
    idx = post_equator_indices[0] # дефолтне значення (початок екватора)
    
    for i in post_equator_indices:
        # Як тільки радіус контуру став меншим або рівним радіусу трубки — це і є наша талія!
        if x_pts[i] <= r_capillary:
            idx = i
            break
            
    status_msg = "✅ Ідеальна одиночна крапля-груша успішно виділена через першу шийку!"
else:
    idx = len(x_pts) - 1
    status_msg = "💡 Крапля ще занадто мала, шийка не сформувалася. Зменшуйте 'b' або збільшуйте 'β'."

# Обрізаємо масиви точок чітко по знайденому індексу першої талії
x_final = x_pts[:idx+1]
y_final = y_pts[:idx+1]

# Фіксуємо верхній край на y = 0 (ростемо вгору для мікроскопа)
base_y = y_final[-1]
adjusted_y = y_final - base_y

total_x = np.concatenate([-x_final[::-1], x_final])
total_y = np.concatenate([-adjusted_y[::-1], -adjusted_y])

# Отрисовка графіка Plotly
fig = go.Figure()

# Сіра лінія зрізу скляного капіляра трубки
fig.add_shape(type="line", x0=-r_capillary, y0=0, x1=r_capillary, y1=0, line=dict(color="gray", width=5))

fig.add_trace(go.Scatter(
    x=total_x, y=total_y,
    mode='lines',
    line=dict(color='deepskyblue', width=4),
    fill='toself',
    fillcolor='rgba(135, 206, 250, 0.3)',
    name="RK4 Контур"
))

fig.update_layout(
    title="Одиночний профіль краплі-груші за Рунге-Куттою",
    xaxis=dict(range=[-2.0, 2.0], scaleanchor="y", scaleratio=1, title="X"),
    yaxis=dict(range=[-0.2, 3.5], title="Y"),
    width=500, height=500,
    template="plotly_dark"
)

st.plotly_chart(fig)
st.success(status_msg)
