# 🧪 GUÍA DE STRESS TESTING - EIATube

## Preparación Previa

### 1. Verificar que la aplicación está corriendo

```bash
# Health check
curl http://localhost:8000/health
# Expected: {"status": "ok"}

# Verificar que Redis está disponible
curl http://localhost:8000/docs  # Debe abrir Swagger UI
```

### 2. Preparar métricas base

```bash
# Terminal 1: Monitorear logs
docker compose logs -f backend

# Terminal 2: Monitorear recursos (si estás en Linux)
watch -n 1 'docker stats'

# Terminal 3: Ejecutar stress test (abajo)
```

---

## 🚀 Opción 1: Apache JMeter

### Instalación

```bash
# macOS
brew install jmeter

# Linux
sudo apt-get install jmeter

# Windows
# Descargar de https://jmeter.apache.org/download_jmeter.cgi
```

### Test Plan Básico

1. **Crear Thread Group**
   - Number of Threads (users): 1000
   - Ramp-up Period: 60 segundos
   - Loop Count: 5

2. **Agregar HTTP Sampler para GET /videos**
   - Protocol: http
   - Server Name: localhost
   - Port: 8000
   - Path: /videos?limit=24&offset=0

3. **Agregar HTTP Sampler para POST /videos/{id}/views**
   - Protocol: http
   - Server Name: localhost
   - Port: 8000
   - Path: /videos/1/views
   - Method: POST

4. **View Results Tree**
   - Summary Report
   - Response Time Graph

### Ejecutar desde CLI

```bash
# Ejecutar en modo batch
jmeter -n -t test-plan.jmx -l results.jtl -j jmeter.log

# Ver resultados
jmeter -g results.jtl -o results_html/
```

---

## 🚀 Opción 2: k6 (Grafana)

### Instalación

```bash
# macOS
brew install k6

# Linux
sudo apt-get install k6

# Windows (via Chocolatey)
choco install k6
```

### Script de Test

Crear archivo `test.js`:

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  vus: 1000,                    // 1000 usuarios virtuales
  duration: '5m',               // 5 minutos
  thresholds: {
    'http_req_duration': ['p(95)<500', 'p(99)<1000'],  // 95% requests < 500ms
    'http_req_failed': ['rate<0.1'],                    // Error rate < 0.1%
  },
};

const BASE_URL = 'http://localhost:8000';

export default function () {
  // 60% - GET /videos
  if (__VU % 10 < 6) {
    let res = http.get(`${BASE_URL}/videos?limit=24&offset=0`);
    check(res, {
      'videos status is 200': (r) => r.status === 200,
      'videos response time < 100ms': (r) => r.timings.duration < 100,
      'videos has data': (r) => r.body.length > 0,
    });
  }
  
  // 20% - POST /videos/{id}/views
  else if (__VU % 10 < 8) {
    let res = http.post(`${BASE_URL}/videos/1/views`);
    check(res, {
      'views status is 200': (r) => r.status === 200,
      'views response time < 50ms': (r) => r.timings.duration < 50,
    });
  }
  
  // 10% - GET /batch/videos/info
  else if (__VU % 10 < 9) {
    let payload = JSON.stringify({
      video_ids: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    });
    let params = { headers: { 'Content-Type': 'application/json' } };
    let res = http.post(`${BASE_URL}/batch/videos/info`, payload, params);
    check(res, {
      'batch status is 200': (r) => r.status === 200,
      'batch response time < 100ms': (r) => r.timings.duration < 100,
    });
  }
  
  // 10% - GET /videos/{id}
  else {
    let videoId = Math.floor(Math.random() * 100) + 1;
    let res = http.get(`${BASE_URL}/videos/${videoId}`);
    check(res, {
      'video detail status is 200': (r) => r.status === 200,
      'video detail response time < 100ms': (r) => r.timings.duration < 100,
    });
  }
  
  sleep(Math.random() * 3);  // Sleep 0-3 segundos entre requests
}
```

### Ejecutar Test

```bash
# Ejecutar test
k6 run test.js

# Ejecutar test con salida en HTML
k6 run test.js -o html=results.html

# Ejecutar test con InfluxDB para gráficas en tiempo real
k6 run test.js --out influxdb
```

### Interpretar Resultados

```
     data_received..................: 150 MB   5.0 MB/s
     data_sent.......................: 75 MB    2.5 MB/s
     http_req_duration..............: avg=45ms  p(95)=120ms p(99)=500ms
     http_req_failed................: 0.50%
     http_req_receiving.............: avg=20ms
     http_req_sending...............: avg=5ms
     http_req_waiting...............: avg=20ms
     http_requests..................: 50000  1666.67/s
     iteration_duration.............: avg=3.2s
     iterations......................: 10000  333.33/s
     vus............................: 1000
     vus_max........................: 1000
