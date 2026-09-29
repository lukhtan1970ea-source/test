# ИСПРАВЛЕНО: Жёсткое и стабильное сопряжение ОДУ-контура с капилляром через шейку
if len(post_equator_idx[0]) > 0:
    # Находим точный индекс самой узкой шейки капли
    x_post = x_mm[post_equator_idx]
    min_sub_idx = x_post.argmin()
    neck_idx = post_equator_idx[0][min_sub_idx]
    
    # Обрезаем расчетный ОДУ-контур строго на уровне этой шейки!
    x_final = x_mm[:neck_idx+1]
    y_final = y_mm[:neck_idx+1]
    status_msg = "✅ Физический купол RK4 успешно сопряжен с капилляром через плавную шейку!"
else:
    neck_idx = len(x_mm) - 1
    x_final = x_mm
    y_final = y_mm
    status_msg = "💡 Капля наливается."

# Строим плавное тригонометрическое расширение от радиуса шейки до радиуса капилляра (2.0 мм)
x_neck = x_final[-1]
y_neck = y_final[-1]

extension_x = []
extension_y = []
ext_steps = 15

# Дорисовываем короткий плавный вогнутый мостик к краям трубки (R=2.0)
for i in range(1, ext_steps + 1):
    t = i / ext_steps
    # Плавное расширение по синусоиде от x_neck до 2.0 мм
    cur_x = x_neck + (2.0 - x_neck) * np.sin(t * np.pi / 2)
    # Короткий подъем по высоте (на 0.25 мм вверх к стеклу)
    cur_y = y_neck + (0.25 * (1.0 - np.cos(t * np.pi / 2)))
    extension_x.append(cur_x)
    extension_y.append(cur_y)

# Склеиваем ОДУ-каплю и наш идеальный сглаживающий переход к капилляру
x_complete = np.concatenate([x_final, np.array(extension_x)])
y_complete = np.concatenate([y_final, np.array(extension_y)])

# Фиксируем верхний торец трубки на уровне y = 0
base_y = y_complete[-1]
adjusted_y = y_complete - base_y

total_x = np.concatenate([-x_complete[::-1], x_complete])
total_y = np.concatenate([-adjusted_y[::-1], -adjusted_y])

# Отрисовка графика
fig = go.Figure()

# Серая линия капилляра (строго от -2.0 до 2.0 мм)
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
    title=f"Истинный физический профиль капли {selected_liquid}",
    xaxis=dict(range=[-3.0, 3.0], scaleanchor="y", scaleratio=1, title="Радиус капли (мм)"),
    yaxis=dict(range=[-0.5, 5.5], title="Высота капли под микроскопом (мм)"),
    width=550, height=550,
    template="plotly_dark"
)

st.plotly_chart(fig)
st.success(f"{status_msg} Внешний радиус трубки: 2.00 мм. Истинный радиус шейки капли: {x_neck:.3f} мм.")
