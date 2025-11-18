# Simulador de Compilador Aritmético

## Objetivo

El proyecto implementa un simulador de las primeras fases de un compilador para expresiones aritméticas simples, cubriendo:

- Análisis léxico con detección de errores.
- Construcción del Árbol de Sintaxis Abstracta (AST).
- Generación de la tabla de símbolos y de la tabla de tipos.
- Generación de código intermedio en forma de código de tres direcciones.

## Requisitos

- Python 3.10 o superior.

## Uso rápido

```bash
python compiler_simulator.py
```

El programa solicitará una expresión aritmética. Tras introducirla, mostrará:

1. La secuencia de tokens generada.
2. La representación textual del AST.
3. La tabla de símbolos (direcciones simuladas para cada operando).
4. La tabla de tipos (tipo entero para cada símbolo identificado).
5. El código de tres direcciones y la referencia donde queda el resultado final.

Ejemplo de entrada y salida:

```
Introduce una expresión aritmética: 3 + 4 * 2

=== Tokens ===
<NUMBER, 3> <PLUS> <NUMBER, 4> <MUL> <NUMBER, 2>

=== AST ===
Operador('+')
  Número(3)
  Operador('*')
    Número(4)
    Número(2)

=== Tabla de símbolos ===
Símbolo: 3, Dirección: dir_1
Símbolo: 4, Dirección: dir_2
Símbolo: 2, Dirección: dir_3

=== Tabla de tipos ===
Símbolo: 3, Tipo: entero
Símbolo: 4, Tipo: entero
Símbolo: 2, Tipo: entero

=== Código de tres direcciones ===
t1 = dir_2 * dir_3
t2 = dir_1 + t1
Resultado final en: t2
```

## Arquitectura

- `Lexer`: recorre la cadena de entrada, genera tokens y lanza `LexerError` si se encuentra un carácter inválido.
- `Parser`: aplica descenso recursivo respetando la precedencia de operadores. Construye nodos `NumberNode` y `BinaryOpNode`. Lanza `ParserError` ante inconsistencias sintácticas.
- `construir_tablas_semanticas`: recorre el AST y crea la tabla de símbolos con direcciones simuladas (`dir_1`, `dir_2`, ...), y la tabla de tipos que marca a cada símbolo como entero.
- `generar_codigo_tres_direcciones`: produce instrucciones temporales `t1`, `t2`, ... que representan el código intermedio, utilizando las direcciones simuladas de la tabla de símbolos.
- `ArithmeticCompiler`: clase de alto nivel que coordina todas las etapas y devuelve un diccionario con los resultados.

## Manejo de errores

- Caracteres inválidos → `LexerError` con la posición reportada.
- Tokens inesperados o paréntesis desbalanceados → `ParserError` especificando la posición aproximada.

## Extensiones recomendadas

- Agregar soporte para números negativos mediante un analizador de signos unarios.
- Incluir ejecución del código de tres direcciones para evaluar la expresión.
- Guardar las tablas y el AST en archivos externos para integración con otras herramientas.

