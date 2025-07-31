const WEATHER_ROOT = 'http://127.0.0.1:8000/api/';
async function g(p) { const r = await fetch(WEATHER_ROOT + p); return r.json(); }

window.API = {
    BASE_URL: 'http://127.0.0.1:8000/api',
    token: localStorage.getItem('jwt') || null,

    async _fetch(endpoint, opts = {}) {
        if (this.token) {
            opts.headers = { ...opts.headers, 'Authorization': `Bearer ${this.token}` };
        }
        if (opts.body && !(opts.body instanceof FormData)) {
            opts.headers = { ...opts.headers, 'Content-Type': 'application/json' };
        }

        const response = await fetch(`${this.BASE_URL}${endpoint}`, opts);
        const data = await response.json().catch(() => response.text());

        if (!response.ok) {
            throw data;
        }
        return data;
    },

    login: async function(username, password) {
        const data = await this._fetch('/auth/login/', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        this.token = data.access;
        localStorage.setItem('jwt', this.token);
        return data;
    },

    logout: function() {
        this.token = null;
        localStorage.removeItem('jwt');
    },
    getEvents: async function() {
        const data = await this._fetch('/events/?format=json');
        return Array.isArray(data) ? data : data.results || [];
    },

    createEvent: function(body) {
        return this._fetch('/events/?format=json', { method: 'POST', body: JSON.stringify(body) });
    },

    getMonitoringPoints: async function() {
        const data = await this._fetch('/puntos-monitoreo/?format=json');
        return Array.isArray(data) ? data : data.results || [];
    },
    
    createMonitoringPoint: function(body) {
        return this._fetch('/puntos-monitoreo/?format=json', { method: 'POST', body: JSON.stringify(body) });
    }
};

window.addEventListener('DOMContentLoaded', async () => {
    console.log('Fetching all application data...');
    try {
        const [summary, hourly, daily, events, points] = await Promise.all([
            g('weather/summary/?format=json').catch(e => {
                console.error('Fallo al cargar el resumen del clima:', e);
                return null;
            }),
            g('weather/?format=json').then(d => d.hourly).catch(e => {
                console.error('Fallo al cargar el clima por hora:', e);
                return null;
            }),
            g('weather/?format=json').then(d => d.daily).catch(e => {
                console.error('Fallo al cargar el clima diario:', e);
                return null;
            }),
            API.getEvents().catch(e => {
                console.warn('Fallo al cargar los eventos iniciales:', e);
                return []; 
            }),
            API.getMonitoringPoints().catch(e => {
                console.warn('Fallo al cargar los puntos iniciales:', e);
                return [];
            })
        ]);

        window.PPP = { summary, hourly, daily };
        window.APIData = { events, points };

        console.log('All data processing finished. Firing ready event.');
        document.dispatchEvent(new Event('ppp-ready'));
    } catch (error) {
        console.error("Error crítico durante la inicialización de datos:", error);
    }
});
