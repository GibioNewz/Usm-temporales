let weatherChart = null;

window.addEventListener('DOMContentLoaded', () => {
  const themeSlider = document.getElementById('theme-slider');
  
  const applyTheme = (theme) => {
    document.body.setAttribute('data-theme', theme);
    if (weatherChart) renderExtrasView();
  };

  const currentTheme = localStorage.getItem('theme') || 'light';
  themeSlider.checked = currentTheme === 'dark';
  applyTheme(currentTheme);

  themeSlider.addEventListener('change', () => {
    const newTheme = themeSlider.checked ? 'dark' : 'light';
    localStorage.setItem('theme', newTheme);
    applyTheme(newTheme);
  });

  initNavigation();
  document.addEventListener('ppp-ready', () => {
    console.log('Data ready. Rendering all views...');
    renderWeatherView();
    renderScheduleView();
    renderExtrasView();
    renderListadosView();
    renderGestionView();
  });
});

function initNavigation() {
  const navLinks = document.querySelectorAll('.nav-link');
  const sidebarNavLinks = document.querySelectorAll('.sidebar-nav-link');
  const views = document.querySelectorAll('.view');
  const sidebarNav = document.getElementById('sidebar-nav');
  const sidebarToggleBtn = document.getElementById('sidebar-toggle-btn');
  const overlay = document.getElementById('overlay');

  const switchView = (targetViewId, activeLink) => {
    views.forEach(view => view.classList.remove('active'));
    document.getElementById(targetViewId).classList.add('active');

    navLinks.forEach(nav => nav.classList.remove('active'));
    sidebarNavLinks.forEach(nav => nav.classList.remove('active'));

    if (activeLink) {
        activeLink.classList.add('active');
    }

    sidebarNav.classList.remove('active');
    overlay.classList.remove('active');
  };

  navLinks.forEach(link => {
    if (link.dataset.view) {
      link.addEventListener('click', (event) => {
        event.preventDefault();
        const targetViewId = 'view-' + link.dataset.view;
        switchView(targetViewId, link);
      });
    }
  });

  sidebarNavLinks.forEach(link => {
    link.addEventListener('click', (event) => {
      event.preventDefault();
      const targetViewId = 'view-' + link.dataset.view;
      switchView(targetViewId, link);
    });
  });

  sidebarToggleBtn.addEventListener('click', () => {
    sidebarNav.classList.toggle('active');
    overlay.classList.toggle('active');
  });

  overlay.addEventListener('click', () => {
    sidebarNav.classList.remove('active');
    overlay.classList.remove('active');
  });

  const initialViewId = 'view-listados';
  document.getElementById(initialViewId).classList.add('active');
  const initialNavLink = document.querySelector(`.nav-link[data-view="listados"]`);
  if (initialNavLink) {
      initialNavLink.classList.add('active');
  }
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
        case 1: case 2: return isDay ? 'partly_cloudy_day' : 'partly_cloudy_night';
        case 3: return 'cloudy';
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
        item.innerHTML = `<span class="hour">${hour.toString().padStart(2, '0')}</span><span class="material-symbols-outlined weather-icon">${getWeatherIconName(code, hour)}</span><strong class="temp">${PPP.hourly.temperature[i].toFixed(0)}°</strong>`;
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
        hourlyForecasts.forEach(f => { if (f.time.getHours() >= startHour && f.time.getHours() <= endHour) { if (f.rain > maxRain) maxRain = f.rain; } });
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
    const totalPrecip = PPP.hourly.precipitation.slice(0, 24).reduce((sum, a) => sum + a, 0);
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
    slider.oninput = (e) => updateDetailCard(e.target.value);
    updateDetailCard(slider.value);
    const nowForLabels = new Date();
    const labels = Array.from({ length: 24 }, (_, i) => { const date = new Date(nowForLabels.getTime() + i * 3600 * 1000); return date.getHours().toString().padStart(2, '0'); });
    const ctx = document.getElementById('weather-chart').getContext('2d');
    if (weatherChart) weatherChart.destroy();
    const isDark = document.body.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#f8f8f2' : '#583c47';
    weatherChart = new Chart(ctx, { type: 'line', data: { labels: labels, datasets: [ { label: 'Temperatura', data: PPP.hourly.temperature.slice(0, 24), borderColor: 'rgba(255, 121, 198, 1)', backgroundColor: 'rgba(255, 121, 198, 0.2)', yAxisID: 'y_temp', tension: 0.4, fill: true, }, { label: 'Lluvia %', data: PPP.hourly.precipitation_probability.slice(0, 24), borderColor: 'rgba(139, 233, 253, 1)', backgroundColor: 'rgba(139, 233, 253, 0.2)', yAxisID: 'y_rain', stepped: true, } ] }, options: { responsive: true, maintainAspectRatio: false, interaction: { mode: 'index', intersect: false }, scales: { x: { ticks: { color: textColor } }, y_temp: { position: 'left', grid: { drawOnChartArea: false }, ticks: { color: textColor } }, y_rain: { position: 'right', max: 100, min: 0, ticks: { color: textColor } } }, plugins: { legend: { labels: { color: textColor } } }, onClick: (_, elements) => { if (elements.length > 0) { slider.value = 23 - elements[0].index; updateDetailCard(slider.value); } } } });
}

