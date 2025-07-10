
let weatherChart = null;

window.addEventListener('DOMContentLoaded', () => {
  const themeSlider = document.getElementById('theme-slider');
  const currentTheme = localStorage.getItem('theme');
  if (currentTheme) {
    document.body.setAttribute('data-theme', currentTheme);
    if (currentTheme === 'dark') themeSlider.checked = true;
  }
  themeSlider.addEventListener('change', () => {
    document.body.setAttribute('data-theme', themeSlider.checked ? 'dark' : 'light');
    localStorage.setItem('theme', themeSlider.checked ? 'dark' : 'light');
  });

  initNavigation();
  document.addEventListener('ppp-ready', () => {
    console.log('Datos PPP listos. Renderizando vistas...');
    renderWeatherView();
    renderScheduleView();
    renderExtrasView();
  });
});

function initNavigation() {
  const navLinks = document.querySelectorAll('.nav-link');
  const views = document.querySelectorAll('.view');
  navLinks.forEach(link => {
    link.addEventListener('click', (event) => {
      event.preventDefault();
      const targetViewId = 'view-' + link.dataset.view;
      navLinks.forEach(nav => nav.classList.remove('active'));
      link.classList.add('active');
      views.forEach(view => view.classList.toggle('active', view.id === targetViewId));
    });
  });
}

function renderWeatherView() {
  if (!window.PPP || !PPP.summary || !PPP.hourly) return;
  
  const currentConditions = PPP.summary.current_conditions;
  const currentHour = new Date().getHours();
  const weatherCode = currentConditions.weather_code ?? 3;
  
  document.getElementById('current-temp').innerText = currentConditions.temperature.toFixed(1);
  document.getElementById('current-desc').innerText = currentConditions.weather_description;
  document.getElementById('now-icon').innerText = getWeatherIconName(weatherCode, currentHour);
  document.getElementById('current-wind').innerText = currentConditions.wind_speed.toFixed(1);
  document.getElementById('current-humidity').innerText = PPP.hourly.humidity[0].toFixed(0);
  
  renderHorizontalForecast();
}

function getWeatherIconName(code, hour) {
    const isDay = hour > 6 && hour < 20;
    switch (code) {
        case 0: return isDay ? 'clear_day' : 'clear_night';
        case 1: 
        case 2: 
            return isDay ? 'partly_cloudy_day' : 'partly_cloudy_night';
        case 3: 
            return 'cloudy';
        case 45: case 48: return 'foggy';
        case 51: case 53: case 55: case 56: case 57: return 'rainy';
        case 61: case 63: case 65: return 'rainy';
        case 66: case 67: return 'weather_snowy';
        case 71: case 73: case 75: case 77: return 'weather_snowy';
        case 80: case 81: case 82: return 'rainy_heavy';
        case 85: case 86: return 'weather_snowy';
        case 95: case 96: case 99: return 'thunderstorm';
        default: return 'cloud';
    }
}

function renderHorizontalForecast() {
    const container = document.getElementById('hourly-scroll-content');
    if (!PPP.hourly || !container) return;
    container.innerHTML = '';
    
    for (let i = 0; i < 24; i++) {
        const date = new Date(new Date().getTime() + i * 3600 * 1000);
        const hour = date.getHours();
        const code = PPP.hourly.weather_code ? PPP.hourly.weather_code[i] : 3;
        
        const item = document.createElement('div');
        item.className = 'hour-forecast-item';
        item.innerHTML = `
            <span class="hour">${hour.toString().padStart(2, '0')}</span>
            <span class="material-symbols-outlined weather-icon">${getWeatherIconName(code, hour)}</span>
            <strong class="temp">${PPP.hourly.temperature[i].toFixed(0)}°</strong>
            <div class="details-row">
                <div class="detail-item">
                    <span class="material-symbols-outlined">humidity_percentage</span>
                    <span>${PPP.hourly.humidity[i].toFixed(0)}%</span>
                </div>
            </div>
        `;
        container.appendChild(item);
    }
}

