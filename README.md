# 🤖 API de IA - Traducción y Chat

API production-ready para traducción inglés-español y chatbot conversacional usando **LangChain + HuggingFace**.

## 🚀 Características

- ✅ **Traducción automática** inglés → español con 3 estilos diferentes
- ✅ **Chatbot conversacional** usando DialoGPT
- ✅ **Documentación automática** con Swagger/OpenAPI
- ✅ **Validación de datos** con Pydantic
- ✅ **Manejo de errores** robusto
- ✅ **Health checks** incluidos
- ✅ **Logging estructurado**

## 📦 Instalación

```bash
# 1. Clonar/crear el proyecto
mkdir mi-api-ia && cd mi-api-ia

# 2. Crear entorno virtual
python -m venv ai-env
source ai-env/bin/activate  # Linux/Mac
# ai-env\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt
```

## 🏃‍♂️ Ejecutar la API

```bash
# Desarrollo (con hot reload)
python main.py

# O usando uvicorn directamente
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: `http://localhost:8000`

## 📚 Endpoints Disponibles

### 🏠 Información General
- `GET /` - Información básica de la API
- `GET /health` - Estado de la API y modelos
- `GET /docs` - Documentación Swagger interactiva
- `GET /demo` - Ejemplo rápido de traducción

### 🔤 Traducción
```bash
POST /translate
Content-Type: application/json

{
  "texto": "Hello, how are you today?",
  "estilo": "basico"  # "basico", "formal", "creativo"
}
```

**Respuesta:**
```json
{
  "texto_original": "Hello, how are you today?",
  "texto_traducido": "Hola, ¿cómo estás hoy?",
  "estilo_usado": "basico"
}
```

### 💬 Chat
```bash
POST /chat
Content-Type: application/json

{
  "pregunta": "¿Cómo estás?"
}
```

**Respuesta:**
```json
{
  "pregunta": "¿Cómo estás?",
  "respuesta": "¡Hola! Estoy bien, gracias por preguntar."
}
```

## 🧪 Probar la API

### Usando curl:
```bash
# Traducción
curl -X POST "http://localhost:8000/translate" \
     -H "Content-Type: application/json" \
     -d '{"texto": "Good morning!", "estilo": "formal"}'

# Chat
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"pregunta": "¿Qué tal el clima?"}'
```

### Usando la documentación interactiva:
Visita `http://localhost:8000/docs` para probar todos los endpoints desde el navegador.

## 🛠️ Tecnologías Utilizadas

- **FastAPI** - Framework web moderno y rápido
- **LangChain** - Orquestación de LLMs
- **HuggingFace Transformers** - Modelos de IA
- **Pydantic** - Validación de datos
- **Uvicorn** - Servidor ASGI

## 🔧 Modelos Incluidos

1. **Traductor**: `Helsinki-NLP/opus-mt-en-es` - Traducción EN→ES optimizada
2. **Chat**: `microsoft/DialoGPT-small` - Conversación en español

## 🎯 Casos de Uso

- **Traducción automática** para apps multiidioma
- **Chatbots** para atención al cliente
- **Prototipado rápido** de aplicaciones IA
- **APIs de microservicios** especializadas en IA

## 📈 Próximas Mejoras

- [ ] Agregar más idiomas de traducción
- [ ] Implementar sistema RAG (documentos + embeddings)
- [ ] Agregar autenticación JWT
- [ ] Métricas de uso con Prometheus
- [ ] Caché con Redis
- [ ] Deployment con Docker

---

💡 **Nota**: Esta API está optimizada para **demos y desarrollo**. Para producción, considera agregar autenticación, rate limiting y monitoreo avanzado.
