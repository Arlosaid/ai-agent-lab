"""
Herramienta de calculadora avanzada usando sympy
"""

import re
import math
import logging
from typing import Union
import sympy as sp
from sympy import sympify, latex
from .base import BaseTool

logger = logging.getLogger(__name__)

class CalculatorTool(BaseTool):
    """Calculadora avanzada con soporte para expresiones matemáticas complejas"""
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Calculadora matemática avanzada. Puede resolver ecuaciones, "
                       "operaciones aritméticas, álgebra, cálculo, trigonometría, etc. "
                       "Ejemplos: '2+2', 'sqrt(16)', 'sin(pi/2)', 'diff(x^2, x)', 'integrate(x^2, x)'"
        )
        
        # Configurar símbolos matemáticos comunes
        self.symbols = {
            'x': sp.Symbol('x'),
            'y': sp.Symbol('y'),
            'z': sp.Symbol('z'),
            't': sp.Symbol('t'),
            'pi': sp.pi,
            'e': sp.E,
            'inf': sp.oo
        }
    
    async def execute(self, expression: str) -> str:
        """Ejecutar cálculo matemático"""
        try:
            # Limpiar y preparar la expresión
            cleaned_expr = self._clean_expression(expression)
            
            logger.info(f"🧮 Calculando: {cleaned_expr}")
            
            # Intentar evaluar la expresión
            result = self._evaluate_expression(cleaned_expr)
            
            # Formatear resultado
            formatted_result = self._format_result(expression, result)
            
            logger.info(f"[SUCCESS] Cálculo completado: {result}")
            return formatted_result
            
        except Exception as e:
            error_msg = f"Error en cálculo: {str(e)}"
            logger.error(error_msg)
            return f"❌ {error_msg}\n\n💡 Tip: Usa sintaxis matemática estándar. Ejemplos:\n" \
                   f"  • Operaciones: 2+2, 3*4, 10/2, 2**3\n" \
                   f"  • Funciones: sqrt(16), sin(pi/2), log(10)\n" \
                   f"  • Álgebra: solve(x^2-4, x), expand((x+1)^2)"
    
    def _clean_expression(self, expr: str) -> str:
        """Limpiar y preparar expresión matemática"""
        # Remover espacios extra
        expr = expr.strip()
        
        # Convertir ^ a ** para potencias
        expr = expr.replace('^', '**')
        
        # Reemplazar algunas funciones comunes
        replacements = {
            'ln': 'log',
            'arcsin': 'asin',
            'arccos': 'acos',
            'arctan': 'atan',
        }
        
        for old, new in replacements.items():
            expr = expr.replace(old, new)
        
        return expr
    
    def _evaluate_expression(self, expr: str) -> Union[sp.Basic, float, int]:
        """Evaluar expresión matemática"""
        try:
            # Intentar parsear con sympy
            parsed_expr = sympify(expr, locals=self.symbols)
            
            # Si es un número, evaluar a float
            if parsed_expr.is_number:
                return float(parsed_expr.evalf())
            
            # Si contiene símbolos, intentar simplificar
            simplified = sp.simplify(parsed_expr)
            
            # Si después de simplificar es un número, evaluarlo
            if simplified.is_number:
                return float(simplified.evalf())
            
            return simplified
            
        except Exception as e:
            # Fallback: usar eval para expresiones simples
            try:
                # Solo permitir caracteres seguros
                safe_expr = re.sub(r'[^0-9+\-*/().\s]', '', expr)
                if safe_expr:
                    return eval(safe_expr)
            except:
                pass
            raise e
    
    def _format_result(self, original_expr: str, result: Union[sp.Basic, float, int]) -> str:
        """Formatear resultado del cálculo"""
        output = f"🧮 **Cálculo Matemático**\n\n"
        output += f"**Expresión:** `{original_expr}`\n\n"
        
        if isinstance(result, (int, float)):
            # Resultado numérico
            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 10)  # Evitar precisión excesiva
            
            output += f"**Resultado:** `{result}`\n"
            
            # Información adicional para números
            if isinstance(result, (int, float)) and result > 0:
                if result != int(result):
                    output += f"**Decimal:** `{float(result)}`\n"
                if result >= 1:
                    output += f"**Científica:** `{result:.2e}`\n"
        
        else:
            # Resultado simbólico
            output += f"**Resultado:** `{result}`\n"
            
            # Intentar evaluación numérica si es posible
            try:
                numeric_val = float(result.evalf())
                output += f"**Valor numérico:** `{numeric_val}`\n"
            except:
                pass
            
            # Mostrar en LaTeX si es complejo
            try:
                latex_expr = latex(result)
                if len(latex_expr) < 100:  # Solo si no es demasiado largo
                    output += f"**LaTeX:** `{latex_expr}`\n"
            except:
                pass
        
        return output
    
    def health_check(self) -> bool:
        """Verificar si la calculadora funciona correctamente"""
        try:
            # Test básico
            test_expr = "2 + 2"
            result = self._evaluate_expression(test_expr)
            return result == 4
        except Exception as e:
            logger.error(f"Health check falló para calculator: {e}")
            return False

class CalculatorLangChainTool:
    """Adaptador para usar CalculatorTool con LangChain"""
    
    def __init__(self):
        self.calc_tool = CalculatorTool()
        self.name = "Calculator"
        self.description = self.calc_tool.description
    
    async def arun(self, expression: str) -> str:
        """Método async para LangChain"""
        return await self.calc_tool.execute(expression)
    
    def run(self, expression: str) -> str:
        """Método sync para LangChain"""
        import asyncio
        return asyncio.run(self.calc_tool.execute(expression)) 