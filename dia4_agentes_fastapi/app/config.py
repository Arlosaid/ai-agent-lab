"""
Configuración de la aplicación - Día 4
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuración de la aplicación usando variables de entorno"""
    
    # Hugging Face Configuration
    hf_model_name: str = Field(
        default="microsoft/DialoGPT-medium",
        description="Modelo de Hugging Face a usar"
    )
    hf_model_type: str = Field(
        default="text-generation",
        description="Tipo de modelo: text-generation, conversational"
    )
    hf_max_tokens: int = Field(
        default=512,
        description="Máximo tokens en respuesta"
    )
    hf_temperature: float = Field(
        default=0.7,
        description="Temperatura del modelo"
    )
    hf_device: str = Field(
        default="auto",
        description="Dispositivo para ejecutar modelo: auto, cpu, cuda"
    )
    
    # Application Configuration
    app_name: str = Field(
        default="Agentes IA - Día 4",
        description="Nombre de la aplicación"
    )
    app_version: str = Field(
        default="1.0.0",
        description="Versión de la aplicación"
    )
    debug: bool = Field(
        default=True,
        description="Modo debug"
    )
    log_level: str = Field(
        default="INFO",
        description="Nivel de logging"
    )
    
    # Server Configuration
    host: str = Field(
        default="0.0.0.0",
        description="Host del servidor"
    )
    port: int = Field(
        default=8000,
        description="Puerto del servidor"
    )
    
    # Tool Configuration
    enable_web_search: bool = Field(
        default=True,
        description="Habilitar búsqueda web"
    )
    enable_calculator: bool = Field(
        default=True,
        description="Habilitar calculadora"
    )
    enable_translator: bool = Field(
        default=True,
        description="Habilitar traductor"
    )
    
    # Timeouts
    request_timeout: int = Field(
        default=30,
        description="Timeout de requests en segundos"
    )
    agent_timeout: int = Field(
        default=45,
        description="Timeout del agente en segundos"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Instancia global de configuración
settings = Settings()

def get_settings() -> Settings:
    """Obtener configuración de la aplicación"""
    return settings

def validate_required_settings():
    """Validar configuraciones requeridas"""
    errors = []
    
    # Validaciones para Hugging Face - modelos siempre disponibles gratuitamente
    if not settings.hf_model_name:
        errors.append("HF_MODEL_NAME es requerida")
    
    # Verificar que el dispositivo sea válido
    valid_devices = ["auto", "cpu", "cuda", "mps"]
    if settings.hf_device not in valid_devices:
        errors.append(f"HF_DEVICE debe ser uno de: {', '.join(valid_devices)}")
    
    if errors:
        raise ValueError(f"Errores de configuración: {', '.join(errors)}")
    
    return True

# Variables de entorno esperadas (para documentación)
EXPECTED_ENV_VARS = {
    "HF_MODEL_NAME": "microsoft/DialoGPT-medium",
    "HF_MODEL_TYPE": "text-generation", 
    "HF_MAX_TOKENS": "512",
    "HF_TEMPERATURE": "0.7",
    "HF_DEVICE": "auto",
    "APP_NAME": "Agentes IA - Día 4",
    "APP_VERSION": "1.0.0",
    "DEBUG": "true",
    "LOG_LEVEL": "INFO",
    "HOST": "0.0.0.0",
    "PORT": "8000",
    "ENABLE_WEB_SEARCH": "true",
    "ENABLE_CALCULATOR": "true", 
    "ENABLE_TRANSLATOR": "true",
    "REQUEST_TIMEOUT": "30",
    "AGENT_TIMEOUT": "45"
} 