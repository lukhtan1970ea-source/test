import streamlit as st

st.set_page_config(page_title="Microscope Mirror Master Test", layout="centered")
st.title("🔬 Тест окуляра мікроскопа (Перевернутий RK4 + Шкала)")

st.markdown("""
### Стенд фінальної збірки:
1. **До гори дрыгом:** Капіляр закріплено знизу, крапля наливається та летить строго **вгору**.
2. **Вимірювальна шкала:** Червоне перехрестя з ризиками плавно рухається за допомогою слайдерів.
""")

# БОКОВА ПАНЕЛЬ КЕРУВАННЯ ШКАЛОЮ
st.sidebar.header("🎛️ Рухома шкала візира")
mic_x = st.sidebar.slider("Зсув шкали по горизонталі X (мм)", -2.0, 2.0, 0.0, 0.05)
mic_y = st.sidebar.slider("Зсув шкали по вертикалі Y (мм)", -4.0, 4.0, 0.0, 0.05)

# Перерахунок міліметрів у масштабні пікселі (1 мм = 50 пікселів)
svg_mic_x = 200 + (mic_x * 50)
svg_mic_y = 200 - (mic_y * 50)

# Генеруємо червоні ризики шкали мікроскопа
ticks_html = ""
for i in range(-200, 201, 10):
    t_len = 14 if i % 50 == 0 else 7
    ticks_html += f'<line x1="{svg_mic_x + i}" y1="{svg_mic_y - t_len}" x2="{svg_mic_x + i}" y2="{svg_mic_y + t_len}" stroke="red" stroke-width="1" />'