```

**Métricas importantes:**
- `http_req_duration`: Debe ser <200ms (p95)
- `http_req_failed`: Debe ser <0.5%
- Throughput: Requiere ser >1000 req/s

---

## 🚀 Opción 3: wrk (Herramienta Ligera)

### Instalación

```bash
# macOS
brew install wrk

# Linux (desde fuente)
git clone https://github.com/wg/wrk.git
cd wrk
make
```

### Test Básico

```bash
# Test simple: 12 threads, 400 conexiones, 30 segundos
wrk -t12 -c400 -d30s http://localhost:8000/videos

# Esperado:
# Running 30s test @ http://localhost:8000/videos
#   12 threads and 400 connections
#   Thread Stats   Avg      Stdev     Max   +/- Stdev
#     Latency    45.40ms   25.30ms 200.50ms   85.24%
#     Req/Sec     850.40    100.20     1.20k    90.10%
#   305640 requests in 30.00s, 1.85GB read
#   Socket errors: 250 connect, 0 read, 50 write, 0 timeout
# Requests/sec:  10188.00
# Transfer/sec:    61.70MB
```

### Script Personalizado (Lua)

Crear `script.lua`:

```lua
-- Distribución de carga realista
math.randomseed(os.time())

request = function()
  local path
  local rand = math.random(100)
  
  if rand < 60 then
    -- 60% GET /videos
    path = "/videos?limit=24&offset=0"
  elseif rand < 80 then
    -- 20% GET /videos/{id}
    local id = math.random(1, 100)
    path = "/videos/" .. id
  elseif rand < 90 then
    -- 10% POST /videos/{id}/views
    local id = math.random(1, 100)
    path = "/videos/" .. id .. "/views"
  else
    -- 10% GET /videos/{id}/comments
    local id = math.random(1, 100)
    path = "/videos/" .. id .. "/comments?limit=20"
  end
  
  return wrk.format(nil, path)
end
```

Ejecutar con script:

```bash
wrk -t12 -c400 -d30s -s script.lua http://localhost:8000/
```

---

## 🚀 Opción 4: Locust (Python)

### Instalación

```bash
pip install locust
```

### Script de Test

Crear `locustfile.py`:

```python
from locust import HttpUser, task, between
import random

class EIATubeUser(HttpUser):
    wait_time = between(0.5, 3)  # Esperar 0.5-3 segundos entre requests
    
    def on_start(self):
        # Simular login si es necesario
        pass
    
    @task(60)
    def list_videos(self):
        """60% de las requests"""
        offset = random.randint(0, 10) * 24
        self.client.get(f"/videos?limit=24&offset={offset}")
    
    @task(20)
    def view_video_detail(self):
        """20% de las requests"""
        video_id = random.randint(1, 100)
        self.client.get(f"/videos/{video_id}")
    
    @task(10)
    def increment_views(self):
        """10% de las requests"""
        video_id = random.randint(1, 100)
        self.client.post(f"/videos/{video_id}/views")
    
    @task(10)
    def get_comments(self):
        """10% de las requests"""
        video_id = random.randint(1, 100)
        self.client.get(f"/videos/{video_id}/comments?limit=20")
```

### Ejecutar Locust

```bash
# Modo web (abre interfaz en http://localhost:8089)
locust -f locustfile.py -H http://localhost:8000

# Modo headless (CLI)
locust -f locustfile.py -H http://localhost:8000 \
  --users 1000 \
  --spawn-rate 50 \
  --run-time 5m
```

---

## 📊 Escenarios de Test Recomendados

### Escenario 1: Ramp-up (Aumento Gradual)

```
Usuarios: 1 → 100 → 500 → 1000 → 2000
Duración: 2 min cada nivel

Objetivo: Ver dónde comienza el degradamiento
```

### Escenario 2: Spike (Pico Súbito)

```
Base: 100 usuarios
Spike: 2000 usuarios súbitamente
Duración: 5 minutos

Objetivo: Probar recuperación después de pico
```

### Escenario 3: Sostenido (Carga Constante)

```
Usuarios: 1000 constant
Duración: 1 hora
Monitoreo: Cada 5 minutos

