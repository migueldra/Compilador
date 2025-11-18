"""Simulador de las primeras fases de un compilador aritmético básico.

Incluye:
    - Análisis léxico: generación de tokens y detección de errores.
    - Análisis sintáctico: construcción de un AST respetando precedencias.
    - Tablas semánticas: tabla de símbolos y tabla de tipos.
    - Generación de código intermedio: código de tres direcciones.

El programa admite números enteros y los operadores +, -, *, /. Los
paréntesis están soportados para facilitar expresiones complejas. Los
espacios en blanco se ignoran durante el análisis léxico.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union


class LexerError(Exception):
    """Error específico del análisis léxico."""

    def __init__(self, position: int, character: str) -> None:
        super().__init__(
            f"Caracter no reconocido '{character}' en la posición {position}."
        )
        self.position = position
        self.character = character


class ParserError(Exception):
    """Error específico del análisis sintáctico."""

    def __init__(self, message: str, position: Optional[int] = None) -> None:
        if position is not None:
            message = f"{message} en la posición {position}."
        super().__init__(message)
        self.position = position


@dataclass
class Token:
    tipo: str
    valor: str
    posicion: int

    def __repr__(self) -> str:  # pragma: no cover - ayuda de depuración
        return f"Token(tipo={self.tipo}, valor={self.valor}, posicion={self.posicion})"


class Lexer:
    """Genera tokens a partir de una cadena de entrada."""

    _TIPOS = {
        "+": "PLUS",
        "-": "MINUS",
        "*": "MUL",
        "/": "DIV",
        "(": "LPAREN",
        ")": "RPAREN",
    }

    def tokenize(self, expresion: str) -> List[Token]:
        tokens: List[Token] = []
        posicion = 0

        while posicion < len(expresion):
            caracter = expresion[posicion]

            if caracter.isdigit():
                inicio = posicion
                while posicion < len(expresion) and expresion[posicion].isdigit():
                    posicion += 1
                valor = expresion[inicio:posicion]
                tokens.append(Token("NUMBER", valor, inicio))
                continue

            if caracter in self._TIPOS:
                tokens.append(Token(self._TIPOS[caracter], caracter, posicion))
                posicion += 1
                continue

            if caracter.isspace():
                posicion += 1
                continue

            raise LexerError(posicion, caracter)

        return tokens


class ASTNode:
    """Nodo base del Árbol de Sintaxis Abstracta."""


@dataclass
class NumberNode(ASTNode):
    valor: int


@dataclass
class BinaryOpNode(ASTNode):
    operador: str
    izquierdo: ASTNode
    derecho: ASTNode


class Parser:
    """Constructores de AST a partir de una secuencia de tokens."""

    def __init__(self, tokens: List[Token]) -> None:
        self._tokens = tokens
        self._indice = 0

    def parse(self) -> ASTNode:
        if not self._tokens:
            raise ParserError("La expresión está vacía")

        nodo = self._parse_expresion()

        if not self._al_final():
            token = self._tokens[self._indice]
            raise ParserError("Token inesperado", token.posicion)

        return nodo

    def _parse_expresion(self) -> ASTNode:
        nodo = self._parse_termino()

        while self._coincide({"PLUS", "MINUS"}):
            operador = self._avanzar().valor
            derecho = self._parse_termino()
            nodo = BinaryOpNode(operador, nodo, derecho)

        return nodo

    def _parse_termino(self) -> ASTNode:
        nodo = self._parse_factor()

        while self._coincide({"MUL", "DIV"}):
            operador = self._avanzar().valor
            derecho = self._parse_factor()
            nodo = BinaryOpNode(operador, nodo, derecho)

        return nodo

    def _parse_factor(self) -> ASTNode:
        if self._coincide({"NUMBER"}):
            token = self._avanzar()
            return NumberNode(int(token.valor))

        if self._coincide({"LPAREN"}):
            self._avanzar()  # consume '('
            nodo = self._parse_expresion()
            if not self._coincide({"RPAREN"}):
                if not self._al_final():
                    posicion = self._tokens[self._indice].posicion
                else:
                    posicion = self._tokens[self._indice - 1].posicion + 1
                raise ParserError("Se esperaba ')'", posicion)
            self._avanzar()  # consume ')'
            return nodo

        token = self._tokens[self._indice] if not self._al_final() else None
        posicion = token.posicion if token else None
        raise ParserError("Factor no válido", posicion)

    def _coincide(self, tipos: Union[str, set]) -> bool:
        if isinstance(tipos, str):
            tipos = {tipos}
        if self._al_final():
            return False
        return self._tokens[self._indice].tipo in tipos

    def _avanzar(self) -> Token:
        token = self._tokens[self._indice]
        self._indice += 1
        return token

    def _al_final(self) -> bool:
        return self._indice >= len(self._tokens)


def formatear_tokens(tokens: List[Token]) -> str:
    partes = []
    for token in tokens:
        if token.tipo == "NUMBER":
            partes.append(f"<{token.tipo}, {token.valor}>")
        else:
            partes.append(f"<{token.tipo}>")
    return " ".join(partes)


def formatear_ast(nodo: ASTNode, nivel: int = 0) -> str:
    indentacion = "  " * nivel
    if isinstance(nodo, NumberNode):
        return f"{indentacion}Número({nodo.valor})"
    if isinstance(nodo, BinaryOpNode):
        resultado = f"{indentacion}Operador('{nodo.operador}')\n"
        resultado += formatear_ast(nodo.izquierdo, nivel + 1) + "\n"
        resultado += formatear_ast(nodo.derecho, nivel + 1)
        return resultado
    raise TypeError(f"Tipo de nodo desconocido: {type(nodo)!r}")


def construir_tablas_semanticas(nodo: ASTNode) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], Dict[int, str]]:
    simbolos: Dict[int, str] = {}
    orden: List[int] = []

    def visitar(actual: ASTNode) -> None:
        if isinstance(actual, NumberNode):
            if actual.valor not in simbolos:
                simbolos[actual.valor] = f"dir_{len(simbolos) + 1}"
                orden.append(actual.valor)
            return
        if isinstance(actual, BinaryOpNode):
            visitar(actual.izquierdo)
            visitar(actual.derecho)
            return
        raise TypeError(f"Tipo de nodo desconocido: {type(actual)!r}")

    visitar(nodo)

    tabla_simbolos = [
        {"simbolo": str(valor), "direccion": simbolos[valor]}
        for valor in orden
    ]

    tabla_tipos = [
        {"simbolo": str(valor), "tipo": "entero"}
        for valor in orden
    ]

    return tabla_simbolos, tabla_tipos, simbolos


def generar_codigo_tres_direcciones(
    nodo: ASTNode,
    direcciones: Dict[int, str],
) -> Tuple[List[str], str]:
    instrucciones: List[str] = []
    temporal = 1

    def generar(actual: ASTNode) -> str:
        nonlocal temporal
        if isinstance(actual, NumberNode):
            return direcciones[actual.valor]
        if isinstance(actual, BinaryOpNode):
            izquierda = generar(actual.izquierdo)
            derecha = generar(actual.derecho)
            destino = f"t{temporal}"
            temporal += 1
            instrucciones.append(f"{destino} = {izquierda} {actual.operador} {derecha}")
            return destino
        raise TypeError(f"Tipo de nodo desconocido: {type(actual)!r}")

    resultado = generar(nodo)
    return instrucciones, resultado


class ArithmeticCompiler:
    """Orquesta las etapas del simulador de compilador aritmético."""

    def __init__(self) -> None:
        self._lexer = Lexer()

    def compilar(self, expresion: str) -> Dict[str, object]:
        tokens = self._lexer.tokenize(expresion)

        parser = Parser(tokens)
        ast = parser.parse()

        tabla_simbolos, tabla_tipos, direcciones = construir_tablas_semanticas(ast)
        codigo_tres_dir, referencia_resultado = generar_codigo_tres_direcciones(ast, direcciones)

        return {
            "tokens": tokens,
            "ast": ast,
            "tabla_simbolos": tabla_simbolos,
            "tabla_tipos": tabla_tipos,
            "codigo_tres_direcciones": codigo_tres_dir,
            "resultado": referencia_resultado,
        }


def ejecutar_desde_consola() -> None:
    compilador = ArithmeticCompiler()
    expresion = input("Introduce una expresión aritmética: ")

    try:
        resultado = compilador.compilar(expresion)
    except LexerError as error:
        print(f"Error léxico: {error}")
        return
    except ParserError as error:
        print(f"Error sintáctico: {error}")
        return

    tokens: List[Token] = resultado["tokens"]
    ast: ASTNode = resultado["ast"]
    tabla_simbolos: List[Dict[str, str]] = resultado["tabla_simbolos"]
    tabla_tipos: List[Dict[str, str]] = resultado["tabla_tipos"]
    codigo_tres_dir: List[str] = resultado["codigo_tres_direcciones"]
    referencia_resultado: str = resultado["resultado"]

    print("\n=== Tokens ===")
    print(formatear_tokens(tokens))

    print("\n=== AST ===")
    print(formatear_ast(ast))

    print("\n=== Tabla de símbolos ===")
    for entrada in tabla_simbolos:
        print(f"Símbolo: {entrada['simbolo']}, Dirección: {entrada['direccion']}")

    print("\n=== Tabla de tipos ===")
    for entrada in tabla_tipos:
        print(f"Símbolo: {entrada['simbolo']}, Tipo: {entrada['tipo']}")

    print("\n=== Código de tres direcciones ===")
    for instruccion in codigo_tres_dir:
        print(instruccion)
    print(f"Resultado final en: {referencia_resultado}")


if __name__ == "__main__":  # pragma: no cover - punto de entrada manual
    ejecutar_desde_consola()

