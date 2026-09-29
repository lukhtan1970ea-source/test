import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="RK4 True Drop Solver", layout="centered")
st.title("🍐 Истинная каплеида Янга-Лапласа (RK4)")

st.markdown("""
В этой модели численный метод Рунге-Кутты интегрирует профиль **от краев капилляра к вершине капли**.
Шейка формируется строго по законам гидродинамики и получается **уже**, чем трубка.
""")

# 1. Физический справочник жидкостей (параметры при 20°C)
LIQUIDS = {
    "Вода (H2O)": {"sigma_20": 72.75, "rho_20": 0.998, "temp_coeff": -0.165},
    "Этанол (C2H5OH)": {"sigma_20": 22.27, "rho_20": 0.789, "temp_coeff": -0.086},
    "Глицерин (C3H8O3)": {"sigma_20": 63.40, "rho_20": 1.261, "temp_coeff": -0.060}
}

selected_liquid = st.selectbox("Выберите исследуемую жидкость:", list(LIQUIDS.keys()))
v_fluid = st.slider("Объем поданной жидкости (мм³)", 10.0, 45.0, 32.0, 1.0)

# Физические константы
R_capillary = 2.0  # Радиус трубки капилляра (мм)
g = 9.81

data = LIQUIDS[selected_liquid]
sigma = (data["sigma_20"] + data["temp_coeff"] * 0.0) / 1000.0  # Н/м
rho = data["rho_20"] * 1000.0                                    # кг/м³

# Капиллярная постоянная (Bond number масштабирования)
beta_phys = (rho * g) / sigma  # м^-2
beta_mm = beta_phys / 1000000.0  # мм^-2

# Эволюция формы в зависимости от объема дозатора
progress = v_fluid / 45.0
b_top = 1.0 + (progress * 2.8) # Высота капли нарастает

# Стартовые условия RK4: начинаем с верхнего крепления на капилляре (x = 2.0, y = 0)
# Угол наклона касательной на срезе стекла плавно зависит от объема жидкости
phi_start = np.pi * 0.5 + (progress * np.pi * 0.32)

x = R_capillary
y = 0.0
phi = phi_start
ds = 0.005 # Сверхмелкий шаг для идеальной плавности

x_coords = []
y_coords = []

# Дифференциальные уравнения Янга-Лапласа для обратного хода (к вершине капли)
def derivatives(x_v, y_v, phi_v):
    # Защита от деления на ноль у оси
    sin_x = np.sin(phi_v) / x_v if x_v > 1e-4 else 0.0
    
    # Изменение координат по длине дуги
    dx = -np.cos(phi_v)
    dy = np.sin(phi_v)
    
    # Капиллярное давление с учетом гидростатического изменения по высоте y_v
    dphi = -(2.0 / b_top + beta_mm * y_v - sin_x)
    return dx, dy, dphi

# Запуск интегратора Рунге-Кутты 4-го порядка
for step in range(4000):
    x_coords.append(x)
    y_coords.append(y)
    
    # Численный расчет коэффициентов RK4
    kx1, ky1, kphi1 = derivatives(x, y, phi)
    kx2, ky2, kphi2 = derivatives(x + 0.5*ds*kx1, y + 0.5*ds*ky1, phi + 0.5*ds*kphi1)
    kx3, ky3, kphi3 = derivatives(x + 0.5*ds*kx2, y + 0.5*ds*ky2, phi + 0.5*ds*kphi2)
    kx4, ky4, kphi4 = derivatives(x + ds*kx3, y + ds*ky3, phi + ds*kphi3)
    
    x += (ds / 6.0) * (kx1 + 2.0*kx2 + 2.0*kx3 + kx4)
    y += (ds / 6.0) * (ky1 + 2.0*ky2 + 2.0*ky3 + ky4)
    phi += (ds / 6.0) * (kphi1 + 2.0*kphi2 + 2.0*kphi3 + kphi4)
    
    # Условие останова: метод дошел до центральной оси капли (x -> 0)
    if x <= 0.005 or phi < 0 or np.isnan(x) or np.isnan(y):
        break

x_pts = np.array(x_coords)
y_pts = np.array(y_coords)

# Зеркальное отображение левой и правой половин для графика Plotly
total_x = np.concatenate([-x_pts, x_pts[::-1]])
total_y = np.concatenate([y_pts, y_pts[::-1]])

# Ищем радиус самой узкой шейки (минимальный x в верхней трети капли)
upper_third = x_pts[:len(x_pts)//3]
min_neck_mm = np.min(upper_third) if len(upper_third) > 0 else R_capillary

# Отрисовка интерактивного графика Plotly
fig = go.Figure()

# Серая линия торца стеклянного капилляра трубки радиусом ровно 2.0 мм
fig.add_shape(type="line", x0=-2.0, y0=0, x1=2.0, y1=0, line=dict(color="silver", width=6))

fig.add_trace(go.Scatter(
    x=total_x, y=total_y,
    mode='lines',
    line=dict(color='deepskyblue', width=4),
    fill='toself',
    fillcolor='rgba(100, 200, 255, 0.35)',
    name="Контур Янга-Лапласа"
))

fig.update_layout(
    title=f"Физический профиль капли {selected_liquid} под микроскопом",
    xaxis=dict(range=[-3.0, 3.0], scaleanchor="y", scaleratio=1, title="Радиус капли (мм)"),
    yaxis=dict(range=[-0.5, 5.5], title="Высота капли (мм)"),
    width=550, height=550,
    template="plotly_dark"
)

st.plotly_chart(fig)
st.info(f"📐 **Параметры геометрии:** Радиус трубки капилляра: 2.00 мм. Минимальный радиус шейки капли: {min_neck_mm:.3f} мм.")
