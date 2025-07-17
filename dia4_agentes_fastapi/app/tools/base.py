"""
Clase base para herramientas del agente IA
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BaseTool(ABC):
    """Clase base para todas las herramientas del agente"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.last_used: Optional[datetime] = None
        self.usage_count = 0
        self.is_available = True
        
    @abstractmethod
    async def execute(self, input_data: str) -> str:
        """Ejecutar la herramienta con los datos de entrada"""
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Verificar si la herramienta está funcionando correctamente"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Obtener información sobre la herramienta"""
        return {
            "name": self.name,
            "description": self.description,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "usage_count": self.usage_count,
            "is_available": self.is_available
        }
    
    async def run(self, input_data: str) -> str:
        """Ejecutar la herramienta con logging y manejo de errores"""
        try:
            logger.info(f"[TOOL] Ejecutando herramienta '{self.name}' con entrada: {input_data[:100]}...")
            
            result = await self.execute(input_data)
            
            # Actualizar estadísticas
            self.last_used = datetime.now()
            self.usage_count += 1
            
            logger.info(f"[SUCCESS] Herramienta '{self.name}' ejecutada exitosamente")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando herramienta '{self.name}': {e}")
            self.is_available = False
            raise e

class ToolManager:
    """Gestor de herramientas para el agente"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        logger.info("[MANAGER] ToolManager inicializado")
    
    def register_tool(self, tool: BaseTool):
        """Registrar una herramienta"""
        self.tools[tool.name] = tool
        logger.info(f"[SUCCESS] Herramienta '{tool.name}' registrada")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Obtener una herramienta por nombre"""
        return self.tools.get(name)
    
    def get_available_tools(self) -> Dict[str, BaseTool]:
        """Obtener todas las herramientas disponibles"""
        return {name: tool for name, tool in self.tools.items() if tool.is_available}
    
    def get_tools_info(self) -> Dict[str, Dict[str, Any]]:
        """Obtener información de todas las herramientas"""
        return {name: tool.get_info() for name, tool in self.tools.items()}
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Verificar el estado de todas las herramientas"""
        results = {}
        for name, tool in self.tools.items():
            try:
                results[name] = tool.health_check()
                tool.is_available = results[name]
            except Exception as e:
                logger.error(f"Error en health check de '{name}': {e}")
                results[name] = False
                tool.is_available = False
        
        return results 