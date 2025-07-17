# 🚀 Día 4: Integración de Agentes IA en FastAPI

## 📋 Descripción

Aplicación **production-ready** que integra agentes IA con herramientas reales usando FastAPI, LangChain y el patrón ReAct. Evolución del Día 3 de herramientas mock a implementación real.

## 🎯 Características Principales

- ✅ **Agentes IA ReAct** con herramientas reales
- ✅ **API REST robusta** con FastAPI
- ✅ **Búsqueda web real** con DuckDuckGo  
- ✅ **Calculadora avanzada** con Sympy
- ✅ **Traductor real** con Google Translate
- ✅ **Health checks** automáticos
- ✅ **Logging estructurado**
- ✅ **Configuración flexible** con variables de entorno
- ✅ **Documentación automática** de API

## 🏗️ Arquitectura

```
dia4_agentes_fastapi/
├── app/
│   ├── main.py              # FastAPI app principal
│   ├── config.py            # Configuración
│   ├── models.py            # Modelos Pydantic
│   ├── agent_service.py     # Servicio del agente
│   └── tools/               # Herramientas
│       ├── web_search.py    # DuckDuckGo
│       ├── calculator.py    # Sympy
│       └── translator.py    # Google Translate
├── requirements.txt         # Dependencias
├── test_app.py             # Script de pruebas
└── README.md               # Este archivo
```

## ⚡ Instalación Rápida

### 1. Clonar e instalar dependencias

```bash
# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```bash
# Para desarrollo (modo mock)
export DEBUG=true
export LOG_LEVEL=INFO

# Para producción (requiere API key)
# ¡Ya no necesitas API keys! HuggingFace es GRATUITO
export HF_MODEL_NAME=microsoft/DialoGPT-medium
export DEBUG=false
```

### 3. Ejecutar pruebas

```bash
python test_app.py
```

### 4. Levantar servidor

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🌐 Endpoints de la API

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Información básica |
| `/health` | GET | Health check detallado |
| `/agent/query` | POST | Consulta al agente |
| `/agent/tools` | GET | Herramientas disponibles |
| `/docs` | GET | Documentación interactiva |

## 📡 Uso de la API

### Consulta básica

```bash
curl -X POST "http://localhost:8000/agent/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuál es el precio actual del Bitcoin?",
    "context": "Información financiera",
    "tools": ["web_search"]
  }'
```

### Cálculo matemático

```bash
curl -X POST "http://localhost:8000/agent/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Calcula la derivada de x^2 + 3x - 5",
    "tools": ["calculator"]
  }'
```

### Traducción

```bash
curl -X POST "http://localhost:8000/agent/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Traduce 'Hello world' al español",
    "tools": ["translator"]
  }'
```

## 🔧 Configuración Avanzada

### Variables de entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `HF_MODEL_NAME` | Modelo de HuggingFace | `microsoft/DialoGPT-medium` |
| `HF_DEVICE` | Dispositivo para modelo | `auto` |
| `DEBUG` | Modo desarrollo | `true` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |
| `ENABLE_WEB_SEARCH` | Habilitar búsqueda web | `true` |
| `ENABLE_CALCULATOR` | Habilitar calculadora | `true` |
| `ENABLE_TRANSLATOR` | Habilitar traductor | `true` |

### Personalizar herramientas

Para añadir una nueva herramienta:

1. Crear clase que herede de `BaseTool`
2. Implementar métodos `execute()` y `health_check()`
3. Registrarla en `tools/__init__.py`
4. Añadir al `AgentService`

## 🧪 Testing

### Ejecutar todas las pruebas

```bash
python test_app.py
```

### Pruebas específicas

```python
# Probar herramientas individuales
from app.tools.web_search import WebSearchTool
search = WebSearchTool()
result = await search.execute("Python programming")
```

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-XX...",
  "services": {
    "agent_service": true,
    "tools": {
      "web_search": true,
      "calculator": true,
      "translator": true
    }
  }
}
```

### Logs

Los logs se guardan en:
- Consola: `INFO` level
- Archivo: `agent_app.log`

## 🐳 Docker (Opcional)

### Dockerfile básico

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Ejecutar con Docker

```bash
docker build -t dia4-agentes .
docker run -p 8000:8000 -e HF_MODEL_NAME=microsoft/DialoGPT-medium dia4-agentes
```

## 🔍 Troubleshooting

### Problema: Herramientas no disponibles

**Solución:** Verificar conexión a internet y dependencias:
```bash
pip install duckduckgo-search googletrans sympy
```

### Problema: Error de API key

**Solución:** En modo desarrollo, funciona sin API key (modo mock):
```bash
export DEBUG=true
# No necesitas borrar nada - HuggingFace es gratuito!
```

### Problema: Timeout en búsquedas

**Solución:** Ajustar timeouts:
```bash
export REQUEST_TIMEOUT=60
export AGENT_TIMEOUT=120
```

## 📈 Comparación con Día 3

| Aspecto | Día 3 (Mock) | Día 4 (Real) |
|---------|--------------|---------------|
| Web Search | 🎭 Simulado | 🌐 DuckDuckGo real |
| Calculadora | ➕ Básica | 🧮 Sympy avanzado |
| Traductor | 🎭 Mock | 🌍 Google Translate |
| Arquitectura | 📓 Notebook | 🚀 FastAPI API |
| Deployment | 🧪 Local only | 🐳 Docker ready |
| Monitoring | ❌ None | 🩺 Health checks |

## 🚀 Próximos Pasos

### Día 5: RAG + Chatbot Web
- Integrar ChromaDB
- Procesar documentos PDF  
- Interface web con Streamlit
- Chat en tiempo real

### Mejoras Futuras
- [ ] Autenticación JWT
- [ ] Rate limiting
- [ ] Métricas con Prometheus
- [ ] CI/CD pipeline
- [ ] Tests unitarios
- [ ] Cache con Redis

## 💼 Aplicación Profesional

Este proyecto demuestra habilidades clave para:

- **Forward Deployed Engineer**: APIs robustas para clientes
- **AI Full Stack Developer**: Stack completo IA + Backend
- **MLOps Engineer**: Deployment y operación de IA

## 📚 Recursos Adicionales

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Agents](https://python.langchain.com/docs/modules/agents/)
- [Pydantic Models](https://docs.pydantic.dev/)
- [Uvicorn Server](https://www.uvicorn.org/)

## 🤝 Contribuir

1. Fork del repositorio
2. Crear feature branch
3. Implementar mejora
4. Añadir tests
5. Submit pull request

## 📝 Licencia

MIT License - Ver archivo LICENSE para detalles

---

**🎉 ¡Felicitaciones por completar el Día 4!**

Has construido una aplicación IA production-ready con herramientas reales. Estás preparado para implementar soluciones IA en entornos empresariales.

**Próximo:** Día 5 - RAG con documentos PDF + Chatbot web 🚀 