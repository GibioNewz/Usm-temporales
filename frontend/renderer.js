let weatherChart = null;
const switchView = (targetViewId, activeLink) => {
    const views = document.querySelectorAll('.view');
    const navLinks = document.querySelectorAll('.nav-link');
    const sidebarNavLinks = document.querySelectorAll('.sidebar-nav-link');
    const sidebarNav = document.getElementById('sidebar-nav');
    const overlay = document.getElementById('overlay');

    views.forEach(view => view.classList.remove('active'));
    document.getElementById(targetViewId).classList.add('active');

    navLinks.forEach(nav => nav.classList.remove('active'));
    sidebarNavLinks.forEach(nav => nav.classList.remove('active'));

    if (activeLink) {
        activeLink.classList.add('active');
    }
    const correspondingSidebarLink = document.querySelector(`.sidebar-nav-link[data-view="${activeLink?.dataset.view}"]`);
    if(correspondingSidebarLink) {
        correspondingSidebarLink.classList.add('active');
    }

    sidebarNav.classList.remove('active');
    overlay.classList.remove('active');
};


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
    renderForumView();
    if (document.getElementById('view-create-question')) {
        initCreateQuestionView();
    }
    initMapView();
  });
});

function initNavigation() {
  const navLinks = document.querySelectorAll('.nav-link');
  const sidebarNavLinks = document.querySelectorAll('.sidebar-nav-link');
  const sidebarNav = document.getElementById('sidebar-nav');
  const sidebarToggleBtn = document.getElementById('sidebar-toggle-btn');
  const overlay = document.getElementById('overlay');

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
        const body = { nombre: $('#pm-name').value, descripcion: $('#pm-desc').value, latitud: $('#pm-lat').value, longitud: $('#pm-lon').value };
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

function renderForumView() {
  if (!window.API) return;
  
  const $ = sel => document.querySelector(sel);
  const departmentSelect = $('#forum-department');
  const subjectSelect = $('#forum-subject');
  const contentTypeSelect = $('#forum-content-type');
  const searchInput = $('#forum-search');
  const contentContainer = $('#forum-content');
  

  const asignaturasMap = {};
  const departamentosMap = {};

  async function loadAllData() {
    try {
      const deptResponse = await API._fetch('/departamentos/');
      const departamentos = Array.isArray(deptResponse) ? deptResponse : deptResponse.results || [];

      departamentos.forEach(dept => {
        departamentosMap[dept.id] = dept;
      });

      const subjResponse = await API._fetch('/asignaturas/');
      const asignaturas = Array.isArray(subjResponse) ? subjResponse : subjResponse.results || [];

      asignaturas.forEach(asig => {
        if (asig.departamento && departamentosMap[asig.departamento]) {
          asig.departamento_obj = departamentosMap[asig.departamento];
        }
        asignaturasMap[asig.id] = asig;
      });
      
      return true;
    } catch (err) {
      console.error('Error cargando datos iniciales:', err);
      return false;
    }
  }
  
  async function loadDepartments() {
    try {
      departmentSelect.innerHTML = `
        <option value="">Todos los departamentos</option>
        ${Object.values(departamentosMap).map(d => `
          <option value="${d.id}">${d.nombre}</option>
        `).join('')}
      `;
    } catch (err) {
      console.error('Error cargando departamentos:', err);
      departmentSelect.innerHTML = '<option value="">Error al cargar</option>';
    }
  }
  
  async function loadSubjects(departmentId) {
    subjectSelect.disabled = true;
    subjectSelect.innerHTML = '<option value="">Cargando asignaturas...</option>';
    
    try {
      const asignaturas = departmentId 
        ? Object.values(asignaturasMap).filter(a => a.departamento == departmentId)
        : Object.values(asignaturasMap);
      
      subjectSelect.innerHTML = `
        <option value="">Todas las asignaturas</option>
        ${asignaturas.map(s => `
          <option value="${s.id}">${s.nombre}</option>
        `).join('')}
      `;
      subjectSelect.disabled = false;
    } catch (err) {
      console.error('Error cargando asignaturas:', err);
      subjectSelect.innerHTML = '<option value="">Error al cargar</option>';
    }
  }
  
  async function loadForumContent() {
    contentContainer.innerHTML = '<p>Cargando contenido...</p>';
    
    const params = new URLSearchParams();
    const searchText = searchInput.value.trim();
    const departmentId = departmentSelect.value;
    const subjectId = subjectSelect.value;
    const contentType = contentTypeSelect.value;
    
    if (searchText) params.append('buscar', searchText);
    if (departmentId) params.append('departamento', departmentId);
    if (subjectId) params.append('asignatura', subjectId);
    
    try {
      let content = [];
      
      if (contentType === 'answer') {
        const response = await API._fetch(`/respuestas/?${params}`);
        const data = Array.isArray(response) ? response : response.results || [];
        content = data.map(formatAnswer);
      } else {
        const response = await API._fetch(`/preguntas/?${params}`);
        const data = Array.isArray(response) ? response : response.results || [];
        content = data.map(formatQuestion);
      }
      
      contentContainer.innerHTML = content.length 
        ? content.join('') 
        : '<p class="empty">No se encontraron resultados</p>';
    } catch (err) {
      console.error('Error cargando contenido:', err);
      contentContainer.innerHTML = '<p class="error">Error al cargar el contenido</p>';
    }
  }
  
  function formatQuestion(question) {
      const asignatura = asignaturasMap[question.asignatura];
      const departamentoNombre = asignatura?.departamento_obj?.nombre || 'No especificado';
      
      return `
        <div class="forum-item question ${question.esta_resuelta ? 'resuelta' : ''}" data-id="${question.id}">
          <div class="forum-header">
            <h3>${question.titulo}</h3>
            <span>${new Date(question.fecha_creacion).toLocaleString()}</span>
          </div>
          <p>${question.contenido}</p>
          <div class="forum-meta">
            <span>Asignatura: ${asignatura?.nombre || 'No especificada'}</span>
            <span>Departamento: ${departamentoNombre}</span>
            <span>${question.esta_resuelta ? '✅ Resuelta' : '❓ Pendiente'}</span>
          </div>
          <div class="forum-footer">
            <button class="btn btn-secondary toggle-answers-btn" data-id="${question.id}">
              Ver respuestas (${question.total_respuestas || 0})
            </button>
            <button class="btn-reply" data-id="${question.id}">
              <span class="material-symbols-outlined">reply</span> Responder
            </button>
          </div>
          <div class="forum-answers" id="answers-${question.id}"></div>
          <div class="reply-form-container" id="reply-form-${question.id}" style="display:none;">
            <form class="reply-form">
              <textarea placeholder="Escriba su respuesta..." required></textarea>
              <button type="submit" class="btn btn-primary">Enviar al foro</button>
            </form>
          </div>
        </div>
      `;
  }
    
  function formatAnswer(answer) {
    return `
      <div class="forum-item answer ${answer.aceptada ? 'aceptada' : ''}">
        <div class="forum-header">
          <h3>Respuesta de ${answer.nombre_mostrar || 'Anónimo'}</h3>
          <span>${new Date(answer.fecha_creacion).toLocaleString()}</span>
        </div>
        <p>${answer.contenido}</p>
        <div class="forum-meta">
          <span>${answer.aceptada ? '✅ Respuesta aceptada' : ''}</span>
        </div>
      </div>
    `;
  }
  
  async function loadAnswers(questionId, container) {
    container.innerHTML = '<p>Cargando respuestas...</p>';
    
    try {
      const response = await API._fetch(`/respuestas/?pregunta=${questionId}`);
      const data = Array.isArray(response) ? response : response.results || [];
      container.innerHTML = data.length 
        ? data.map(formatAnswer).join('') 
        : '<p class="empty">No hay respuestas aún</p>';
    } catch (err) {
      console.error('Error cargando respuestas:', err);
      container.innerHTML = '<p class="error">Error al cargar respuestas</p>';
    }
  }

  departmentSelect.addEventListener('change', () => {
    loadSubjects(departmentSelect.value);
    loadForumContent();
  });
  
  subjectSelect.addEventListener('change', loadForumContent);
  contentTypeSelect.addEventListener('change', loadForumContent);
  searchInput.addEventListener('input', debounce(loadForumContent, 300));
  
  contentContainer.addEventListener('click', (e) => {
    if (e.target.matches('.btn-reply')) {
        const questionId = e.target.dataset.id;
        const replyFormContainer = $(`#reply-form-${questionId}`);
        replyFormContainer.style.display = replyFormContainer.style.display === 'none' ? 'block' : 'none';
        if (replyFormContainer.style.display === 'block') {
            replyFormContainer.querySelector('textarea').focus();
        }
    } else if (e.target.matches('.toggle-answers-btn')) {
        const questionId = e.target.dataset.id;
        const answersContainer = $(`#answers-${questionId}`);
        if (answersContainer.style.display === 'block') {
            answersContainer.style.display = 'none';
            e.target.innerText = `Ver respuestas (${e.target.dataset.totalRespuestas})`;
        } else {
            answersContainer.style.display = 'block';
            loadAnswers(questionId, answersContainer);
            e.target.innerText = 'Ocultar respuestas';
        }
    }
});
  contentContainer.addEventListener('submit', async (e) => {
    if (e.target.matches('.reply-form')) {
      e.preventDefault();
      const form = e.target;
      const textarea = form.querySelector('textarea');
      const questionId = form.closest('.forum-item').dataset.id;

      if (!questionId) {
        alert('Error: No se pudo encontrar el ID de la pregunta. Por favor, recargue la página.');
        console.error('No se pudo encontrar el ID de la pregunta para enviar la respuesta.');
        return;
      }

      if (!textarea.value.trim()) {
        alert('Por favor, escribe una respuesta.');
        return;
      }


      const body = {
        pregunta: parseInt(questionId, 10), 
        contenido: textarea.value.trim(),
        es_anonima: false 
      };

      try {
        const response = await API._fetch('/respuestas/', {
          method: 'POST',
          body: JSON.stringify(body),
        });

        console.log('Respuesta enviada con éxito:', response);
        const answersContainer = $(`#answers-${questionId}`);
        if (answersContainer.style.display === 'block') {
           loadAnswers(questionId, answersContainer);
        }
      
        textarea.value = '';
        form.closest('.reply-form-container').style.display = 'none';

      } catch (err) {
        console.error('Error al enviar la respuesta:', err);
        alert('Error al enviar la respuesta: ' + (err.message || JSON.stringify(err)));
      }
    }
  });
  $('#btn-create-question').addEventListener('click', (e) => {
    e.preventDefault();
    switchView('view-create-question', null);
  });
  loadAllData().then(success => {
    if (success) {
      loadDepartments();
      loadSubjects();
      loadForumContent();
    }
  });

  function debounce(func, wait) {
    let timeout;
    return (...args) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  }
}
function initCreateQuestionView() {
    const $ = sel => document.querySelector(sel);
    const deptSelect = $('#create-dept-select');
    const subjectSelect = $('#create-subject-select');
    const anonymousCheckbox = $('#question-anonymous');
    const authorNameGroup = $('#author-name-group');
    const questionAuthorInput = $('#question-author');
    const questionTitleInput = $('#question-title');
    const questionContentInput = $('#question-content');
    const showDeptFormBtn = $('#btn-show-dept-form');
    const createDeptBtn = $('#btn-create-dept');
    const showSubjectFormBtn = $('#btn-show-subject-form');
    const createSubjectBtn = $('#btn-show-subject-form');
    const nextStep1Btn = $('#btn-next-step1');
    const prevStep2Btn = $('#btn-prev-step2');
    const nextStep2Btn = $('#btn-next-step2');
    const prevStep3Btn = $('#btn-prev-step3');
    const submitQuestionBtn = $('#btn-submit-question');
    let selectedDeptId = null;
    let selectedSubjectId = null;
    async function loadDepartments() {
        try {
            const response = await API._fetch('/departamentos/');
            const depts = Array.isArray(response) ? response : response.results || [];
            deptSelect.innerHTML = '<option value="">Selecciona un departamento</option>';
            depts.forEach(dept => {
                const option = document.createElement('option');
                option.value = dept.id;
                option.textContent = dept.nombre;
                deptSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error al cargar departamentos:', error);
            deptSelect.innerHTML = '<option value="">Error al cargar</option>';
        }
    }
    async function loadSubjects(deptId) {
        subjectSelect.disabled = !deptId;
        if (!deptId) {
            subjectSelect.innerHTML = '<option value="">Primero selecciona un departamento</option>';
            return;
        }
        
        try {
            const response = await API._fetch(`/asignaturas/?departamento=${deptId}`);
            const subjects = Array.isArray(response) ? response : response.results || [];
            subjectSelect.innerHTML = '<option value="">Selecciona una asignatura</option>';
            subjects.forEach(subject => {
                const option = document.createElement('option');
                option.value = subject.id;
                option.textContent = subject.nombre;
                subjectSelect.appendChild(option);
            });
            subjectSelect.disabled = false;
        } catch (error) {
            console.error('Error al cargar asignaturas:', error);
            subjectSelect.innerHTML = '<option value="">Error al cargar</option>';
        }
    }
    showDeptFormBtn.addEventListener('click', () => {
        $('#create-dept-form').style.display = 'block';
    });
    
    showSubjectFormBtn.addEventListener('click', () => {
        $('#create-subject-form').style.display = 'block';
    });
    createDeptBtn.addEventListener('click', async () => {
        const name = $('#new-dept-name').value;
        const code = $('#new-dept-code').value;
        if (!name || !code) return;
        
        try {
              const newDept = await API._fetch('/departamentos/', {
                  method: 'POST',
                  body: JSON.stringify({ 
                      nombre: name,
                      codigo: code 
                  })
              });
            const option = document.createElement('option');
            option.value = newDept.id;
            option.textContent = newDept.nombre;
            deptSelect.appendChild(option);
            deptSelect.value = newDept.id;
            selectedDeptId = newDept.id;
            $('#create-dept-form').style.display = 'none';
            $('#new-dept-name').value = '';
            nextStep1Btn.disabled = false;
        } catch (error) {
            console.error('Error al crear departamento:', error);
            alert('Error al crear departamento: ' + (error.message || JSON.stringify(error)));
        }
    });
    createSubjectBtn.addEventListener('click', async () => {
        const name = $('#new-subject-name').value;
        const code = $('#new-subject-code').value;
        if (!name || !code || !selectedDeptId) return;
        
        try {
            const newSubject = await API._fetch('/asignaturas/', {
                method: 'POST',
                body: JSON.stringify({ 
                    nombre: name,
                    numero: code,
                    departamento: selectedDeptId 
                })
            });
            const option = document.createElement('option');
            option.value = newSubject.id;
            option.textContent = newSubject.nombre;
            subjectSelect.appendChild(option);
            subjectSelect.value = newSubject.id;
            selectedSubjectId = newSubject.id;
            $('#create-subject-form').style.display = 'none';
            $('#new-subject-name').value = '';
            $('#new-subject-code').value = '';
            nextStep2Btn.disabled = false;
        } catch (error) {
            console.error('Error al crear asignatura:', error);
            alert('Error al crear asignatura: ' + (error.message || JSON.stringify(error)));
        }
    });
    deptSelect.addEventListener('change', () => {
        selectedDeptId = deptSelect.value;
        nextStep1Btn.disabled = !selectedDeptId;
        if (selectedDeptId) loadSubjects(selectedDeptId);
    });
    
    subjectSelect.addEventListener('change', () => {
        selectedSubjectId = subjectSelect.value;
        nextStep2Btn.disabled = !selectedSubjectId;
    });
    
    nextStep1Btn.addEventListener('click', () => {
        $('#step-department').classList.remove('active');
        $('#step-subject').classList.add('active');
    });
    
    prevStep2Btn.addEventListener('click', () => {
        $('#step-subject').classList.remove('active');
        $('#step-department').classList.add('active');
    });
    
    nextStep2Btn.addEventListener('click', () => {
        $('#step-subject').classList.remove('active');
        $('#step-question').classList.add('active');
    });
    
    prevStep3Btn.addEventListener('click', () => {
        $('#step-question').classList.remove('active');
        $('#step-subject').classList.add('active');
    });
    anonymousCheckbox.addEventListener('change', () => {
        authorNameGroup.style.display = anonymousCheckbox.checked ? 'none' : 'block';
        if (anonymousCheckbox.checked) {
            questionAuthorInput.removeAttribute('required');
        } else {
            questionAuthorInput.setAttribute('required', 'required');
        }
    });
    submitQuestionBtn.addEventListener('click', async () => {
        const title = questionTitleInput.value;
        const content = questionContentInput.value;
        const author = anonymousCheckbox.checked ? null : questionAuthorInput.value;
        
        if (!title || !content || (!anonymousCheckbox.checked && !author)) {
            alert('Por favor, completa todos los campos requeridos.');
            return;
        }
        
        try {
            const body = {
                titulo: title,
                contenido: content,
                asignatura: selectedSubjectId,
                autor: author
            };
            
            await API._fetch('/preguntas/', {
                method: 'POST',
                body: JSON.stringify(body)
            });
            
            alert('Pregunta publicada con éxito!');
            switchView('view-forum', null);
        } catch (error) {
            console.error('Error al publicar pregunta:', error);
            alert('Error: ' + (error.message || JSON.stringify(error)));
        }
    });
    loadDepartments();
}
let mapaInicializado = false;

function initMapView() {
    if (mapaInicializado) return; 
    if (!document.getElementById('view-mapa')) return;
    console.log("Inicializando la vista del mapa...");
    mapaInicializado = true;
    const NAME_MAP = window.NAME_MAP;
    const tracker = document.getElementById('tracker'),
        pill = document.getElementById('pill'),
        pillNum = document.getElementById('pill-num'),
        btns = [...document.querySelectorAll('#view-mapa .floor-btn')],
        maps = [...document.querySelectorAll('#view-mapa .floor-map')],
        searchI = document.getElementById('search'),
        roomList = document.getElementById('roomList'),
        banioAscFum = /^(bano|ascensor|fumadores)/i,
        shapeTags = ['rect', 'path', 'polygon', 'circle', 'ellipse', 'polyline'];
    let current = 1,
        zoom = 1,
        minZ = 1, maxZ = 3, stepZ = .25;

    Object.values(NAME_MAP).forEach(n => {
        const opt = document.createElement('option');
        opt.value = n;
        roomList.appendChild(opt);
    });
    Object.keys(NAME_MAP).forEach(id => {
        const opt = document.createElement('option');
        opt.value = id;
        roomList.appendChild(opt);
    });
    const validTerms = [...roomList.options].map(o => o.value.toLowerCase());

    function movePill(btn) {
        pillNum.textContent = btn.textContent;
        pill.style.width = 'auto';
        const w = pill.getBoundingClientRect().width,
            tr = tracker.getBoundingClientRect(),
            br = btn.getBoundingClientRect(),
            left = br.left - tr.left + (br.width - w) / 2;
        pill.style.transform = `translate(${left}px, -50%)`;
    }

    movePill(btns[0]);

    btns.forEach(btn => {
        btn.addEventListener('click', () => {
            const dest = +btn.dataset.floor;
            if (dest === current) return;
            btns.forEach(b => b.classList.toggle('active', b === btn));
            movePill(btn);
            swapMaps(dest);
            current = dest;
            applyZoom();
            applyFilter(activeFilter);
            hideTip();
        });
    });

    function swapMaps(dest) {
        const from = maps.find(m => +m.dataset.floor === current),
            to = maps.find(m => +m.dataset.floor === dest),
            dir = dest > current ? 'slide-up' : 'slide-down';
        to.classList.add('active', dir);
        from.classList.remove('active', 'slide-up', 'slide-down');
        to.addEventListener('animationend', () => to.classList.remove('slide-up', 'slide-down'), { once: true });
    }

    const tToColor = t => `hsla(${240 - (t / 40) * 240}, 90%, 60%, .7)`;

    function colorize(svg) {
        svg.querySelectorAll('[id]').forEach(el => {
            const tag = el.tagName.toLowerCase();
            if (banioAscFum.test(el.id) || !shapeTags.includes(tag)) return;
            const t = +(el.dataset.temp || 0);
            el.style.fill = tToColor(t);
            el.setAttribute('title', `${t} °C`);
        });
    }

    function randomTemps() {
        maps.forEach(f => {
            const svg = f.querySelector('svg');
            if (!svg) return;
            svg.querySelectorAll('[id]').forEach(el => {
                const tag = el.tagName.toLowerCase();
                if (banioAscFum.test(el.id) || !shapeTags.includes(tag)) return;
                el.dataset.temp = (Math.random() * 40).toFixed(1);
            });
            colorize(svg);
        });
    }
    document.getElementById('rand').onclick = randomTemps;

    function applyZoom() {
        const svg = maps.find(m => m.classList.contains('active'))?.querySelector('svg');
        if (svg) svg.style.transform = `scale(${zoom})`;
    }
    document.getElementById('plus').onclick = () => { zoom = Math.min(maxZ, zoom + stepZ); applyZoom() };
    document.getElementById('minus').onclick = () => { zoom = Math.max(minZ, zoom - stepZ); applyZoom() };

    let tip = null;
    function hideTip() { tip?.remove(); tip = null; }

    function showTip(el) {
        hideTip();
        const parentCard = el.closest('.card');
        if (!parentCard) return;

        if (banioAscFum.test(el.id)) return;
        const temp = el.dataset.temp;
        const titulo = NAME_MAP[el.id] ?? el.id;

        tip = document.createElement('div');
        tip.className = 'tooltip';
        tip.textContent = temp ? `${titulo} • ${temp} °C` : titulo;
        
        parentCard.appendChild(tip);

        const r = el.getBoundingClientRect();
        const parentRect = parentCard.getBoundingClientRect();
        tip.style.left = `${r.left - parentRect.left + r.width / 2}px`;
        tip.style.top = `${r.top - parentRect.top}px`;
    }

    let activeFilter = 'reset';
    function applyFilter(cat) {
        activeFilter = cat;
        const svg = maps.find(m => m.classList.contains('active'))?.querySelector('svg');
        if (!svg) return;
        svg.querySelectorAll(shapeTags.join(',')).forEach(el => {
            const id = el.id.toLowerCase();
            if (cat === 'reset') { el.style.opacity = '.85' }
            else {
                const match = (cat === 'bano') ? /^bano/i.test(id)
                    : (cat === 'ascensor') ? /^ascensor/i.test(id)
                    : (cat === 'fumadores') ? /^fumadores/i.test(id) : false;
                el.style.opacity = match ? '1' : '.15';
            }
        });
    }
    document.querySelectorAll('#view-mapa .filter-btn').forEach(b => b.onclick = () => applyFilter(b.dataset.cat));

    searchI.addEventListener('keydown', e => {
        if (e.key !== 'Enter') return;
        const q = searchI.value.trim().toLowerCase();
        if (!validTerms.includes(q)) {
            alert('Sala no encontrada'); return;
        }
        findAndShow(q);
    });

    async function findAndShow(query) {
        for (const m of maps) {
            const svg = m.querySelector('svg');
            if (!svg) continue;
            for (const el of svg.querySelectorAll('[id]')) {
                const id = el.id, name = (NAME_MAP[id] ?? '').toLowerCase();
                if (id.toLowerCase() === query || name === query) {
                    const floor = +m.dataset.floor;
                    if (floor !== current) {
                        btns[floor - 1].click();
                        await new Promise(r => setTimeout(r, 400));
                    }
                    setTimeout(() => showTip(el), 50);
                    return;
                }
            }
        }
    }

    const files = { 1: './piso1.svg', 2: './piso2.svg', 3: './piso3.svg', 4: './piso4.svg' };
    Promise.all(maps.map(async m => {
        try {
            const raw = await (await fetch(files[m.dataset.floor])).text();
            m.innerHTML = raw.replace(/<script[\s\S]*?<\/script>/ig, '');
            const svg = m.querySelector('svg');
            svg.addEventListener('click', e => {
                const el = e.target.closest('[id]');
                if (el) showTip(el);
            });
            svg.addEventListener('click', (e) => {
                if (e.target.tagName.toLowerCase() === 'svg') {
                    hideTip();
                }
            }, true);
        } catch(e) { 
            m.textContent = 'Error: No se pudo cargar el archivo del mapa. Asegúrate de que el archivo ' + files[m.dataset.floor] + ' exista.';
            console.error(e);
        }
    })).then(randomTemps);
}