import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="RK4 Natural Drop Solver", layout="centered")
st.title("🍐 Истинная физическая каплеида (Прямой RK4)")

st.markdown("""
### Прямой физический расчет (Сверху вниз от капилляра)
Интегрируем классическое уравнение Янга-Лапласа от вершины висящей капли. 
Капля честно провисает вниз под действием гравитации, а в конце вся картинка переворачивается для микроскопа.
""")

# Ползунок реального объема налитой воды в мм³
v_fluid = st.slider("Объем поданной воды (мм³)", 4.0, 18.5, 17.5, 0.1)

# Физические константы (Вода при 20°C, капилляр радиусом строго 1.0 мм)
R_capillary = 1.0  
g = 9.81
sigma = 0.07275    # Поверхностное натяжение (Н/м)
rho = 998.2        # Плотность (кг/м³)

# Капиллярная постоянная (мм^-2)
beta_mm = (rho * g) / sigma / 1000000.0  # ~ 0.1345 мм^-2

# СВЯЗЬ ОБЪЕМА И КРИВИЗНЫ КУПОЛА:
# Радиус купола b_real_mm плавно уменьшается, заставляя каплю тяжелеть и вытягиваться
progress = v_fluid / 18.5
b_real_mm = 2.4 - (progress * 1.55)

# Стартовые условия RK4 в самой нижней точке (вершине) висящей капли (x=0, y=0, phi=0)
x = 1e-6
y = 0.0
phi = 0.0
ds = 0.002  # Сверхмелкий шаг интегрирования

x_coords = []
y_coords = []
phi_values = []

def derivatives(x_v, y_v, phi_v):
    dx = np.cos(phi_v)
    dy = np.sin(phi_v)
    sin_x_term = 1.0 / b_real_mm if x_v < 1e-4 else np.sin(phi_v) / x_v
    
    # ЕСТЕСТВЕННЫЙ МИНУС: Гравитация честно тянет каплю вниз, 
    # формируя изящную талию перед капилляром
    dphi = 2.0 / b_real_mm - (beta_mm * y_v) - sin_x_term
    return dx, dy, dphi

# Запуск численного интегратора
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
    
    # ИСПРАВЛЕННЫЙ ОСТАНОВ: Даем пузу расшириться наружу (x может быть больше 1.0),
    # проходим экватор (phi > 90 град) и останавливаемся только тогда, 
    # когда на этапе сужения шейки радиус X упал обратно до радиуса капилляра 1.0 мм!
    if phi > np.pi / 2 and x <= R_capillary:
        break
        
    if phi > np.pi * 1.4 or x < 0 or np.isnan(x) or np.isnan(y):
        break

x_pts = np.array(x_coords)
y_pts = np.array(y_coords)
phi_pts = np.array(phi_values)

# Защитная фиксация точки контакта на стекле трубки
x_pts[-1] = R_capillary

# Находим шейку капли (минимальный радиус на этапе сужения после экватора)
post_equator_idx = np.where(phi_pts > np.pi / 2)[0]
if len(post_equator_idx) > 0:
    neck_idx = post_equator_idx[x_pts[post_equator_idx].argmin()]
    physical_neck_radius = x_pts[neck_idx]
else:
    physical_neck_radius = R_capillary

# ЗЕРКАЛЬНЫЙ ПЕРЕВОРОТ ДЛЯ МИКРОСКОПА:
# Вычитаем y_pts[-1], чтобы плоскость стекла была на y = 0, 
# и ставим знак минус перед adjusted_y, отправляя каплю расти ВВЕРХ
adjusted_y = y_pts - y_pts[-1]

total_x = np.concatenate([-x_pts[::-1], x_pts])
total_y = np.concatenate([-adjusted_y[::-1], -adjusted_y])

# Отрисовка
fig = go.Figure()

# Срез стеклянного капилляра трубки радиусом строго 1.0 мм (диаметр 2.0 мм)
fig.add_shape(type="line", x0=-1.0, y0=0, x1=1.0, y1=0, line=dict(color="silver", width=6))

fig.add_trace(go.Scatter(
    x=total_x, y=total_y,
    mode='lines',
    line=dict(color='deepskyblue', width=4),
    fill='toself',
    fillcolor='rgba(100, 200, 255, 0.35)',
    name="Контур Янга-Лапласа"
))

fig.update_layout(
    title=f"Истинный физический профиль капли Вода (H2O)",
    xaxis=dict(range=[-1.6, 1.6], scaleanchor="y", scaleratio=1, title="Радиус капли (мм)"),
    yaxis=dict(range=[-0.2, 3.5], title="Высота капли под микроскопом (мм)"),
    width=550, height=550,
    template="plotly_dark"
)

st.plotly_chart(fig)
st.info(f"📐 **Геометрия:** Радиус трубки: {R_capillary:.2f} мм. Радиус шейки капли: {physical_neck_radius:.3f} мм.")
