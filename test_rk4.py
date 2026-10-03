import streamlit as st

st.set_page_config(page_title="Microscope Optical Master", layout="centered")
st.title("🔬 Окуляр вимірювального мікроскопа")

st.markdown("""
### Лабораторна оптична система:
1. **Ціна поділки шкали:** строго **$0.1$ мм** (кожна маленька риска — $0.1$ мм, велика — $0.5$ мм).
2. **Автентична механіка:** Запустіть дозатор рідини. Вимірювальний візир плавно 
   переміщується ручками тонкої наводки прямо під окуляром мікроскопа.
""")

if "app_running" not in st.session_state:
    st.session_state.app_running = False

col_b1, col_b2 = st.columns(2)
with col_b1:
    if st.button("💧 Відкрити затвор дозатора рідини", use_container_width=True):
        st.session_state.app_running = True
with col_b2:
    if st.button("🛑 Перекрити кран", use_container_width=True):
        st.session_state.app_running = False
        st.rerun()

if st.session_state.app_running:
    svg_html = """
    <div style="background: #161616; padding: 20px; border-radius: 16px; width: 420px; margin: 0 auto; box-shadow: 0 8px 32px rgba(0,0,0,0.6); border: 1px solid #333; text-align: center;">
        
        <!-- ОКУЛЯР ОПТИЧНОГО МІКРОСКОПА -->
        <svg id="drop-container" width="400" height="400" viewBox="0 0 400 400" style="background: #010401; border: 4px solid #555; border-radius: 50%; margin-bottom: 15px;">
            
            <!-- Скляний капіляр знизу (Діаметр 2.0 мм = 200px у новому масштабі, тобто радіус 100px від центру) -->
            <rect x="95" y="340" width="210" height="60" fill="#333" opacity="0.85" />
            <rect x="100" y="340" width="200" height="60" fill="#010401" />
            <line x1="100" y1="340" x2="300" y2="340" stroke="#666" stroke-width="3" />

            <!-- Контур краплі (росте ВГОРУ) -->
            <path id="fluid-drop" d="" fill="rgba(100, 210, 255, 0.43)" stroke="lightskyblue" stroke-width="2.5" stroke-linejoin="round" />
            
            <!-- Летяча сфера відриву -->
            <circle id="flying-ball" cx="200" cy="500" r="0" fill="rgba(100, 210, 255, 0.55)" stroke="lightskyblue" stroke-width="2" style="display: none;" />

            <!-- ВИМІРЮВАЛЬНА СІТКА ОКУЛЯРНОГО МІКРОМЕТРА -->
            <g id="microscope-grid">
                <line id="grid-line-y" x1="0" y1="200" x2="400" y2="200" stroke="rgba(255,0,0,0.85)" stroke-width="1.5" />
                <line id="grid-line-x" x1="200" y1="0" x2="200" y2="400" stroke="rgba(255,0,0,0.85)" stroke-width="1.5" />
                <g id="grid-ticks"></g>
            </g>
        </svg>

        <!-- МЕХАНІЧНІ ГВИНТИ ТОНКОЇ НАВОДКИ ШКАЛИ -->
        <div style="color: #ccc; font-family: sans-serif; font-size: 13px; text-align: left; padding: 0 10px;">
            <div style="margin-bottom: 12px;">
                <label>⚙️ Гвинт X (горизонтальний зсув візира): <span id="val-x">0.00</span> мм</label>
                <input type="range" id="slider-x" min="-2.0" max="2.0" step="0.01" value="0" style="width: 100%; margin-top: 5px; accent-color: red;">
            </div>
            <div>
                <label>⚙️ Гвинт Y (вертикальний зсув візира): <span id="val-y">0.00</span> мм</label>
                <input type="range" id="slider-y" min="-4.0" max="4.0" step="0.01" value="0" style="width: 100%; margin-top: 5px; accent-color: red;">
            </div>
        </div>
    </div>
    <script>
        if (window.animFrameId) { cancelAnimationFrame(window.animFrameId); }
        const pathDrop = document.getElementById('fluid-drop');
        const ballFly = document.getElementById('flying-ball');
        const lineX = document.getElementById('grid-line-x');
        const lineY = document.getElementById('grid-line-y');
        const ticksContainer = document.getElementById('grid-ticks');
        const sliderX = document.getElementById('slider-x');
        const sliderY = document.getElementById('slider-y');
        const valX = document.getElementById('val-x');
        const valY = document.getElementById('val-y');

        function updateMicroscopeGrid() {
            let x_mm = parseFloat(sliderX.value);
            let y_mm = parseFloat(sliderY.value);
            valX.innerText = x_mm.toFixed(2);
            valY.innerText = y_mm.toFixed(2);

            let px_x = 200 + (x_mm * 100); 
            let px_y = 200 - (y_mm * 100);

            lineX.setAttribute('x1', px_x); lineX.setAttribute('x2', px_x);
            lineY.setAttribute('y1', px_y); lineY.setAttribute('y2', px_y);

            let html = '';
            for (let i = -200; i <= 200; i += 10) {
                let is_major = (i % 50 === 0); 
                let t_len = is_major ? 14 : 7;
                html += `<line x1="${px_x + i}" y1="${px_y - t_len}" x2="${px_x + i}" y2="${px_y + t_len}" stroke="rgba(255,0,0,0.85)" stroke-width="${is_major ? 1.2 : 0.8}" />`;
            }
            ticksContainer.innerHTML = html;
        }
        sliderX.addEventListener('input', updateMicroscopeGrid);
        sliderY.addEventListener('input', updateMicroscopeGrid);
        updateMicroscopeGrid();

        function generatePearContour(progress) {
            let points = []; let steps = 140; 
            let totalH = 2.0 + (progress * 148.0); 
            let baseR = 100;                     
            let maxBulbR = baseR + (progress * 55); 
            let neckR = baseR - (Math.pow(progress, 2.0) * 8.0); 

            for (let i = 0; i <= steps; i++) {
                let t = i / steps; let y = 340 - (t * totalH); let r = baseR;
                if (t < 0.35) {
                    let k = t / 0.35; let smooth = 0.5 - 0.5 * Math.cos(k * Math.PI);
                    r = baseR - (baseR - neckR) * smooth;
                } else if (t < 0.75) {
                    let k = (t - 0.35) / 0.40; let smooth = Math.sin(k * Math.PI / 2);
                    r = neckR + (maxBulbR - neckR) * smooth;
                } else {
                    let k = (t - 0.75) / 0.25; r = maxBulbR * Math.sqrt(Math.max(0.0, 1.0 - k * k));
                }
                points.push({x: 200 - r, y: y});
            }
            let dPath = `M 100,340`;
            for (let pt of points) dPath += ` L ${pt.x.toFixed(1)},${pt.y.toFixed(1)}`;
            for (let i = points.length - 1; i >= 0; i--) {
                dPath += ` L ${(200 + (200 - points[i].x)).toFixed(1)},${points[i].y.toFixed(1)}`;
            }
            dPath += ` Z`;
            return {d: dPath, h: totalH, r: maxBulbR};
        }

        let startTime = null; const loopDuration = 4800; 
        function animationFrame(timestamp) {
            if (!startTime) startTime = timestamp;
            let elapsed = timestamp - startTime;
            let p = (elapsed % loopDuration) / loopDuration;

            if (p <= 0.82) {
                ballFly.style.display = 'none'; pathDrop.style.display = 'block';
                let progress = p / 0.82; let contour = generatePearContour(progress);
                pathDrop.setAttribute('d', contour.d);
                window.lastH = contour.h; window.lastR = contour.r;
            } else if (p <= 0.88) {
                let snapProgress = (p - 0.82) / 0.06;
                let stretchH = window.lastH + (snapProgress * 25);
                let snapNeckR = (100 - (0.82 * 8.0)) * (1.0 - snapProgress) + 6.0 * snapProgress;
                let points = [];
                for (let i = 0; i <= 140; i++) {
                    let t = i / 140; let y = 340 - (t * stretchH); let r = 100;
                    if (t < 0.45) {
                        let k = t / 0.45; let smooth = 0.5 - 0.5 * Math.cos(k * Math.PI);
                        r = 100 - (100 - snapNeckR) * smooth;
                    } else if (t < 0.75) {
                        let k = (t - 0.45) / 0.30; r = snapNeckR + (window.lastR * 1.02 - snapNeckR) * Math.sin(k * Math.PI / 2);
                    } else {
                        let k = (t - 0.75) / 0.25; r = window.lastR * 1.02 * Math.sqrt(Math.max(0.0, 1.0 - k * k));
                    }
                    points.push({x: 200 - r, y: y});
                }
                let dPath = `M 100,340`;
                for (let pt of points) dPath += ` L ${pt.x.toFixed(1)},${pt.y.toFixed(1)}`;
                for (let i = points.length - 1; i >= 0; i--) {
                    dPath += ` L ${(200 + (200 - points[i].x)).toFixed(1)},${points[i].y.toFixed(1)}`;
                }
                dPath += ` Z`; pathDrop.setAttribute('d', dPath);
            } else if (p <= 0.96) {
                let fallProgress = (p - 0.88) / 0.08;
                let restH = 12 * (1.0 - fallProgress) + 1.0;
                pathDrop.setAttribute('d', `M 100,340 A 100,${restH} 0 0,1 300,340 Z`);
                ballFly.style.display = 'block';
                let ballRadius = window.lastR * 0.84;
                let startY = 340 - window.lastH - 25;
                let curY = startY - (fallProgress * 320); 
                ballFly.setAttribute('cx', '200'); ballFly.setAttribute('cy', curY); ballFly.setAttribute('r', ballRadius);
            } else {
                ballFly.style.display = 'none';
            }
            window.animFrameId = requestAnimationFrame(animationFrame);
        }
        window.animFrameId = requestAnimationFrame(animationFrame);
    </script>
    """
    st.components.v1.html(svg_html, height=540, scrolling=False)
else:
    st.info("💡 Відкрийте затвор дозатора рідини вище, щоб налаштувати фокус та спостерігати краплю в окулярі.")
