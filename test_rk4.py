import streamlit as st

st.set_page_config(page_title="Perfect Hydrodynamic Drop", layout="centered")
st.title("🔬 Високоточна симуляція капілярної краплі")

st.markdown("""
Повна гідродинамічна анімація наливання та відриву краплі-груші. 
Розрахунок контуру та кінематика польоту перенесені на сторону клієнта (JS/SVG), 
що гарантує **100% плавність без трясіння графіка, завісань та зламів контуру**.
""")

# КНОПКА ЗАПУСКУ НА СТОРОНІ PYTHON
if st.button("🚀 Запустити безкінечну анімацію дозатора", use_container_width=True):

    # Ідеальний математичний HTML/JS/SVG рушій каплеїди
    svg_html = """
    <div style="background: #111; padding: 15px; border-radius: 12px; width: 430px; margin: 0 auto; box-shadow: 0 4px 20px rgba(0,0,0,0.5);">
        <svg id="drop-container" width="400" height="500" viewBox="0 0 400 500" style="background: #050505; border: 2px solid #333; border-radius: 8px;">
            <!-- Скляний капіляр (Трубка діаметром 2 мм фіксована на радіусі 30px від центру) -->
            <rect x="165" y="0" width="70" height="50" fill="#444" opacity="0.8" />
            <rect x="170" y="0" width="60" height="50" fill="#050505" />
            <line x1="170" y1="50" x2="230" y2="50" stroke="#666" stroke-width="3" />

            <!-- Контур краплі (динамічна груша) -->
            <path id="fluid-drop" d="" fill="rgba(100, 210, 255, 0.45)" stroke="lightskyblue" stroke-width="2.5" stroke-linejoin="round" />
            <!-- Летяча сфера відриву -->
            <circle id="flying-ball" cx="200" cy="-100" r="0" fill="rgba(100, 210, 255, 0.55)" stroke="lightskyblue" stroke-width="2" style="display: none;" />
        </svg>
    </div>

    <script>
        // Скидаємо та очищуємо старі змінні при кожній ініціалізації вікна
        if (window.animFrameId) {
            cancelAnimationFrame(window.animFrameId);
        }

        const pathDrop = document.getElementById('fluid-drop');
        const ballFly = document.getElementById('flying-ball');
        
        function generatePearContour(progress) {
            let points = [];
            let steps = 140; 
            
            // СТРОГИЙ СТАРТ З ПЛОСКОГО МЕНІСКА:
            // На самому початку (progress=0) висота краплі всього 0.5 пікселя
            let totalH = 0.5 + (progress * 149.5); 
            let baseR = 30;                     
            
            // На старті максимальний радіус точно дорівнює радіусу трубки (крапля ще не роздута)
            let maxBulbR = baseR + (progress * 28); 
            
            // Шийка звужується плавно і тільки на пізніх етапах видовження груші
            let neckR = baseR - (Math.pow(progress, 2.0) * 5.5);   

            for (let i = 0; i <= steps; i++) {
                let t = i / steps; 
                let y = 50 + (t * totalH);
                let r = baseR;

                if (t < 0.35) {
                    let k = t / 0.35;
                    let smooth = 0.5 - 0.5 * Math.cos(k * Math.PI);
                    r = baseR - (baseR - neckR) * smooth;
                } else if (t < 0.75) {
                    let k = (t - 0.35) / 0.40;
                    let smooth = Math.sin(k * Math.PI / 2);
                    r = neckR + (maxBulbR - neckR) * smooth;
                } else {
                    let k = (t - 0.75) / 0.25;
                    r = maxBulbR * Math.sqrt(Math.max(0.0, 1.0 - k * k));
                }

                points.push({x: 200 - r, y: y});
            }

            let dPath = `M 170,50`;
            for (let pt of points) {
                dPath += ` L ${pt.x.toFixed(1)},${pt.y.toFixed(1)}`;
            }
            for (let i = points.length - 1; i >= 0; i--) {
                let rightX = 200 + (200 - points[i].x);
                dPath += ` L ${rightX.toFixed(1)},${points[i].y.toFixed(1)}`;
            }
            dPath += ` Z`;
            return {d: dPath, h: totalH, r: maxBulbR};
        }

        let startTime = null;
        const loopDuration = 4800; 

        function animationFrame(timestamp) {
            if (!startTime) startTime = timestamp;
            let elapsed = timestamp - startTime;
            let p = (elapsed % loopDuration) / loopDuration;

            if (p <= 0.82) {
                ballFly.style.display = 'none';
                pathDrop.style.display = 'block';
                
                let progress = p / 0.82;
                let contour = generatePearContour(progress);
                pathDrop.setAttribute('d', contour.d);
                
                window.lastH = contour.h;
                window.lastR = contour.r;

            } else if (p <= 0.88) {
                let snapProgress = (p - 0.82) / 0.06;
                let stretchH = window.lastH + (snapProgress * 25);
                let snapNeckR = (30 - (0.82 * 5.5)) * (1.0 - snapProgress) + 2.5 * snapProgress;

                let points = [];
                for (let i = 0; i <= 140; i++) {
                    let t = i / 140;
                    let y = 50 + (t * stretchH);
                    let r = 30;

                    if (t < 0.45) {
                        let k = t / 0.45;
                        let smooth = 0.5 - 0.5 * Math.cos(k * Math.PI);
                        r = 30 - (30 - snapNeckR) * smooth;
                    } else if (t < 0.75) {
                        let k = (t - 0.45) / 0.30;
                        r = snapNeckR + (window.lastR * 1.02 - snapNeckR) * Math.sin(k * Math.PI / 2);
                    } else {
                        let k = (t - 0.75) / 0.25;
                        r = window.lastR * 1.02 * Math.sqrt(Math.max(0.0, 1.0 - k * k));
                    }
                    points.push({x: 200 - r, y: y});
                }

                let dPath = `M 170,50`;
                for (let pt of points) dPath += ` L ${pt.x.toFixed(1)},${pt.y.toFixed(1)}`;
                for (let i = points.length - 1; i >= 0; i--) {
                    dPath += ` L ${(200 + (200 - points[i].x)).toFixed(1)},${points[i].y.toFixed(1)}`;
                }
                dPath += ` Z`;
                pathDrop.setAttribute('d', dPath);

            } else if (p <= 0.96) {
                let fallProgress = (p - 0.88) / 0.08;
                let restH = 8 * (1.0 - fallProgress) + 1.0;
                pathDrop.setAttribute('d', `M 170,50 A 30,${restH} 0 0,0 230,50 Z`);
                
                ballFly.style.display = 'block';
                let ballRadius = window.lastR * 0.84;
                let startY = 50 + window.lastH + 25;
                let curY = startY + (fallProgress * 280); 
                
                ballFly.setAttribute('cx', '200');
                ballFly.setAttribute('cy', curY);
                ballFly.setAttribute('r', ballRadius);
                
            } else {
                let finalProgress = (p - 0.96) / 0.04;
                ballFly.setAttribute('cy', 450 + (finalProgress * 150));
            }

            window.animFrameId = requestAnimationFrame(animationFrame);
        }
        window.animFrameId = requestAnimationFrame(animationFrame);
    </script>
    """

    # Викликаємо компонент без помилкового аргументу 'key'
    st.components.v1.html(svg_html, height=530, scrolling=False)
