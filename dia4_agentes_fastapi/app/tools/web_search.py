"""
Herramienta de búsqueda web real usando DuckDuckGo
"""

import asyncio
import logging
from typing import Optional
try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None
from .base import BaseTool

logger = logging.getLogger(__name__)

class WebSearchTool(BaseTool):
    """Herramienta de búsqueda web usando DuckDuckGo"""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Buscar información actualizada en internet usando DuckDuckGo. "
                       "Útil para obtener datos recientes, noticias, precios, etc."
        )
        self.max_results = 5
        self.region = "es-es"  # Región en español
        
    async def execute(self, query: str) -> str:
        """Ejecutar búsqueda web"""
        try:
            # DuckDuckGo search no es nativa async, usar thread pool
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, 
                self._search_sync, 
                query
            )
            
            if not results:
                return f"No se encontraron resultados para: {query}"
            
            # Formatear resultados
            formatted_results = self._format_results(results, query)
            
            logger.info(f"🌐 Búsqueda web completada: {len(results)} resultados para '{query}'")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error en búsqueda web: {e}")
            return f"Error realizando búsqueda: {str(e)}"
    
    def _search_sync(self, query: str) -> list:
        """Búsqueda síncrona usando DuckDuckGo"""
        if DDGS is None:
            logger.warning("DDGS no disponible, retornando resultados mock")
            return [{
                'title': f"[MOCK] Resultado para: {query}",
                'body': "Biblioteca de búsqueda web no disponible. Instala 'ddgs' para funcionalidad completa.",
                'href': "https://example.com"
            }]
        
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(
                    keywords=query,
                    region=self.region,
                    max_results=self.max_results,
                    safesearch='moderate'
                ))
                return results
        except Exception as e:
            logger.error(f"Error en _search_sync: {e}")
            return []
    
    def _format_results(self, results: list, query: str) -> str:
        """Formatear resultados de búsqueda"""
        formatted = f"🌐 Resultados de búsqueda para '{query}':\n\n"
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'Sin título')
            body = result.get('body', 'Sin descripción')
            href = result.get('href', '')
            
            # Truncar descripción si es muy larga
            if len(body) > 200:
                body = body[:200] + "..."
            
            formatted += f"{i}. **{title}**\n"
            formatted += f"   {body}\n"
            formatted += f"   🔗 {href}\n\n"
        
        formatted += f"📊 Total: {len(results)} resultados encontrados"
        return formatted
    
    def health_check(self) -> bool:
        """Verificar si DuckDuckGo está disponible"""
        if DDGS is None:
            logger.warning("DDGS no disponible, usando modo mock")
            return True  # Mock siempre disponible
        
        try:
            # Test rápido con búsqueda simple
            with DDGS() as ddgs:
                test_results = list(ddgs.text(
                    keywords="test",
                    max_results=1,
                    safesearch='moderate'
                ))
                return len(test_results) > 0
        except Exception as e:
            logger.error(f"Health check falló para web_search: {e}")
            return False

class WebSearchLangChainTool:
    """Adaptador para usar WebSearchTool con LangChain"""
    
    def __init__(self):
        self.web_tool = WebSearchTool()
        self.name = "DuckDuckGo_Search"
        self.description = self.web_tool.description
    
    async def arun(self, query: str) -> str:
        """Método async para LangChain"""
        return await self.web_tool.execute(query)
    
    def run(self, query: str) -> str:
        """Método sync para LangChain"""
        return asyncio.run(self.web_tool.execute(query)) 