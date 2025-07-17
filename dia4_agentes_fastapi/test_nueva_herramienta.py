#!/usr/bin/env python3
"""
🎓 TUTORIAL: Probando la nueva herramienta de análisis de sentimientos

Este script demuestra:
1. Cómo crear herramientas personalizadas
2. Cómo integrarlas en el sistema
3. Cómo probarlas independientemente
4. Cómo usarlas con el agente

Ejecutar: python test_nueva_herramienta.py
"""

import asyncio
import logging
from app.tools.sentiment_analyzer import SentimentAnalyzerTool

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_sentiment_tool():
    """Probar la herramienta de análisis de sentimientos"""
    
    print("🎓 TUTORIAL: Probando nueva herramienta de análisis de sentimientos")
    print("=" * 70)
    
    # 1. Crear instancia de la herramienta
    sentiment_tool = SentimentAnalyzerTool()
    
    print(f"✅ Herramienta creada: {sentiment_tool.name}")
    print(f"📝 Descripción: {sentiment_tool.description}")
    print()
    
    # 2. Verificar health check
    is_healthy = sentiment_tool.health_check()
    print(f"🩺 Health check: {'✅ Saludable' if is_healthy else '❌ Error'}")
    print()
    
    # 3. Probar con diferentes textos
    test_texts = [
        "Me encanta este producto, es fantástico y excelente calidad!",
        "Este servicio es terrible, muy malo y decepcionante",
        "El clima está normal hoy, ni bueno ni malo",
        "I love this amazing product! It's the best thing ever!",
        "This is absolutely horrible and awful. I hate it!"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"🧪 PRUEBA {i}:")
        print(f"📝 Texto: {text}")
        print("🤖 Análisis:")
        
        try:
            result = await sentiment_tool.execute(text)
            print(result)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 50)
    
    # 4. Mostrar estadísticas
    info = sentiment_tool.get_info()
    print("📊 ESTADÍSTICAS DE LA HERRAMIENTA:")
    print(f"   • Nombre: {info['name']}")
    print(f"   • Veces usada: {info['usage_count']}")
    print(f"   • Última vez usada: {info['last_used']}")
    print(f"   • Disponible: {info['is_available']}")

async def test_with_tool_manager():
    """Probar usando el ToolManager (como lo hace el agente)"""
    
    print("\n🎓 TUTORIAL: Probando con ToolManager (sistema completo)")
    print("=" * 70)
    
    # Importar el tool manager actualizado
    from app.tools import create_tool_manager
    
    # Crear el gestor
    tool_manager = create_tool_manager()
    
    # Verificar que nuestra herramienta está registrada
    tools_info = tool_manager.get_tools_info()
    
    print("🔧 HERRAMIENTAS REGISTRADAS:")
    for name, info in tools_info.items():
        status = "✅" if info['is_available'] else "❌"
        print(f"   {status} {name}: {info['usage_count']} usos")
    
    print()
    
    # Probar nuestra nueva herramienta a través del manager
    sentiment_tool = tool_manager.get_tool("sentiment_analyzer")
    
    if sentiment_tool:
        print("🧪 Probando a través del ToolManager:")
        result = await sentiment_tool.run("Esta aplicación de IA es increíble!")
        print(result)
    else:
        print("❌ Herramienta no encontrada en el manager")

async def demonstrate_extensibility():
    """Demostrar lo fácil que es extender el sistema"""
    
    print("\n🎓 TUTORIAL: Patrón de extensibilidad")
    print("=" * 70)
    
    print("""
🧠 CONCEPTOS CLAVE QUE HAS APRENDIDO:

1. **Patrón Strategy**: Cada herramienta implementa BaseTool
   → Puedes intercambiar herramientas sin cambiar el agente

2. **Dependency Injection**: El ToolManager inyecta herramientas
   → Fácil testing y configuración

3. **Interface Segregation**: Cada herramienta solo expone lo necesario
   → execute() y health_check()

4. **Single Responsibility**: Cada herramienta hace una cosa bien
   → Fácil mantener y debuggear

5. **Open/Closed Principle**: Sistema abierto para extensión
   → Adds nuevas herramientas sin modificar código existente

🚀 PRÓXIMOS PASOS PARA PRÁCTICA:

1. Crear herramienta de "generador de códigos QR"
2. Crear herramienta de "análisis de imágenes"
3. Crear herramienta de "conectar con base de datos"
4. Crear herramienta de "envío de emails"

💼 VALOR PARA EMPRESAS:

- Forward Deployed Engineer: Puedes añadir herramientas específicas del cliente
- AI Full Stack: Entiendes toda la arquitectura de agentes
- MLOps Engineer: Sistema robusto y monitoreable
    """)

async def main():
    """Función principal del tutorial"""
    
    print("""
🎓 TUTORIAL COMPLETO: EXTENSIÓN DE AGENTES IA
==============================================

Este tutorial te enseña cómo extender tu sistema de agentes
con nuevas capacidades - una habilidad CLAVE para trabajos de IA.
    """)
    
    # Ejecutar todas las pruebas
    await test_sentiment_tool()
    await test_with_tool_manager()
    await demonstrate_extensibility()
    
    print("""
🎉 ¡TUTORIAL COMPLETADO!

Has aprendido a:
✅ Crear nuevas herramientas siguiendo el patrón establecido
✅ Integrarlas en el sistema existente
✅ Probarlas independientemente
✅ Entender la arquitectura extensible

🚀 Esto te diferencia de otros candidatos porque demuestras
   que puedes CONSTRUIR y EXTENDER sistemas de IA reales.
    """)

if __name__ == "__main__":
    asyncio.run(main()) 