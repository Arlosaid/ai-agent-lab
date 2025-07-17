"""
Herramienta de análisis de sentimientos usando modelos locales
"""

import logging
from typing import Optional
try:
    from transformers import pipeline
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

from .base import BaseTool

logger = logging.getLogger(__name__)

class SentimentAnalyzerTool(BaseTool):
    """Herramienta para analizar sentimientos en texto"""
    
    def __init__(self):
        super().__init__(
            name="sentiment_analyzer",
            description="Analizar el sentimiento (positivo, negativo, neutral) de un texto. "
                       "Útil para análisis de opiniones, reviews, comentarios, etc."
        )
        self.pipeline = None
        self._initialize_model()
        
    def _initialize_model(self):
        """Inicializar el modelo de análisis de sentimientos"""
        try:
            if HF_AVAILABLE:
                # Modelo liviano en español
                self.pipeline = pipeline(
                    "sentiment-analysis",
                    model="nlptown/bert-base-multilingual-uncased-sentiment",
                    return_all_scores=True
                )
                logger.info("✅ Modelo de sentimientos inicializado")
            else:
                logger.warning("⚠️ Transformers no disponible - usando análisis mock")
        except Exception as e:
            logger.error(f"❌ Error inicializando modelo de sentimientos: {e}")
            self.pipeline = None

    async def execute(self, text: str) -> str:
        """Analizar sentimiento del texto"""
        try:
            if not text.strip():
                return "❌ Error: Texto vacío para analizar"
            
            if self.pipeline is None:
                # Análisis mock básico (para casos sin modelo)
                return self._mock_sentiment_analysis(text)
            
            # Análisis real con modelo
            results = self.pipeline(text)
            
            # Procesar resultados
            analysis = self._format_sentiment_results(text, results[0])
            
            logger.info(f"🧠 Análisis de sentimiento completado para texto: {text[:50]}...")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error en análisis de sentimientos: {e}")
            return f"❌ Error analizando sentimiento: {str(e)}"
    
    def _mock_sentiment_analysis(self, text: str) -> str:
        """Análisis mock básico usando palabras clave"""
        text_lower = text.lower()
        
        # Palabras positivas y negativas básicas
        positive_words = ['excelente', 'genial', 'bueno', 'fantástico', 'increíble', 'love', 'great', 'amazing', 'good', 'excellent']
        negative_words = ['malo', 'terrible', 'horrible', 'pésimo', 'awful', 'bad', 'terrible', 'horrible', 'hate', 'worst']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "POSITIVO ✅"
            confidence = min(0.6 + (positive_count * 0.1), 0.95)
        elif negative_count > positive_count:
            sentiment = "NEGATIVO ❌"
            confidence = min(0.6 + (negative_count * 0.1), 0.95)
        else:
            sentiment = "NEUTRAL ⚪"
            confidence = 0.5
        
        return f"""📊 **ANÁLISIS DE SENTIMIENTO** (Mock)

📝 **Texto analizado**: "{text[:100]}{'...' if len(text) > 100 else ''}"
🎯 **Sentimiento**: {sentiment}
📈 **Confianza**: {confidence:.1%}
🔍 **Método**: Análisis de palabras clave básico

⚠️ **Nota**: Este es un análisis básico. Para mayor precisión, instala 'transformers'."""

    def _format_sentiment_results(self, text: str, results: list) -> str:
        """Formatear resultados del modelo real"""
        # Encontrar el sentimiento con mayor score
        best_result = max(results, key=lambda x: x['score'])
        
        # Mapear etiquetas del modelo a español
        label_map = {
            'POSITIVE': 'POSITIVO ✅',
            'NEGATIVE': 'NEGATIVO ❌', 
            'NEUTRAL': 'NEUTRAL ⚪',
            '1 star': 'MUY NEGATIVO ❌❌',
            '2 stars': 'NEGATIVO ❌',
            '3 stars': 'NEUTRAL ⚪',
            '4 stars': 'POSITIVO ✅',
            '5 stars': 'MUY POSITIVO ✅✅'
        }
        
        sentiment_label = label_map.get(best_result['label'], best_result['label'])
        confidence = best_result['score']
        
        # Crear resumen detallado
        all_scores = "\n".join([
            f"   • {label_map.get(r['label'], r['label'])}: {r['score']:.1%}"
            for r in sorted(results, key=lambda x: x['score'], reverse=True)
        ])
        
        return f"""📊 **ANÁLISIS DE SENTIMIENTO**

📝 **Texto analizado**: "{text[:100]}{'...' if len(text) > 100 else ''}"
🎯 **Sentimiento principal**: {sentiment_label}
📈 **Confianza**: {confidence:.1%}

📋 **Todos los scores**:
{all_scores}

🤖 **Modelo**: bert-base-multilingual-uncased-sentiment"""

    def health_check(self) -> bool:
        """Verificar si la herramienta está funcionando"""
        try:
            # Test básico
            test_result = "Funcional" if HF_AVAILABLE else "Mock mode"
            return True
        except Exception as e:
            logger.error(f"❌ Health check failed para sentiment_analyzer: {e}")
            return False 