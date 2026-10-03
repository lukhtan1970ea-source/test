import streamlit as st

st.set_page_config(page_title="Perfect Hydrodynamic Drop", layout="centered")
st.title("🔬 Високоточна симуляція капілярної краплі")

st.markdown("""
Повна гідродинамічна анімація наливання та відриву краплі-груші. 
Розрахунок контуру та кінематика польоту перенесені на сторону клієнта (JS/SVG), 
що гарантує **100% плавність без трясіння графіка, завісань та зламів контуру**.
""")

# Ідеальний математичний HTML/JS/SVG рушій каплеїди
svg_html = """
<div style="background: #111; padding: 15px; border-radius: 12px; width: 430px; margin: 0 auto; box-shadow: 0 4px 20px rgba(0,0,0,0.5);">
    <svg id="drop-container" width="400" height="500" viewBox="0 0 400 500" style="background: #050505; border: 2px solid #333; border-radius: 8px;">
        <!-- Скляний капіляр (Трубка діаметром 2 мм фіксована на радіусі 30px від центру) -->
        <rect x="165" y="0" width="70" height="50" fill="#444" opacity="0.8" />
        <rect x="170" y="0" width="60" height="50" fill="#050505" />
        <line x1="170" y1="50" x2="230" y2="50" stroke="#666" stroke-width="3" />

        # Контур краплі (динамічна груша)
        <path id="fluid-drop" d="" fill="rgba(100, 210, 255, 0.45)" stroke="lightskyblue" stroke-width="2.5" stroke-linejoin="round" />
        # Летяча сфера відриву
        <circle id="flying-ball" cx="200" cy="-100" r="0" fill="rgba(100, 210, 255, 0.55)" stroke="lightskyblue" stroke-width="2" style="display: none;" />
    </svg>
</div>

<script>
    const pathDrop = document.getElementById('fluid-drop');
    const ballFly = document.getElementById('flying-ball');
    
    function generatePearContour(progress) {
        let points = [];
        let steps = 140; // Велика кількість точок для ідеальної гладкості
        
        // Фізичні масштабні параметри груші в пікселях
        let totalH = 15 + (progress * 135); // Висота плавно росте до 150px
        let baseR = 30;                     // Радіус капіляра фіксований (30px)
        let maxBulbR = 30 + (progress * 28); // Максимальне пузо розширюється до 58px
        let neckR = 30 - (progress * 5.5);   // Шийка делікатно звужується до 24.5px (вужче капіляра!)

        // Будуємо контур зліва направо через параметричну S-подібну криву
        for (let i = 0; i <= steps; i++) {
            let t = i / steps; // Нормована висота від 0 (капіляр) до 1 (макушка)
            let y = 50 + (t * totalH);
            let r = baseR;

            if (t < 0.35) {
                // ЗОНА ШИЙКИ: Ультра-плавний вогнутий косинусоїдальний перехід від скла до талії
                let k = t / 0.35;
                let smooth = 0.5 - 0.5 * Math.cos(k * Math.PI);
                r = baseR - (baseR - neckR) * smooth;
            } else if (t < 0.75) {
                // ЗОНА ПУЗА: Плавне перетікання від талії шийки до максимального розширення мешочка
                let k = (t - 0.35) / 0.40;
                let smooth = Math.sin(k * Math.PI / 2);
                r = neckR + (maxBulbR - neckR) * smooth;
            } else {
                // ЗОНА МАКУШКИ: Закруглення нижнього купола за строго круговим законом еліпса/кола
                let k = (t - 0.75) / 0.25;
                r = maxBulbR * Math.sqrt(Math.max(0.0, 1.0 - k * k));
            }

            points.push({x: 200 - r, y: y});
        }

        // Дзеркально збираємо праву сторону контуру знизу вгору для замикання фігури
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
    const loopDuration = 4800; // Реалістичний повільний цикл наливання

    function animationFrame(timestamp) {
        if (!startTime) startTime = timestamp;
        let elapsed = timestamp - startTime;
        let p = (elapsed % loopDuration) / loopDuration;

        if (p <= 0.82) {
            // ФАЗА 1: ПЛАВНЕ НАЛИВАННЯ МАКСИМАЛЬНОЇ ГРУШІ
            ballFly.style.display = 'none';
            pathDrop.style.display = 'block';
            
            let progress = p / 0.82;
            let contour = generatePearContour(progress);
            pathDrop.setAttribute('d', contour.d);
            
            // Запам'ятовуємо геометрію для моменту відриву
            window.lastH = contour.h;
            window.lastR = contour.r;

        } else if (p <= 0.88) {
            // ФАЗА 2: МОМЕНТ ВІДРИВУ (Ефект швидкісної камери - Slow Mo нитки)
            let snapProgress = (p - 0.82) / 0.06;
            
            // Ножка капли стрімко витягується вниз і тоншає в ниточку біля самого скла
            let stretchH = window.lastH + (snapProgress * 25);
            let snapNeckR = (30 - (0.82 * 5.5)) * (1.0 - snapProgress) + 2.5 * snapProgress;

            let points = [];
            for (let i = 0; i <= 140; i++) {
                let t = i / 140;
                let y = 50 + (t * stretchH);
                let r = 30;

                if (t < 0.45) {
                    // Формуємо довгу тонку капілярну нитку без злаків
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
            // ФАЗА 3: ВІДРИВ ТА ВІЛЬНЕ ПАДІННЯ СФЕРИ ВНИЗ
            let fallProgress = (p - 0.88) / 0.08;
            
            # Залишок рідини на зрізі трубки миттєво втягується в плоский меніск
            let restH = 8 * (1.0 - fallProgress) + 1.0;
            pathDrop.setAttribute('d', `M 170,50 A 30,${restH} 0 0,0 230,50 Z`);
            
            // Мешочек перетворюється на ідеальну летячу кулю під дією поверхневого натягу
            ballFly.style.display = 'block';
            let ballRadius = window.lastR * 0.84;
            let startY = 50 + window.lastH + 25;
            let curY = startY + (fallProgress * 280); // Стрімке падіння вниз до підлоги
            
            ballFly.setAttribute('cx', '200');
            ballFly.setAttribute('cy', curY);
            ballFly.setAttribute('r', ballRadius);
            
        } else {
            // ФАЗА 4: ПАДІННЯ ЗА МЕЖІ ЕКРАНУ
            let finalProgress = (p - 0.96) / 0.04;
            ballFly.setAttribute('cy', 450 + (finalProgress * 150));
        }

        requestAnimationFrame(animationFrame);
    }
    requestAnimationFrame(animationFrame);
</script>
"""

st.components.v1.html(svg_html, height=530, scrolling=False)
