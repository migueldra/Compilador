# Explicación del Simulador de Compilador Aritmético

## Introducción

Este proyecto implementa un **simulador de compilador** que procesa expresiones aritméticas básicas (como `3 + 4 * 2` o `(5 - 2) / 3`). El compilador simula las primeras fases que todo compilador real realiza: análisis léxico, análisis sintáctico, análisis semántico y generación de código intermedio.

---

## Arquitectura General

El proyecto está compuesto por dos partes principales:

1. **Backend en Python** (`compiler_simulator.py`): Implementa toda la lógica del compilador
2. **Frontend en HTML/JavaScript** (`index.html`): Interfaz web interactiva para visualizar el proceso

---

## Componentes Principales del Código

### 1. Clases de Error Personalizadas

```python
class LexerError(Exception)
class ParserError(Exception)
```

**¿Qué hacen?**
- `LexerError`: Se lanza cuando el analizador léxico encuentra un carácter que no reconoce (por ejemplo, `@` o `#` en una expresión aritmética).
- `ParserError`: Se lanza cuando hay un error sintáctico, como paréntesis sin cerrar o tokens en posiciones incorrectas.

**Ejemplo**: Si escribes `3 + @ 5`, se lanzará un `LexerError` porque `@` no es un operador válido.

---

### 2. Clase Token

```python
@dataclass
class Token:
    tipo: str      # Tipo del token (NUMBER, SUM, RES, MUL, DIV, etc.)
    valor: str     # El valor literal (el número o el símbolo)
    posicion: int  # Posición en la cadena original
```

**¿Qué hace?**
Representa una unidad léxica reconocida. Por ejemplo, la expresión `3 + 4` se convierte en tres tokens:
- Token(tipo="NUMBER", valor="3", posicion=0)
- Token(tipo="SUM", valor="+", posicion=2)
- Token(tipo="NUMBER", valor="4", posicion=4)

---

### 3. Clase Lexer (Analizador Léxico)

```python
class Lexer:
    _TIPOS = {
        "+": "SUM",
        "-": "RES",
        "*": "MUL",
        "/": "DIV",
        "(": "PAREN_IZ",
        ")": "PAREN_D",
    }
    
    def tokenize(self, expresion: str) -> List[Token]
```

**¿Qué hace?**
El analizador léxico es la **primera fase** del compilador. Su función es:

1. **Recorrer carácter por carácter** la expresión de entrada
2. **Reconocer patrones**:
   - Si encuentra un dígito, lee todos los dígitos consecutivos para formar un número
   - Si encuentra un operador (`+`, `-`, `*`, `/`) o paréntesis, crea un token correspondiente
   - Ignora los espacios en blanco
3. **Generar una lista de tokens** que representa la expresión

**Ejemplo de funcionamiento:**
- Entrada: `"3 + 4 * 2"`
- Proceso:
  - Lee `3` → crea token `NUMBER` con valor `"3"`
  - Lee espacio → lo ignora
  - Lee `+` → crea token `SUM`
  - Lee espacio → lo ignora
  - Lee `4` → crea token `NUMBER` con valor `"4"`
  - Lee espacio → lo ignora
  - Lee `*` → crea token `MUL`
  - Lee espacio → lo ignora
  - Lee `2` → crea token `NUMBER` con valor `"2"`
- Salida: Lista de 5 tokens: `[NUMBER(3), SUM(+), NUMBER(4), MUL(*), NUMBER(2)]`

**Si encuentra un carácter inválido** (como `@` o `#`), lanza un `LexerError` indicando la posición del error.

---

### 4. Árbol de Sintaxis Abstracta (AST)

```python
class ASTNode:  # Clase base
    pass

@dataclass
class NumberNode(ASTNode):
    valor: int

@dataclass
class BinaryOpNode(ASTNode):
    operador: str
    izquierdo: ASTNode
    derecho: ASTNode
```

**¿Qué hace?**
El AST es una **representación en árbol** de la estructura de la expresión. Cada nodo puede ser:
- **NumberNode**: Representa un número (hoja del árbol)
- **BinaryOpNode**: Representa una operación binaria con dos hijos (izquierdo y derecho)

**Ejemplo:**
Para la expresión `3 + 4 * 2`, el AST sería:
```
        +
       / \
      3   *
         / \
        4   2
```

Esto refleja la **precedencia de operadores**: la multiplicación se evalúa antes que la suma.

---

### 5. Clase Parser (Analizador Sintáctico)

```python
class Parser:
    def parse(self) -> ASTNode
    def _parse_expresion(self) -> ASTNode
    def _parse_termino(self) -> ASTNode
    def _parse_factor(self) -> ASTNode
```

**¿Qué hace?**
El analizador sintáctico es la **segunda fase** del compilador. Toma la lista de tokens y construye el AST respetando:

