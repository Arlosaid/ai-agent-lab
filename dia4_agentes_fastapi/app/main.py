"""
Día 4: Integración de Agentes IA en FastAPI
Aplicación production-ready con herramientas reales
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Modelos y endpoints se importarán aquí
from app.models import AgentRequest, AgentResponse, HealthResponse
from app.agent_service import AgentService

# Variables globales para servicios
agent_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo del ciclo de vida de la aplicación"""
    global agent_service
    
    # Startup
    logger.info("[STARTUP] Iniciando aplicación de Agentes IA...")
    try:
        agent_service = AgentService()
        await agent_service.initialize()
        logger.info("[SUCCESS] Servicios de agentes inicializados correctamente")
    except Exception as e:
        logger.error(f"[ERROR] Error inicializando servicios: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("[SHUTDOWN] Cerrando aplicación...")
    if agent_service:
        await agent_service.cleanup()
    logger.info("[SUCCESS] Aplicación cerrada correctamente")

# Crear aplicación FastAPI
app = FastAPI(
    title="Agentes IA - Día 4",
    description="Integración de agentes IA con herramientas reales en FastAPI",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=dict)
async def root():
    """Endpoint raíz"""
    return {
        "message": "[AI AGENTS] API de Agentes IA - Día 4",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check detallado"""
    try:
        # Verificar estado del agente
        agent_status = await agent_service.health_check() if agent_service else False
        
        status = "healthy" if agent_status else "unhealthy"
        
        return HealthResponse(
            status=status,
            timestamp=datetime.now(),
            services={
                "agent_service": agent_status,
                "tools": agent_service.get_tools_status() if agent_service else {}
            }
        )
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.post("/agent/query", response_model=AgentResponse)
async def query_agent(request: AgentRequest):
    """Procesar consulta con el agente IA"""
    try:
        logger.info(f"[REQUEST] Nueva consulta: {request.query[:100]}...")
        
        if not agent_service:
            raise HTTPException(status_code=503, detail="Agent service not available")
        
        response = await agent_service.process_query(
            query=request.query,
            context=request.context,
            tools=request.tools
        )
        
        logger.info(f"[RESPONSE] Respuesta generada en {response.processing_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error procesando consulta: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/tools", response_model=dict)
async def get_available_tools():
    """Obtener herramientas disponibles"""
    try:
        if not agent_service:
            raise HTTPException(status_code=503, detail="Agent service not available")
        
        tools = agent_service.get_available_tools()
        return {
            "tools": tools,
            "count": len(tools),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error obteniendo herramientas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 