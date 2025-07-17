"""
Herramienta de traducción usando implementación mock para desarrollo
(Substituye Google Translate para evitar problemas de dependencias)
"""

import asyncio
import logging
from typing import Optional, Dict, List
from .base import BaseTool

logger = logging.getLogger(__name__)

class MockTranslationResult:
    """Resultado mock de traducción"""
    def __init__(self, text: str, src: str, dest: str):
        self.text = text
        self.src = src
        self.dest = dest

class TranslatorTool(BaseTool):
    """Herramienta de traducción usando implementación mock para desarrollo"""
    
    def __init__(self):
        super().__init__(
            name="translator",
            description="Traductor de idiomas usando servicio mock para desarrollo. "
                       "Puede detectar automáticamente el idioma origen y traducir a múltiples idiomas. "
                       "Formato: 'texto a traducir' o 'texto | idioma_destino' "
                       "Ejemplos: 'Hello world | es', 'Bonjour | en', 'auto-detect: Guten Tag'"
        )
        self.default_target = 'es'  # Español por defecto
        
        # Idiomas más comunes
        self.common_languages = {
            'es': 'Español',
            'en': 'Inglés', 
            'fr': 'Francés',
            'de': 'Alemán',
            'it': 'Italiano',
            'pt': 'Portugués',
            'ru': 'Ruso',
            'ja': 'Japonés',
            'ko': 'Coreano',
            'zh': 'Chino',
            'ar': 'Árabe'
        }
        
        # Traducciones mock para demo
        self.mock_translations = {
            ('hello', 'en', 'es'): 'hola',
            ('hello world', 'en', 'es'): 'hola mundo',
            ('good morning', 'en', 'es'): 'buenos días',
            ('thank you', 'en', 'es'): 'gracias',
            ('how are you', 'en', 'es'): 'cómo estás',
            ('hola', 'es', 'en'): 'hello',
            ('hola mundo', 'es', 'en'): 'hello world',
            ('buenos días', 'es', 'en'): 'good morning',
            ('gracias', 'es', 'en'): 'thank you',
            ('cómo estás', 'es', 'en'): 'how are you',
        }
    
    async def execute(self, text_input: str) -> str:
        """Ejecutar traducción mock"""
        try:
            # Parsear entrada
            text, target_lang, source_lang = self._parse_input(text_input)
            
            logger.info(f"[TRANSLATE] Traduciendo (MOCK) '{text[:50]}...' a {target_lang}")
            
            # Simular traducción usando mock
            result = await self._translate_mock(text, source_lang, target_lang)
            
            if result:
                formatted_result = self._format_result(text, result)
                logger.info(f"[SUCCESS] Traducción mock completada: {result.src} -> {result.dest}")
                return formatted_result
            else:
                return f"Error en traducción mock de '{text}'"
                
        except Exception as e:
            logger.error(f"Error en traducción mock: {e}")
            return f"Error en traducción: {str(e)}"
    
    def _parse_input(self, text_input: str) -> tuple[str, str, Optional[str]]:
        """Parsear entrada del usuario"""
        # Formato: "texto | idioma_destino"
        if '|' in text_input:
            parts = text_input.split('|', 1)
            text = parts[0].strip()
            target_lang = parts[1].strip().lower()
        else:
            text = text_input.strip()
            target_lang = self.default_target
        
        # Auto-detectar idioma origen (simulado)
        source_lang = self._detect_language_mock(text)
        
        return text, target_lang, source_lang
    
    def _detect_language_mock(self, text: str) -> str:
        """Detectar idioma de forma mock"""
        text_lower = text.lower()
        
        # Detección simple basada en palabras comunes
        spanish_words = ['hola', 'gracias', 'buenos', 'días', 'cómo', 'estás', 'sí', 'no']
        english_words = ['hello', 'thank', 'good', 'morning', 'how', 'are', 'yes', 'no']
        
        spanish_count = sum(1 for word in spanish_words if word in text_lower)
        english_count = sum(1 for word in english_words if word in text_lower)
        
        if spanish_count > english_count:
            return 'es'
        else:
            return 'en'
    
    async def _translate_mock(self, text: str, source_lang: Optional[str], target_lang: str) -> MockTranslationResult:
        """Traducción mock usando diccionario predefinido"""
        # Simular delay de API
        await asyncio.sleep(0.1)
        
        text_lower = text.lower().strip()
        
        # Buscar en traducciones predefinidas
        for (mock_text, src, dest), translation in self.mock_translations.items():
            if (text_lower == mock_text and 
                source_lang == src and 
                target_lang == dest):
                return MockTranslationResult(translation, src, dest)
        
        # Si no encuentra traducción exacta, crear una mock genérica
        if target_lang == 'es' and source_lang == 'en':
            mock_translation = f"[TRADUCCIÓN MOCK ES] {text}"
        elif target_lang == 'en' and source_lang == 'es':
            mock_translation = f"[MOCK TRANSLATION EN] {text}"
        else:
            mock_translation = f"[MOCK {target_lang.upper()}] {text}"
        
        return MockTranslationResult(mock_translation, source_lang, target_lang)
    
    def _format_result(self, original_text: str, result: MockTranslationResult) -> str:
        """Formatear resultado de traducción"""
        source_name = self.common_languages.get(result.src, result.src.upper())
        target_name = self.common_languages.get(result.dest, result.dest.upper())
        
        return f"""[TRANSLATE] TRADUCCIÓN COMPLETADA (MOCK MODE)

Texto original ({source_name}): {original_text}
Traducción ({target_name}): {result.text}
Idiomas: {result.src} -> {result.dest}

Nota: Esta es una traducción mock para desarrollo.
En producción se usaría Google Translate u otro servicio real."""
    
    def health_check(self) -> bool:
        """Verificar disponibilidad del traductor mock"""
        try:
            # El mock siempre está disponible
            logger.info("[HEALTH] Traductor mock: OK")
            return True
        except Exception as e:
            logger.error(f"Error en health check del traductor mock: {e}")
            return False
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Obtener idiomas soportados (mock)"""
        return self.common_languages.copy()
    
    def get_common_languages(self) -> Dict[str, str]:
        """Obtener idiomas comunes"""
        return self.common_languages.copy()

class TranslatorLangChainTool:
    """Adaptador de LangChain para el traductor mock"""
    
    def __init__(self):
        self.translator_tool = TranslatorTool()
        self.name = "translator"
        self.description = self.translator_tool.description
    
    async def arun(self, text_input: str) -> str:
        """Ejecutar traducción de forma asíncrona"""
        return await self.translator_tool.execute(text_input)
    
    def run(self, text_input: str) -> str:
        """Ejecutar traducción de forma síncrona"""
        return asyncio.run(self.translator_tool.execute(text_input)) 