1. **Precedencia de operadores**: `*` y `/` tienen mayor precedencia que `+` y `-`
2. **Asociatividad**: Los operadores se asocian de izquierda a derecha
3. **Paréntesis**: Cambian el orden de evaluación

**Estrategia de parsing:**
Utiliza **descenso recursivo** con tres niveles de precedencia:

- **`_parse_expresion()`**: Maneja `+` y `-` (menor precedencia)
- **`_parse_termino()`**: Maneja `*` y `/` (mayor precedencia)
- **`_parse_factor()`**: Maneja números y paréntesis (máxima precedencia)

**Ejemplo de funcionamiento:**
Para `3 + 4 * 2`:
1. `parse()` llama a `_parse_expresion()`
2. `_parse_expresion()` llama a `_parse_termino()` para obtener `3`
3. Ve el token `SUM(+)`, lo consume
4. Llama a `_parse_termino()` de nuevo, que:
   - Llama a `_parse_factor()` para obtener `4`
   - Ve el token `MUL(*)`, lo consume
   - Llama a `_parse_factor()` para obtener `2`
   - Construye: `BinaryOpNode('*', 4, 2)`
5. Construye: `BinaryOpNode('+', 3, BinaryOpNode('*', 4, 2))`

**Si hay un error sintáctico** (paréntesis sin cerrar, token inesperado), lanza un `ParserError`.

---

### 6. Construcción de Tablas Semánticas

```python
def construir_tablas_semanticas(nodo: ASTNode) -> Tuple[...]
```

**¿Qué hace?**
Esta función realiza el **análisis semántico** (tercera fase). Recorre el AST y genera:

1. **Tabla de Símbolos**: Asigna una dirección de memoria simulada a cada número único encontrado
   - Ejemplo: Si la expresión tiene los números `3`, `4` y `2`, crea:
     - `3` → `dir_1`
     - `4` → `dir_2`
     - `2` → `dir_3`

2. **Tabla de Tipos**: Indica el tipo de dato de cada símbolo
   - En este caso, todos son de tipo `"entero"`

**Ejemplo:**
Para `3 + 4 * 2`:
- Tabla de símbolos:
  - Símbolo: 3, Dirección: dir_1
  - Símbolo: 4, Dirección: dir_2
  - Símbolo: 2, Dirección: dir_3
- Tabla de tipos:
  - Símbolo: 3, Tipo: entero
  - Símbolo: 4, Tipo: entero
  - Símbolo: 2, Tipo: entero

---

### 7. Generación de Código de Tres Direcciones

```python
def generar_codigo_tres_direcciones(nodo: ASTNode, direcciones: Dict) -> Tuple[...]
```

**¿Qué hace?**
Esta función genera **código intermedio** (cuarta fase). El código de tres direcciones es una representación intermedia que facilita la generación de código máquina posterior.

**Formato**: Cada instrucción tiene la forma:
```
destino = operando1 operador operando2
```

**Ejemplo:**
Para `3 + 4 * 2`:
1. Primero se evalúa `4 * 2`:
   ```
   t1 = dir_2 * dir_3
   ```
2. Luego se evalúa `3 + t1`:
   ```
   t2 = dir_1 + t1
   ```
3. El resultado final está en `t2`

**Características:**
- Usa variables temporales (`t1`, `t2`, `t3`, ...) para almacenar resultados intermedios
- Usa las direcciones de la tabla de símbolos (`dir_1`, `dir_2`, ...) para referenciar los operandos
- Respeta el orden de evaluación determinado por el AST

---

### 8. Clase ArithmeticCompiler

```python
class ArithmeticCompiler:
    def compilar(self, expresion: str) -> Dict[str, object]
```

**¿Qué hace?**
Esta clase **orquesta todas las fases** del compilador en orden:

1. **Análisis Léxico**: Convierte la expresión en tokens
2. **Análisis Sintáctico**: Construye el AST
3. **Análisis Semántico**: Genera las tablas de símbolos y tipos
4. **Generación de Código**: Produce el código de tres direcciones

**Retorna un diccionario** con todos los resultados:
- `tokens`: Lista de tokens generados
- `ast`: Árbol de sintaxis abstracta
- `tabla_simbolos`: Tabla de símbolos
- `tabla_tipos`: Tabla de tipos
- `codigo_tres_direcciones`: Lista de instrucciones de tres direcciones
- `resultado`: Variable temporal donde queda el resultado final

---

### 9. Funciones de Formateo

```python
def formatear_tokens(tokens: List[Token]) -> str
def formatear_ast(nodo: ASTNode, nivel: int = 0) -> str
```

**¿Qué hacen?**
Convierten las estructuras de datos internas en **representaciones textuales legibles** para mostrar al usuario:

- `formatear_tokens()`: Convierte la lista de tokens en una cadena como:
  ```
  <NUMBER, 3> <SUM> <NUMBER, 4> <MUL> <NUMBER, 2>
  ```

