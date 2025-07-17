"""
Servicio de Agente IA con patrón ReAct y herramientas reales
"""

import time
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

# LangChain imports
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain_core.language_models.llms import BaseLLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.outputs import LLMResult, Generation
from langchain_huggingface import HuggingFacePipeline
from typing import Optional, List, Any, Dict, Mapping

# HuggingFace imports
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
except ImportError as e:
    torch = None
    AutoTokenizer = None
    AutoModelForCausalLM = None
    pipeline = None
    print(f"[WARNING] HuggingFace dependencies not available: {e}")

# Configuración y herramientas locales
from .config import get_settings
from .tools import create_langchain_tools, create_tool_manager
from .models import AgentResponse, AgentStep, ToolType

logger = logging.getLogger(__name__)

class AgentService:
    """Servicio principal del agente IA con herramientas reales"""
    
    def __init__(self):
        self.settings = get_settings()
        self.llm = None
        self.agent_executor = None
        self.tool_manager = None
        self.langchain_tools = []
        self.is_initialized = False
        
    async def initialize(self):
        """Inicializar el servicio del agente"""
        try:
            logger.info("[INIT] Inicializando AgentService...")
            
            # Configurar LLM
            await self._setup_llm()
            
            # Configurar herramientas
            await self._setup_tools()
            
            # Configurar agente ReAct
            await self._setup_agent()
            
            self.is_initialized = True
            logger.info("[SUCCESS] AgentService inicializado correctamente")
            
        except Exception as e:
            logger.error(f"[ERROR] Error inicializando AgentService: {e}")
            raise e
    
    async def _setup_llm(self):
        """Configurar el modelo de lenguaje con Hugging Face"""
        try:
            # FORZAR MOCK TEMPORALMENTE - DialoGPT-medium no funciona bien con ReAct
            if self.settings.hf_model_name == "microsoft/DialoGPT-medium":
                logger.warning("[OVERRIDE] DialoGPT-medium no es compatible con agentes ReAct")
                logger.warning("[OVERRIDE] Forzando uso de MockLLM para demostración")
                raise ImportError("Modelo no compatible - usando mock")
            
            # Verificar dependencias de HuggingFace
            if torch is None or AutoTokenizer is None or AutoModelForCausalLM is None or pipeline is None:
                raise ImportError("Dependencias de HuggingFace no disponibles")
            
            # NOTA IMPORTANTE: Modelos recomendados para agentes ReAct:
            # - "google/flan-t5-large" (excelente para seguir instrucciones) ⭐ RECOMENDADO
            # - "HuggingFaceH4/zephyr-7b-beta" (muy bueno para agentes)
            # - "microsoft/GODEL-v1_1-large-seq2seq" (mejor para tareas estructuradas)
            # - "meta-llama/Llama-2-7b-chat-hf" (excelente pero requiere permisos)
            # Para cambiar modelo: actualizar hf_model_name en config.py o variable de entorno
                
            logger.info(f"[LLM] Configurando modelo HuggingFace: {self.settings.hf_model_name}")
            
            # Configurar dispositivo
            device = self._get_device()
            logger.info(f"[LLM] Usando dispositivo: {device}")
            
            # Cargar tokenizer y modelo
            tokenizer = AutoTokenizer.from_pretrained(self.settings.hf_model_name)
            
            # Asegurar que el tokenizer tenga un token de padding
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Configurar modelo
            model = AutoModelForCausalLM.from_pretrained(
                self.settings.hf_model_name,
                torch_dtype=torch.float16 if device != "cpu" else torch.float32,
                device_map=device if device != "cpu" else None,
                trust_remote_code=True
            )
            
            # Crear pipeline
            hf_pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=self.settings.hf_max_tokens,
                temperature=self.settings.hf_temperature,
                do_sample=True,
                device=0 if device == "cuda" else -1
            )
            
            # Crear LLM de LangChain
            self.llm = HuggingFacePipeline(pipeline=hf_pipeline)
            
            logger.info(f"[LLM] LLM de HuggingFace configurado exitosamente")
            
        except Exception as e:
            logger.error(f"[ERROR] Error configurando LLM de HuggingFace: {e}")
            logger.warning("[FALLBACK] Usando modelo mock debido al error")
            self.llm = MockLLM()
    
    def _get_device(self) -> str:
        """Determinar el dispositivo óptimo para ejecutar el modelo"""
        if torch is None:
            return "cpu"
        
        if self.settings.hf_device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return self.settings.hf_device
    
    async def _setup_tools(self):
        """Configurar herramientas del agente"""
        # Crear gestor de herramientas personalizado
        self.tool_manager = create_tool_manager()
        
        # Crear herramientas para LangChain
        self.langchain_tools = create_langchain_tools()
        
        # Verificar salud de herramientas
        health_status = await self.tool_manager.health_check_all()
        
        available_tools = [name for name, status in health_status.items() if status]
        unavailable_tools = [name for name, status in health_status.items() if not status]
        
        logger.info(f"[TOOLS] Herramientas disponibles: {available_tools}")
        if unavailable_tools:
            logger.warning(f"[WARNING] Herramientas no disponibles: {unavailable_tools}")
    
    async def _setup_agent(self):
        """Configurar agente ReAct"""
        # Prompt mejorado para ReAct con mejor compatibilidad
        react_prompt = PromptTemplate.from_template("""Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

IMPORTANT RULES:
- Always respond in Spanish but keep the keywords (Thought, Action, Action Input, Final Answer) in English
- Use tools when you need specific information
- Be precise and helpful in your responses
- If you can answer directly without tools, skip to Final Answer

Question: {input}
{agent_scratchpad}""")
        
        # Convertir herramientas a formato LangChain Tool
        langchain_tools_formatted = []
        for tool in self.langchain_tools:
            langchain_tool = Tool(
                name=tool.name,
                description=tool.description,
                func=tool.run,
                coroutine=tool.arun
            )
            langchain_tools_formatted.append(langchain_tool)
        
        # Crear agente ReAct
        agent = create_react_agent(
            llm=self.llm,
            tools=langchain_tools_formatted,
            prompt=react_prompt
        )
        
        # Crear executor del agente con configuración robusta
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=langchain_tools_formatted,
            verbose=True,
            return_intermediate_steps=True,
            max_iterations=3,  # Reducido para evitar bucles infinitos
            max_execution_time=self.settings.agent_timeout,
            handle_parsing_errors=True  # Crucial para manejar errores de parsing
        )
        
        logger.info("[AGENT] Agente ReAct configurado")
    
    async def process_query(
        self, 
        query: str, 
        context: Optional[str] = None,
        tools: Optional[List[ToolType]] = None
    ) -> AgentResponse:
        """Procesar consulta del usuario"""
        start_time = time.time()
        
        try:
            if not self.is_initialized:
                raise RuntimeError("AgentService no está inicializado")
            
            logger.info(f"[QUERY] Procesando consulta: {query[:100]}...")
            
            # Construir entrada completa
            full_input = self._build_input(query, context)
            
            # Ejecutar agente
            result = await self._execute_agent(full_input)
            
            # Extraer pasos y respuesta
            steps = self._extract_steps(result.get('intermediate_steps', []))
            final_answer = result.get('output', 'No se pudo generar respuesta')
            
            # Extraer herramientas usadas
            tools_used = self._extract_tools_used(steps)
            
            processing_time = time.time() - start_time
            
            response = AgentResponse(
                response=final_answer,
                steps=steps,
                tools_used=tools_used,
                processing_time=processing_time,
                success=True
            )
            
            logger.info(f"[SUCCESS] Consulta procesada en {processing_time:.2f}s")
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = str(e)
            
            logger.error(f"[ERROR] Error procesando consulta: {error_msg}")
            
            return AgentResponse(
                response=f"Error procesando consulta: {error_msg}",
                steps=[],
                tools_used=[],
                processing_time=processing_time,
                success=False,
                error_message=error_msg
            )
    
    def _build_input(self, query: str, context: Optional[str]) -> str:
        """Construir entrada completa para el agente"""
        if context:
            return f"Contexto: {context}\n\nPregunta: {query}"
        return query
    
    async def _execute_agent(self, input_text: str) -> Dict[str, Any]:
        """Ejecutar el agente de forma asíncrona"""
        loop = asyncio.get_event_loop()
        
        # AgentExecutor no es nativo async, usar thread pool
        result = await loop.run_in_executor(
            None,
            lambda: self.agent_executor.invoke({"input": input_text})
        )
        
        return result
    
    def _extract_steps(self, intermediate_steps: List) -> List[AgentStep]:
        """Extraer pasos del proceso de razonamiento"""
        steps = []
        
        for i, (agent_action, observation) in enumerate(intermediate_steps):
            step = AgentStep(
                step_number=i + 1,
                thought=agent_action.log if hasattr(agent_action, 'log') else "Pensando...",
                action=agent_action.tool if hasattr(agent_action, 'tool') else None,
                tool_used=agent_action.tool if hasattr(agent_action, 'tool') else None,
                observation=str(observation) if observation else None
            )
            steps.append(step)
        
        return steps
    
    def _extract_tools_used(self, steps: List[AgentStep]) -> List[str]:
        """Extraer lista de herramientas utilizadas"""
        tools_used = []
        for step in steps:
            if step.tool_used and step.tool_used not in tools_used:
                tools_used.append(step.tool_used)
        return tools_used
    
    async def health_check(self) -> bool:
        """Verificar estado del servicio"""
        try:
            if not self.is_initialized:
                return False
            
            # Verificar herramientas
            if self.tool_manager:
                tools_health = await self.tool_manager.health_check_all()
                return any(tools_health.values())
            
            return True
        except Exception as e:
            logger.error(f"Error en health check: {e}")
            return False
    
    def get_tools_status(self) -> Dict[str, Any]:
        """Obtener estado de las herramientas"""
        if not self.tool_manager:
            return {}
        
        return self.tool_manager.get_tools_info()
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Obtener herramientas disponibles"""
        if not self.tool_manager:
            return []
        
        tools_info = self.tool_manager.get_tools_info()
        return [info for info in tools_info.values() if info.get('is_available', False)]
    
    async def cleanup(self):
        """Limpiar recursos"""
        logger.info("[CLEANUP] Limpiando AgentService...")
        self.is_initialized = False
        # Aquí se pueden limpiar recursos adicionales si es necesario

class MockLLM(BaseLLM):
    """LLM mock completamente compatible con LangChain para desarrollo sin API key"""
    
    def __init__(self):
        super().__init__()
        self._temperature = 0.7
        self._max_tokens = 1000
        self._model_name = "mock-gpt-3.5-turbo"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Método principal requerido por BaseLLM"""
        return self._generate_mock_response(prompt)
    
    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Generar respuestas para múltiples prompts"""
        generations = []
        for prompt in prompts:
            response = self._generate_mock_response(prompt)
            generations.append([Generation(text=response)])
        
        return LLMResult(generations=generations)
    
    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Versión asíncrona de _call"""
        return self._call(prompt, stop, run_manager, **kwargs)
    
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Parámetros que identifican el modelo"""
        return {
            "model_name": self._model_name,
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
        }
    
    def _generate_mock_response(self, content: str) -> str:
        """Generar respuesta mock inteligente basada en el contenido"""
        content_lower = content.lower()
        
        # Detectar si ya hay una observación en el prompt (segunda fase del ReAct)
        has_observation = "observation:" in content_lower or "[mock]" in content_lower
        
        if has_observation:
            # Segunda fase: ya se ejecutó una herramienta, generar respuesta final
            if any(word in content_lower for word in ['bitcoin', 'btc', 'precio', 'criptomoneda']):
                return """Thought: He obtenido información actualizada sobre el precio del Bitcoin.
