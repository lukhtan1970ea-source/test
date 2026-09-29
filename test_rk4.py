import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="RK4 Drop Test", layout="centered")
st.title("🧪 Тест гидродинамического контура Янга-Лапласа (RK4)")

st.markdown("""
Этот стенд рассчитывает форму висящей капли путем численного интегрирования системы ОДУ:
* $dx/ds = \cos(\phi)$
* $dy/ds = \sin(\phi)$
* $d\phi/ds = 2 + \\beta \cdot y - \sin(\phi)/x$
""")

# Настройки параметров в интерфейсе
b_radius = st.slider("Радиус кривизны в вершине (b)", 0.5, 5.0, 1.0, 0.1)
beta = st.slider("Параметр формы (Bond number / β)", 0.1, 1.0, 0.5, 0.05)
ds = st.slider("Шаг интегрирования (ds)", 0.01, 0.1, 0.02, 0.01)

# Кнопка расчета
if st.button("Рассчитать контур капли"):
    # Почетные условия (стартуем из вершины x=0, y=0, phi=0)
    # Добавляем микро-сдвиг для избежания деления на 0
    x = 1e-6
    y = 0.0
    phi = 0.0
    
    x_coords = []
    y_coords = []
    
    # Функция производных
    def derivatives(x_v, y_v, phi_v):
        d_x = np.cos(phi_v)
        d_y = np.sin(phi_v)
        
        # Раскрытие неопределенности в вершине по Лопиталю (x -> 0)
        sin_x_term = 1.0 if x_v < 1e-4 else np.sin(phi_v) / x_v
        d_phi = 2.0 + (beta * y_v) - sin_x_term
        
        return d_x, d_y, d_phi

    # Цикл интегрирования Рунге-Кутты 4-го порядка
    for step in range(1000):
        # Сохраняем симметричные точки
        x_coords.append(x)
        y_coords.append(y)
        
        # Шаг RK4
        kx1, ky1, kphi1 = derivatives(x, y, phi)
        kx2, ky2, kphi2 = derivatives(x + 0.5*ds*kx1, y + 0.5*ds*ky1, phi + 0.5*ds*kphi1)
        kx3, ky3, kphi3 = derivatives(x + 0.5*ds*kx2, y + 0.5*ds*ky2, phi + 0.5*ds*kphi2)
        kx4, ky4, kphi4 = derivatives(x + ds*kx3, y + ds*ky3, phi + ds*kphi4)
        
        x += (ds / 6.0) * (kx1 + 2.0*kx2 + 2.0*kx3 + kx4)
        y += (ds / 6.0) * (ky1 + 2.0*ky2 + 2.0*ky3 + ky4)
        phi += (ds / 6.0) * (kphi1 + 2.0*kphi2 + 2.0*kphi3 + kphi4)
        
        # Условие останова (когда контур закручивается обратно к оси или уходит вверх)
        if phi > np.pi * 1.0 or x < 0 or np.isnan(x) or np.isnan(y):
            break

    # Отрисовка полученного контура капли
    if len(x_coords) > 0:
        x_pts = np.array(x_coords)
        y_pts = np.array(y_coords)
        
        # Зеркально отражаем левую и правую стороны
        total_x = np.concatenate([-x_pts[::-1], x_pts])
        total_y = np.concatenate([y_pts[::-1], y_pts])
        
        # Строим график в Plotly
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=total_x, y=-total_y, # минус y, чтобы капля висела вниз
            mode='lines',
            line=dict(color='deepskyblue', width=3),
            fill='toself',
            fillcolor='rgba(135, 206, 250, 0.3)'
        ))
        
        fig.update_layout(
            title="Профиль static капли (Расчет Python RK4)",
            xaxis=dict(range=[-3, 3], scaleanchor="y", scaleratio=1),
            yaxis=dict(range=[-4, 0.5]),
            width=500, height=500,
            template="plotly_dark"
        )
        st.plotly_chart(fig)
        st.success(f"Контур успешно рассчитан! Количество точек: {len(x_coords)}")
    else:
        st.error("Ошибка: Метод Рунге-Кутты разошелся, массив точек пуст.")
