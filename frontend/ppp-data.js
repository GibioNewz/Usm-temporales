
const ROOT = 'http://192.168.1.81:8000/api/';
async function g(p){ const r=await fetch(ROOT+p); return r.json(); }

window.addEventListener('DOMContentLoaded', async()=>{
  PPP = {
    summary:        await g('weather/summary/?format=json'),
    hourly:         await g('weather/?format=json').then(d=>d.hourly),
    daily:          await g('weather/?format=json').then(d=>d.daily),
    uv:             await g('weather/uv/?format=json'),
    temp:           await g('weather/temperature/?format=json'),
    humidity:       await g('weather/humidity/?format=json'),
    precipitation:  await g('weather/precipitation/?format=json'),
    wind:           await g('weather/wind/?format=json'),
    visibility:     await g('weather/visibility/?format=json'),
    clouds:         await g('weather/clouds/?format=json'),
  };
  document.dispatchEvent(new Event('ppp-ready'));
});