function renderListadosView() {
    if (!window.API || !window.APIData) return;
    const $ = sel => document.querySelector(sel);

    const renderEventList = (events) => {
        const ul = $('#ev-list');
        if (!events || events.length === 0) { ul.innerHTML = '<li class="empty">— No hay eventos para mostrar —</li>'; return; }
        const sortedEvents = [...events].sort((a, b) => new Date(a.date) - new Date(b.date));
        ul.innerHTML = sortedEvents.map(ev => `<li><strong>${ev.title}</strong><p>${ev.description || '<em>Sin descripción</em>'}</p><small>Fecha: ${new Date(ev.date).toLocaleString()} &middot; Creado por: ${ev.created_by_username || '—'}</small></li>`).join('');
    };

    const renderPointsList = (points) => {
        const ul = $('#pm-list');
        if (!points || points.length === 0) { ul.innerHTML = '<li class="empty">— No hay puntos para mostrar —</li>'; return; }
        ul.innerHTML = points.map(p => `<li><strong>${p.nombre}</strong><p>${p.descripcion || '<em>Sin descripción</em>'}</p><small>Lat: ${p.latitud} &middot; Lon: ${p.longitud} &middot; Creado por: ${p.creado_por_username || '—'}</small></li>`).join('');
    };
    
    $('#ev-reload').addEventListener('click', async () => {
        try { renderEventList(await API.getEvents()); } catch(err) { renderEventList([]); }
    });
    
    $('#pm-reload').addEventListener('click', async () => {
        try { renderPointsList(await API.getMonitoringPoints()); } catch(err) { renderPointsList([]); }
    });

    renderEventList(APIData.events);
    renderPointsList(APIData.points);
}

function renderGestionView() {
    if (!window.API) return;
    const $ = sel => document.querySelector(sel);

    const showOut = (elem, data, isSuccess = false) => {
        elem.style.display = 'block';
        elem.className = `output-box ${isSuccess ? 'success' : 'error'}`;
        elem.textContent = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
    };
    const updateAuthUI = () => {
        const badge = $('#auth-badge');
        const createEventForm = $('#ev-create');
        const createPointForm = $('#pm-create');
        const isLoggedIn = !!API.token;
        badge.textContent = isLoggedIn ? 'Online' : 'Offline';
        badge.classList.toggle('online', isLoggedIn);
        createEventForm.querySelectorAll('input, textarea, button').forEach(el => el.disabled = !isLoggedIn);
        createPointForm.querySelectorAll('input, textarea, button').forEach(el => el.disabled = !isLoggedIn);
        createEventForm.closest('.card').style.opacity = isLoggedIn ? 1 : 0.6;
        createPointForm.closest('.card').style.opacity = isLoggedIn ? 1 : 0.6;
        createEventForm.closest('.card').style.pointerEvents = isLoggedIn ? 'auto' : 'none';
        createPointForm.closest('.card').style.pointerEvents = isLoggedIn ? 'auto' : 'none';
    };

    $('#form-login').addEventListener('submit', async (e) => {
        e.preventDefault();
        try {
            await API.login($('#l-user').value, $('#l-pass').value);
            showOut($('#auth-out'), '✓ Login correcto', true);
            updateAuthUI();
            $('#ev-reload').click();
            $('#pm-reload').click();
        } catch (err) {
            showOut($('#auth-out'), err);
        }
    });

    $('#btn-logout').addEventListener('click', () => {
        API.logout();
        showOut($('#auth-out'), 'Sesión cerrada', true);
        updateAuthUI();
        $('#ev-reload').click();
        $('#pm-reload').click();
    });

    $('#ev-create').addEventListener('submit', async (e) => {
        e.preventDefault();
        const body = { title: $('#ev-title').value, description: $('#ev-desc').value, date: $('#ev-date').value };
        try {
            const data = await API.createEvent(body);
            showOut($('#ev-create-out'), `✓ ${data.message}`, true);
            $('#ev-reload').click();
            e.target.reset();
        } catch (err) {
            showOut($('#ev-create-out'), err, false);
        }
    });

    $('#pm-create').addEventListener('submit', async (e) => {
        e.preventDefault();
        const body = { nombre: $('#pm-name').value, descripcion: $('#pm-desc').value, latitud: $('#pm-lat').value, longitud: $('#pm-lon').value }; // CORRECCIÓN AQUÍ
        try {
            const data = await API.createMonitoringPoint(body);
            showOut($('#pm-create-out'), `✓ ${data.message || 'Punto creado con éxito.'}`, true);
            $('#pm-reload').click();
            e.target.reset();
        } catch (err) {
            showOut($('#pm-create-out'), err, false);
        }
    });
    updateAuthUI();
}