Final Answer: El precio actual del Bitcoin es de aproximadamente $65,000 USD (simulación en modo desarrollo). Para obtener precios reales en tiempo real, configura las API keys correspondientes."""
            
            elif any(op in content_lower for op in ['+', '-', '*', '/', 'calcul', 'cuanto es']):
                return """Thought: He completado el cálculo matemático solicitado.
Final Answer: He procesado tu cálculo matemático. En modo desarrollo estoy usando respuestas simuladas. Para cálculos reales, el sistema funcionará automáticamente."""
            
            elif any(word in content_lower for word in ['traduc', 'translate', 'idioma']):
                return """Thought: He completado la traducción solicitada.
Final Answer: Traducción completada en modo desarrollo con modelo mock. El sistema de traducción funcionará en modo producción."""
            
            else:
                return """Thought: He procesado la consulta.
Final Answer: Consulta procesada correctamente en modo desarrollo. El sistema está funcionando apropiadamente."""
        
        else:
            # Primera fase: necesito usar herramientas
            if any(word in content_lower for word in ['bitcoin', 'btc', 'precio', 'criptomoneda']):
                return """Thought: El usuario pregunta sobre el precio del Bitcoin. Necesito buscar información actualizada en la web.
Action: web_search
Action Input: precio actual Bitcoin USD"""

            elif any(op in content_lower for op in ['+', '-', '*', '/', 'calcul', 'cuanto es']):
                return """Thought: Necesito resolver esta operación matemática usando la calculadora.
Action: calculator
Action Input: operacion matematica"""

            elif any(word in content_lower for word in ['traduc', 'translate', 'idioma']):
                return """Thought: El usuario quiere traducir texto. Voy a usar la herramienta de traducción.
Action: translator
Action Input: texto a traducir"""

            else:
                # Para consultas generales, responder directamente sin herramientas
                return """Thought: Esta consulta la puedo responder directamente sin necesidad de herramientas.
Final Answer: He recibido tu consulta. Estoy funcionando en modo desarrollo con modelo mock. Para funcionalidad completa, asegúrate de configurar adecuadamente el entorno de producción."""
    
    # Propiedades adicionales para compatibilidad con LangChain
    @property
    def _llm_type(self):
        return "mock_llm"
    
    @property 
    def model_name(self):
        return self._model_name 