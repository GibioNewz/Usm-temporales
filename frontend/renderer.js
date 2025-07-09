window.addEventListener('DOMContentLoaded', () => {
  const base = 'http://127.0.0.1:8000/api/weather/';

  // --- Summary ---
  fetch(base + 'summary/?format=json')
    .then(res => res.json())
    .then(data => {
      document.getElementById('temp').innerText =
        data.current_conditions.temperature.toFixed(1);
      document.getElementById('desc').innerText =
        data.current_conditions.weather_description;
      document.getElementById('wind').innerText =
        data.current_conditions.wind_speed.toFixed(1);
      document.getElementById('raw').textContent =
        JSON.stringify(data, null, 2);
    })
    .catch(err => {
      document.getElementById('raw').textContent =
        'Error al cargar summary: ' + err;
    });

  // --- UV ---
  fetch(base + 'uv/?format=json')
    .then(res => res.json())
    .then(data => {
      document.getElementById('uv-index').innerText =
        data.uv_index[0] + ' (próxima hora)';
    })
    .catch(err => {
      document.getElementById('uv-index').innerText =
        'Error UV: ' + err;
    });

  // --- Pronóstico horario (próximas 6 horas) ---
  fetch(base + '?format=json')
    .then(res => res.json())
    .then(data => {
      const temps = data.hourly.temperature;
      const ul = document.getElementById('hourly-list');
      ul.innerHTML = ''; // limpia el “Cargando…”

      const now = new Date();
      for (let i = 0; i < 6; i++) {
        const li = document.createElement('li');
        // +i horas en ms
        const nextHour = new Date(now.getTime() + i * 3600 * 1000);
        const hourStr = nextHour.getHours().toString().padStart(2, '0') + ':00';
        li.innerText = `${hourStr} → ${temps[i].toFixed(1)}°C`;
        ul.appendChild(li);
      }
    })
    .catch(err => {
      document.getElementById('hourly-list').innerHTML =
        '<li>Error hora: ' + err + '</li>';
    });
});