- `formatear_ast()`: Convierte el AST en una representación indentada:
  ```
  Operador('+')
    Número(3)
    Operador('*')
      Número(4)
      Número(2)
  ```

---

### 10. Interfaz Web (HTML/JavaScript)

**¿Qué hace?**
El archivo `index.html` contiene:

1. **Interfaz de usuario**: Formulario donde el usuario ingresa la expresión
2. **Visualización de resultados**: Muestra tokens, AST (tanto texto como gráfico), tablas semánticas y código de tres direcciones
3. **Manejo de errores**: Resalta visualmente dónde ocurrió el error en la expresión
4. **Visualización interactiva del AST**: Permite navegar paso a paso la construcción del árbol

**Características especiales:**
- **Visualización gráfica del AST**: Usa SVG para dibujar el árbol de forma visual
- **Navegación paso a paso**: Botones para ver cómo se construye el AST gradualmente
- **Resaltado de errores**: Muestra exactamente qué carácter causó el error

---

## Flujo Completo de Ejecución

Para la expresión `3 + 4 * 2`:

1. **Entrada**: `"3 + 4 * 2"`

2. **Análisis Léxico (Lexer)**:
   ```
   [NUMBER(3), SUM(+), NUMBER(4), MUL(*), NUMBER(2)]
   ```

3. **Análisis Sintáctico (Parser)**:
   ```
   AST:
        +
       / \
      3   *
         / \
        4   2
   ```

4. **Análisis Semántico**:
   - Tabla de símbolos: `{3: dir_1, 4: dir_2, 2: dir_3}`
   - Tabla de tipos: Todos son `entero`

5. **Generación de Código**:
   ```
   t1 = dir_2 * dir_3
   t2 = dir_1 + t1
   Resultado final en: t2
   ```

---

## Conceptos Clave Explicados

### ¿Por qué se llama "compilador"?
Un compilador es un programa que traduce código de un lenguaje (código fuente) a otro lenguaje (código objeto o intermedio). En este caso:
- **Lenguaje fuente**: Expresiones aritméticas como `3 + 4 * 2`
- **Lenguaje destino**: Código de tres direcciones como `t1 = dir_2 * dir_3`

### ¿Qué es un token?
Un token es la **unidad mínima con significado** en un lenguaje. Es como las palabras en un idioma: `3` es un token (número), `+` es otro token (operador).

### ¿Por qué usar un AST?
El AST representa la **estructura jerárquica** de la expresión, respetando la precedencia de operadores. Es más fácil trabajar con un árbol que con una cadena de texto plana.

### ¿Qué es el código de tres direcciones?
Es un **código intermedio** que facilita la generación de código máquina. Cada instrucción tiene:
- Un destino (donde se guarda el resultado)
- Dos operandos (los valores que se operan)
- Un operador (la operación a realizar)

---

## Ejemplos de Uso

### Ejemplo 1: Expresión simple
**Entrada**: `5 + 3`
**Tokens**: `<NUMBER, 5> <SUM> <NUMBER, 3>`
**AST**: 
```
Operador('+')
  Número(5)
  Número(3)
```
**Código de tres direcciones**:
```
t1 = dir_1 + dir_2
Resultado final en: t1
```

### Ejemplo 2: Con paréntesis
**Entrada**: `(3 + 4) * 2`
**Tokens**: `<PAREN_IZ> <NUMBER, 3> <SUM> <NUMBER, 4> <PAREN_D> <MUL> <NUMBER, 2>`
**AST**:
```
Operador('*')
  Operador('+')
    Número(3)
    Número(4)
  Número(2)
```
**Código de tres direcciones**:
```
t1 = dir_1 + dir_2
t2 = t1 * dir_3
Resultado final en: t2
```

### Ejemplo 3: Con error
**Entrada**: `3 + @ 5`
**Error**: `LexerError: Caracter no reconocido '@' en la posición 4.`

---

## Ventajas de este Diseño

1. **Modularidad**: Cada fase está separada, facilitando el mantenimiento
2. **Extensibilidad**: Es fácil agregar nuevos operadores o tipos de datos
3. **Claridad**: El código es fácil de entender y seguir
4. **Visualización**: La interfaz web permite ver todo el proceso paso a paso

---

## Posibles Mejoras Futuras

1. **Números negativos**: Agregar soporte para `-5` o `3 + (-2)`
2. **Números decimales**: Permitir expresiones como `3.5 + 2.1`
3. **Más operadores**: Potencia (`^`), módulo (`%`), etc.
4. **Ejecución del código**: Evaluar realmente el código de tres direcciones
5. **Optimización**: Simplificar expresiones como `3 + 0` o `5 * 1`

---

## Conclusión

Este simulador demuestra los **conceptos fundamentales** de un compilador de manera didáctica y visual. Aunque es simple, implementa las fases principales que todo compilador real debe tener: análisis léxico, sintáctico, semántico y generación de código. Es una excelente herramienta educativa para entender cómo funcionan los compiladores por dentro.