# КНОПКА ЗАПУСКА
if st.button("🚀 Запустити перевернуту анімацію досліду", use_container_width=True):

    svg_html = f"""
    <div style="background: #111; padding: 15px; border-radius: 12px; width: 430px; margin: 0 auto; box-shadow: 0 4px 20px rgba(0,0,0,0.5);">
        <svg id="drop-container" width="400" height="400" viewBox="0 0 400 400" style="background: #030703; border: 3px solid #333; border-radius: 50%;">
            
            <!-- ПЕРЕВЕРНУТИЙ КАПІЛЯР ЗНИЗУ (Y=350) -->
            <rect x="165" y="350" width="70" height="50" fill="#444" opacity="0.8" />
            <rect x="170" y="350" width="60" height="50" fill="#030703" />
            <line x1="170" y1="350" x2="230" y2="350" stroke="#666" stroke-width="3" />

            <!-- Контур краплі (динамічна груша, що росте ВГОРУ) -->
            <path id="fluid-drop" d="" fill="rgba(100, 210, 255, 0.45)" stroke="lightskyblue" stroke-width="2.5" stroke-linejoin="round" />
            <!-- Летяча сфера відриву (летить вгору) -->
            <circle id="flying-ball" cx="200" cy="500" r="0" fill="rgba(100, 210, 255, 0.55)" stroke="lightskyblue" stroke-width="2" style="display: none;" />

            <!-- РУХОМА ВИМІРЮВАЛЬНА ШКАЛА ПОВЕРХ УСЬОГО -->
            <line x1="0" y1="{svg_mic_y}" x2="400" y2="{svg_mic_y}" stroke="rgba(255,0,0,0.8)" stroke-width="1.5" />
            <line x1="{svg_mic_x}" y1="0" x2="{svg_mic_x}" y2="400" stroke="rgba(255,0,0,0.8)" stroke-width="1.5" />
            {ticks_html}
        </svg>
    </div>

    <script>
        if (window.animFrameId) {{
            cancelAnimationFrame(window.animFrameId);
        }}

        const pathDrop = document.getElementById('fluid-drop');
        const ballFly = document.getElementById('flying-ball');
        
        function generatePearContour(progress) {{
            let points = [];
            let steps = 140; 
            
            // На старті висота каплі мінімальна, ростемо вгору (віднімаємо від 350)
            let totalH = 0.5 + (progress * 149.5); 
            let baseR = 30;                     
            let maxBulbR = baseR + (progress * 28); 
            let neckR = baseR - (Math.pow(progress, 2.0) * 5.5);   

            for (let i = 0; i <= steps; i++) {{
                let t = i / steps; 
                // ІСПРАВЛЕНО НА ВГОРУ: Координата Y зменшується від 350 до центру
                let y = 350 - (t * totalH);
                let r = baseR;

                if (t < 0.35) {{
                    let k = t / 0.35;
                    let smooth = 0.5 - 0.5 * Math.cos(k * Math.PI);
                    r = baseR - (baseR - neckR) * smooth;
                }} else if (t < 0.75) {{
                    let k = (t - 0.35) / 0.40;
                    let smooth = Math.sin(k * Math.PI / 2);
                    r = neckR + (maxBulbR - neckR) * smooth;
                }} else {{
                    let k = (t - 0.75) / 0.25;
                    r = maxBulbR * Math.sqrt(Math.max(0.0, 1.0 - k * k));
                }}

                points.push({{x: 200 - r, y: y}});
            }}

            let dPath = `M 170,350`;
            for (let pt of points) {{
                dPath += ` L ${pt.x.toFixed(1)},${pt.y.toFixed(1)}`;
            }}
            for (let i = points.length - 1; i >= 0; i--) {{
                let rightX = 200 + (200 - points[i].x);
                dPath += ` L ${rightX.toFixed(1)},${points[i].y.toFixed(1)}`;
            }}
            dPath += ` Z`;
            return {{d: dPath, h: totalH, r: maxBulbR}};
        }

        let startTime = null;
        const loopDuration = 4800; 

        function animationFrame(timestamp) {{
            if (!startTime) startTime = timestamp;
            let elapsed = timestamp - startTime;
            let p = (elapsed % loopDuration) / loopDuration;

            if (p <= 0.82) {{
                ballFly.style.display = 'none';
                pathDrop.style.display = 'block';
                
                let progress = p / 0.82;
                let contour = generatePearContour(progress);
                pathDrop.setAttribute('d', contour.d);
                
                window.lastH = contour.h;
                window.lastR = contour.r;

            }} else if (p <= 0.88) {{
                let snapProgress = (p - 0.82) / 0.06;
                let stretchH = window.lastH + (snapProgress * 25);
                let snapNeckR = (30 - (0.82 * 5.5)) * (1.0 - snapProgress) + 2.5 * snapProgress;

                let points = [];
                for (let i = 0; i <= 140; i++) {{
                    let t = i / 140;
                    let y = 350 - (t * stretchH); // Ростемо вгору
                    let r = 30;

                    if (t < 0.45) {{
                        let k = t / 0.45;
                        let smooth = 0.5 - 0.5 * Math.cos(k * Math.PI);
                        r = 30 - (30 - snapNeckR) * smooth;
                    } else if (t < 0.75) {{
                        let k = (t - 0.45) / 0.30;
                        r = snapNeckR + (window.lastR * 1.02 - snapNeckR) * Math.sin(k * Math.PI / 2);
                    } else {{
                        let k = (t - 0.75) / 0.25;
                        r = window.lastR * 1.02 * Math.sqrt(Math.max(0.0, 1.0 - k * k));
                    }}
                    points.push({{x: 200 - r, y: y}});
                }}

                let dPath = `M 170,350`;
                for (let pt of points) dPath += ` L ${pt.x.toFixed(1)},${pt.y.toFixed(1)}`;
                for (let i = points.length - 1; i >= 0; i--) {{
                    dPath += ` L ${(200 + (200 - points[i].x)).toFixed(1)},${points[i].y.toFixed(1)}`;
                }}
                dPath += ` Z`;
                pathDrop.setAttribute('d', dPath);

            }} else if (p <= 0.96) {{
                let fallProgress = (p - 0.88) / 0.08;
                let restH = 8 * (1.0 - fallProgress) + 1.0;
                // Меніск затягується вгору
                pathDrop.setAttribute('d', `M 170,350 A 30,${restH} 0 0,1 230,350 Z`);
                
                ballFly.style.display = 'block';
                let ballRadius = window.lastR * 0.84;
                let startY = 350 - window.lastH - 25;
                let curY = startY - (fallProgress * 280); // ІСПРАВЛЕНО НА ВГОРУ: віднімаємо координату улітання
                
                ballFly.setAttribute('cx', '200');
                ballFly.setAttribute('cy', curY);
                ballFly.setAttribute('r', ballRadius);
                
            } else {{
                let finalProgress = (p - 0.96) / 0.04;
                // Сфера улітає в стратосферу за межі верхнього кола
                ballFly.setAttribute('cy', 50 - (finalProgress * 150));
            }}

            window.animFrameId = requestAnimationFrame(animationFrame);
        }}
        window.animFrameId = requestAnimationFrame(animationFrame);
    </script>
    """

    st.components.v1.html(svg_html, height=440, scrolling=False)