function renderScheduleView() {
    if (!window.PPP || !PPP.hourly) return;
    const bloques = [ { id: "1-2", start: "08:15", end: "09:25" }, { id: "3-4", start: "09:40", end: "10:50" }, { id: "5-6", start: "11:05", end: "12:15" }, { id: "7-8", start: "12:30", end: "13:40" }, { id: "9-10", start: "14:00", end: "15:10" }, { id: "11-12", start: "15:30", end: "16:40" }, { id: "13-14", start: "17:00", end: "18:10" }, { id: "15-16", start: "18:30", end: "19:40" } ];
    const hourlyForecasts = Array.from({ length: 24 }, (_, i) => ({ time: new Date(new Date().getTime() + i * 3600 * 1000), rain: PPP.hourly.precipitation_probability[i] }));

    bloques.forEach(bloque => {
        const [startHour] = bloque.start.split(':').map(Number);
        const [endHour] = bloque.end.split(':').map(Number);
        let maxRain = 0;
        hourlyForecasts.forEach(f => {
            if (f.time.getHours() >= startHour && f.time.getHours() <= endHour) {
                if (f.rain > maxRain) maxRain = f.rain;
            }
        });
        const row = document.querySelector(`.schedule-table tr[data-block="${bloque.id}"]`);
        if (row) row.querySelector('.rain-risk').textContent = `${Math.round(maxRain)}%`;
    });
}

function renderExtrasView() {
    if (!window.PPP || !PPP.hourly) return;
    const slider = document.getElementById('hour-slider-vertical');
    
    document.getElementById('summary-sensation').innerText = `${PPP.hourly.apparent_temperature[0].toFixed(1)}°C`;
    document.getElementById('summary-uv').innerText = Math.max(...PPP.hourly.uv_index).toFixed(1);
    document.getElementById('summary-visib').innerText = `${(Math.max(...PPP.hourly.visibility) / 1000).toFixed(1)} km`;
    const totalPrecip = PPP.hourly.precipitation.reduce((sum, a) => sum + a, 0);
    document.getElementById('summary-precip').innerText = `${totalPrecip.toFixed(1)} mm`;

    const updateDetailCard = (sliderValue) => {
        const idx = 23 - parseInt(sliderValue);
        const time = new Date(new Date().getTime() + idx * 3600 * 1000);
        document.getElementById('detail-time').innerText = `${time.getHours().toString().padStart(2, '0')}:00 Detalle`;
        document.getElementById('detail-temp').innerText = `${PPP.hourly.temperature[idx].toFixed(1)}°C`;
        document.getElementById('detail-hum').innerText = PPP.hourly.humidity[idx].toFixed(0);
        document.getElementById('detail-uv').innerText = PPP.hourly.uv_index[idx].toFixed(1);
        document.getElementById('detail-rain').innerText = PPP.hourly.precipitation_probability[idx].toFixed(0);
        document.getElementById('detail-rain-mm').innerText = PPP.hourly.precipitation[idx].toFixed(1);
        document.getElementById('detail-clouds').innerText = PPP.hourly.cloud_cover[idx].toFixed(0);
        document.getElementById('detail-sensation').innerText = `${PPP.hourly.apparent_temperature[idx].toFixed(1)}°C`;
    };

    slider.addEventListener('input', (e) => updateDetailCard(e.target.value));
    updateDetailCard(slider.value);

    const nowForLabels = new Date();
    const labels = Array.from({ length: 24 }, (_, i) => {
        const date = new Date(nowForLabels.getTime() + i * 3600 * 1000);
        return date.getHours().toString().padStart(2, '0') + ':00';
    });

    const ctx = document.getElementById('weather-chart').getContext('2d');
    if (weatherChart) weatherChart.destroy();

    weatherChart = new Chart(ctx, {
        type: 'line',
        data: { labels: labels, datasets: [ { label: 'Temperatura', data: PPP.hourly.temperature, borderColor: 'rgba(255, 121, 198, 1)', backgroundColor: 'rgba(255, 121, 198, 0.2)', yAxisID: 'y_temp', tension: 0.4, fill: true, }, { label: 'Lluvia %', data: PPP.hourly.precipitation_probability, borderColor: 'rgba(139, 233, 253, 1)', backgroundColor: 'rgba(139, 233, 253, 0.2)', yAxisID: 'y_rain', stepped: true, } ] },
        options: {
            responsive: true, maintainAspectRatio: false, interaction: { mode: 'index', intersect: false },
            scales: { y_temp: { position: 'left', grid: { drawOnChartArea: false }, ticks: { color: '#f8f8f2' } }, y_rain: { position: 'right', max: 100, min: 0, ticks: { color: '#f8f8f2' } } },
            plugins: { legend: { labels: { color: '#f8f8f2' } } },
            onClick: (event, elements) => {
                if (elements.length > 0) {
                    const index = elements[0].index;
                    slider.value = 23 - index;
                    updateDetailCard(slider.value);
                }
            }
        }
    });
}