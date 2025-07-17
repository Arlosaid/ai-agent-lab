"""
Modelos Pydantic para la API de Agentes IA
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ToolType(str, Enum):
    """Tipos de herramientas disponibles"""
    CALCULATOR = "calculator"
    TRANSLATOR = "translator"
    WEB_SEARCH = "web_search"
    SENTIMENT_ANALYZER = "sentiment_analyzer"  # 🎓 NUEVA
    ALL = "all"

class AgentRequest(BaseModel):
    """Modelo para peticiones al agente"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "¿Cuál es el precio actual del Bitcoin en USD?",
                "context": "El usuario quiere información financiera actualizada",
                "tools": ["web_search", "calculator"]
            }
        }
    )
    
    query: str = Field(
        ...,
        description="Consulta del usuario para el agente",
        min_length=1,
        max_length=1000
    )
    
    context: Optional[str] = Field(
        None,
        description="Contexto adicional para la consulta",
        max_length=500
    )
    
    tools: Optional[List[ToolType]] = Field(
        default=[ToolType.ALL],
        description="Herramientas específicas a usar (por defecto: todas)"
    )

class AgentStep(BaseModel):
    """Paso individual del proceso de razonamiento del agente"""
    step_number: int = Field(..., description="Número del paso")
    thought: str = Field(..., description="Pensamiento/razonamiento")
    action: Optional[str] = Field(None, description="Acción tomada")
    tool_used: Optional[str] = Field(None, description="Herramienta utilizada")
    observation: Optional[str] = Field(None, description="Resultado de la acción")
    timestamp: datetime = Field(default_factory=datetime.now)

class AgentResponse(BaseModel):
    """Modelo para respuestas del agente"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "response": "El precio actual del Bitcoin es $43,250 USD...",
                "steps": [
                    {
                        "step_number": 1,
                        "thought": "Necesito buscar el precio actual del Bitcoin",
                        "action": "web_search",
                        "tool_used": "DuckDuckGoSearchRun",
                        "observation": "Bitcoin price: $43,250 USD..."
                    }
                ],
                "tools_used": ["web_search"],
                "processing_time": 2.45,
                "success": True
            }
        }
    )
    
    response: str = Field(..., description="Respuesta final del agente")
    
    steps: List[AgentStep] = Field(
        default=[],
        description="Pasos del proceso de razonamiento ReAct"
    )
    
    tools_used: List[str] = Field(
        default=[],
        description="Herramientas utilizadas en el proceso"
    )
    
    processing_time: float = Field(
        ...,
        description="Tiempo de procesamiento en segundos"
    )
    
    success: bool = Field(..., description="Si la consulta fue exitosa")
    
    error_message: Optional[str] = Field(
        None,
        description="Mensaje de error si success=False"
    )
    
    timestamp: datetime = Field(default_factory=datetime.now)

class HealthResponse(BaseModel):
    """Modelo para el health check"""
    status: str = Field(..., description="Estado general del servicio")
    timestamp: datetime = Field(default_factory=datetime.now)
    services: Dict[str, Any] = Field(
        default={},
        description="Estado de servicios individuales"
    )

class ToolInfo(BaseModel):
    """Información sobre una herramienta"""
    name: str = Field(..., description="Nombre de la herramienta")
    description: str = Field(..., description="Descripción de la herramienta")
    type: ToolType = Field(..., description="Tipo de herramienta")
    available: bool = Field(..., description="Si la herramienta está disponible")
    last_used: Optional[datetime] = Field(None, description="Última vez que se usó")

class ConfigModel(BaseModel):
    """Modelo para configuración de la aplicación"""
    hf_model_name: str = Field(default="microsoft/DialoGPT-medium", description="Modelo de Hugging Face a usar")
    hf_model_type: str = Field(default="text-generation", description="Tipo de modelo de HF")
    hf_max_tokens: int = Field(default=512, description="Máximo tokens en respuesta")
    hf_temperature: float = Field(default=0.7, description="Temperatura del modelo")
    hf_device: str = Field(default="auto", description="Dispositivo para el modelo")
    timeout: int = Field(default=30, description="Timeout en segundos")
    
    # Configuración de herramientas
    enable_web_search: bool = Field(default=True, description="Habilitar búsqueda web")
    enable_calculator: bool = Field(default=True, description="Habilitar calculadora")
    enable_translator: bool = Field(default=True, description="Habilitar traductor") 