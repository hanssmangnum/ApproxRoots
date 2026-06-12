from typing import Callable

from utils.func_parser import compile_expression, compile_with_derivative


class ParserService:
    """Compila expresiones de texto en evaluadores callable."""

    def compile_expression(self, text: str) -> Callable[[float], float]:
        return compile_expression(text)

    def compile_with_derivative(
        self, text: str
    ) -> tuple[Callable[[float], float], Callable[[float], float]]:
        return compile_with_derivative(text)

    def compile_derivative(self, text: str) -> Callable[[float], float]:
        return self.compile_with_derivative(text)[1]
