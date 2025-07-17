"""
Herramientas para el agente IA - Día 4
"""

from .base import BaseTool, ToolManager
from .web_search import WebSearchTool, WebSearchLangChainTool
from .calculator import CalculatorTool, CalculatorLangChainTool
from .translator import TranslatorTool, TranslatorLangChainTool
# 🎓 NUEVA HERRAMIENTA - Ejemplo educativo
from .sentiment_analyzer import SentimentAnalyzerTool

__all__ = [
    # Clases base
    "BaseTool",
    "ToolManager",
    
    # Herramientas personalizadas
    "WebSearchTool",
    "CalculatorTool", 
    "TranslatorTool",
    "SentimentAnalyzerTool",  # 🎓 NUEVA: Análisis de sentimientos
    
    # Adaptadores para LangChain
    "WebSearchLangChainTool",
    "CalculatorLangChainTool",
    "TranslatorLangChainTool"
]

def create_tool_manager() -> ToolManager:
    """Crear y configurar el gestor de herramientas"""
    manager = ToolManager()
    
    # Registrar herramientas originales
    manager.register_tool(WebSearchTool())
    manager.register_tool(CalculatorTool())
    manager.register_tool(TranslatorTool())
    
    # 🎓 NUEVA: Registrar herramienta de sentimientos
    manager.register_tool(SentimentAnalyzerTool())
    
    return manager

def create_langchain_tools() -> list:
    """Crear herramientas compatibles con LangChain"""
    # TODO: Crear adaptador LangChain para SentimentAnalyzerTool
    return [
        WebSearchLangChainTool(),
        CalculatorLangChainTool(),
        TranslatorLangChainTool()
    ] 