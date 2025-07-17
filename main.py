# 🚀 API de IA Optimizada - Carga bajo demanda
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Optional
import uvicorn
import logging

# Imports de LangChain y HuggingFace (solo cuando sea necesario)
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 📋 Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🧠 Variables globales para los modelos (inicialmente None)
translator_llm = None
chains = {}

# 📊 Modelos Pydantic
class TranslationRequest(BaseModel):
    texto: str = Field(..., min_length=1, max_length=500, description="Texto en inglés a traducir")
    estilo: Literal["basico", "formal", "creativo"] = Field(default="basico", description="Estilo de traducción")

class TranslationResponse(BaseModel):
    texto_original: str
    texto_traducido: str
    estilo_usado: str

# 🔧 Función para cargar traductor bajo demanda
def load_translator():
    """Carga el modelo de traducción solo cuando se necesita"""
    global translator_llm, chains
    
    if translator_llm is not None:
        return  # Ya está cargado
    
    try:
        logger.info("🤖 Cargando modelo de traducción bajo demanda...")
        
        from langchain_huggingface import HuggingFacePipeline
        from transformers import pipeline
        
        translator_pipeline = pipeline(
            "translation",
            model="Helsinki-NLP/opus-mt-en-es",
            device="cpu"
        )
        translator_llm = HuggingFacePipeline(pipeline=translator_pipeline)
        
        # Crear prompts
        prompt_basico = PromptTemplate(
            input_variables=["texto"],
            template="{texto}"
        )
        
        prompt_formal = PromptTemplate(
            input_variables=["texto"], 
            template="Traduce el siguiente texto al español de manera como si fuera para niños de 5 años: {texto}"
        )
        
        prompt_creativo = PromptTemplate(
            input_variables=["texto"],
            template="Traduce el siguiente texto al español de manera para un animal: {texto}"
        )
        
        # Crear chains
        output_parser = StrOutputParser()
        chains = {
            "basico": prompt_basico | translator_llm | output_parser,
            "formal": prompt_formal | translator_llm | output_parser,
            "creativo": prompt_creativo | translator_llm | output_parser
        }
        
        logger.info("✅ Modelo de traducción cargado exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error cargando modelo de traducción: {str(e)}")
        raise

# 🚀 Crear la aplicación FastAPI
app = FastAPI(
    title="🤖 API de IA Optimizada",
    description="API con carga bajo demanda para traducción inglés-español",
    version="1.0.0"
)

# 🏠 Endpoint raíz
@app.get("/")
async def root():
    return {
        "message": "🤖 API de IA Optimizada activa",
        "status": "ready",
        "endpoints": {
            "traduccion": "/translate",
            "salud": "/health",
            "documentacion": "/docs"
        }
    }

# ❤️ Endpoint de health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "traductor_cargado": translator_llm is not None,
        "memoria_usage": "optimizado - carga bajo demanda"
    }

# 🔤 Endpoint de traducción (con carga bajo demanda)
@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    Traduce texto de inglés a español con diferentes estilos
    El modelo se carga automáticamente en la primera petición
    """
    try:
        # Cargar modelo solo si es necesario
        if translator_llm is None:
            logger.info("⏳ Primera petición - cargando modelo...")
            load_translator()
        
        if request.estilo not in chains:
            raise HTTPException(status_code=400, detail=f"Estilo '{request.estilo}' no válido")
        
        # Ejecutar traducción
        traduccion = chains[request.estilo].invoke({"texto": request.texto})
        
        return TranslationResponse(
            texto_original=request.texto,
            texto_traducido=traduccion,
            estilo_usado=request.estilo
        )
        
    except Exception as e:
        logger.error(f"Error en traducción: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en traducción: {str(e)}")

# 🧪 Endpoint de demo rápido (sin IA)
@app.get("/demo")
async def demo():
    """Demo que funciona sin cargar modelos"""
    return {
        "🎯": "API Demo",
        "status": "funcionando",
        "ejemplo_traduccion": "Usa POST /translate para traducir",
        "modelo_estado": "carga bajo demanda" if translator_llm is None else "cargado"
    }

# 🏃‍♂️ Ejecutar la aplicación
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1", 
        port=8000,  # Puerto estándar
        reload=True
    ) 