Objetivo: Detectar memory leaks, degradamiento gradual
```

### Escenario 4: Distribuido (Múltiples Endpoints)

```
60% GET /videos
20% GET /videos/{id}
10% POST /videos/{id}/views
10% GET /videos/{id}/comments

Objetivo: Comportamiento realista
```

---

## 📈 Métricas a Monitorear

### Métricas de Aplicación

```bash
# 1. Response Time (Latencia)
- Promedio (Mean): <100ms
- Percentil 95 (p95): <500ms
- Percentil 99 (p99): <1000ms

# 2. Throughput
- Requests/segundo: >1000 req/s

# 3. Error Rate
- % de fallos: <0.5%
- HTTP 500s: 0
- Timeouts: <0.1%

# 4. Conexiones DB
- Activas: <60 (pool size)
- En espera: <10
```

### Métricas de Sistema

```bash
# 1. CPU
- Promedio: 40-60%
- Pico: <80%

# 2. Memoria
- Promedio: 50-60%
- Pico: <80%

# 3. Disco I/O
- Read: <100 MB/s
- Write: <50 MB/s

# 4. Red
- Bandwidth: <1 Gbps
- Packet loss: 0%
```

---

## 🔍 Identificar Cuellos de Botella

### 1. Verificar Cache Hits

```bash
# Mirar logs del backend
docker compose logs -f backend | grep "cache"

# Esperado: 70-80% de requests vienen de cache
```

### 2. Analizar Queries Lentas

```bash
# Conectar a SQLite
sqlite3 eiatube.db

# Ver queries de tiempo real (si tienes logging)
PRAGMA query_only = ON;
SELECT * FROM log WHERE duration > 100;  # Queries >100ms
```

### 3. Monitorear Redis

```bash
# Conectar a Redis
redis-cli

# Ver estadísticas
INFO stats
INFO memory

# Ver comandos lentos
SLOWLOG GET 10
```

---

## 🐛 Troubleshooting

### Problema: Error rate alto (>1%)

**Soluciones:**
1. Revisar logs del backend: `docker compose logs backend`
2. Verificar rate limiting: Reducir usuarios o aumentar límites
3. Revisar conexiones DB: `max_overflow` insuficiente
4. Aumentar timeout: En configuración de HTTP clients

### Problema: Response time muy alto (>1000ms)

**Soluciones:**
1. Verificar CPU: ¿Está al 100%?
2. Verificar memoria: ¿Out of memory?
3. Revisar Redis: ¿Disponible? ¿Lento?
4. Aumentar replicas del backend: Agregar más instancias

### Problema: Conexiones saturadas

**Soluciones:**
```bash
# Aumentar pool size en app/core/database.py
pool_size=40,       # De 20
max_overflow=60,    # De 40

# Reiniciar backend
docker compose restart backend
```

---

## 📋 Checklist Pre-Test

- [ ] Backend corriendo: `curl http://localhost:8000/health`
- [ ] Frontend accesible: `curl http://localhost:5173`
- [ ] Redis disponible: `redis-cli ping`
- [ ] Datos de prueba: Videos/usuarios creados
- [ ] Logs habilitados: `docker compose logs -f`
- [ ] Monitoreo de recursos: Terminal con `docker stats`
- [ ] Herramienta de test descargada: k6, JMeter, etc.
- [ ] Script de test revisado y validado
- [ ] Métricas base documentadas

---

## 📊 Template de Reporte

```markdown
# Reporte de Stress Testing - EIATube

## Configuración del Test
- Herramienta: [k6/JMeter/wrk/Locust]
- Usuarios: [número]
- Duración: [tiempo]
- Ramp-up: [tiempo]
- Endpoint principal: [ruta]

## Resultados

### Métricas de Latencia
- Media: [valor] ms
- P95: [valor] ms
- P99: [valor] ms
- Max: [valor] ms

### Throughput
- Requests/segundo: [valor]
- Bytes/segundo: [valor]

### Errores
- Total requests: [número]
- Failed: [número] ([%])
- HTTP 500s: [número]
- Timeouts: [número]

### Recursos Utilizados
- CPU: [promedio]% - [pico]%
- Memoria: [promedio]% - [pico]%
- Conexiones DB: [máximo]
- Redis hits: [%]

## Hallazgos
- [Análisis de resultados]
- [Cuellos de botella identificados]
- [Recomendaciones de optimización]

## Siguiente Paso
- [Qué optimizar próximo]
```

---

**Buena suerte en el stress test! 🚀**
