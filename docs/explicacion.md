# Explicación de la implementación de Triqui

## 1. Problema y modelo

El agente aprende a elegir una casilla en un tablero de 3×3, intentando maximizar su probabilidad de ganar. El tablero se representa mediante una tupla de 9 valores: `1` es X, `-1` es O y `0` representa una casilla vacía.

El estado es el tablero actual; las acciones disponibles son las casillas libres; la transición incorpora una jugada del agente y, para su siguiente decisión, la respuesta del adversario.

## 2. Estimación de valor

Cada jugador mantiene su propia tabla de valores, `AgenteTD.valores`. Se utilizan valores de estado posterior a la jugada (*afterstates*). Al inicio, `V(s)=0.5` para estados no terminales no visitados; los terminales tienen valores fijos: `1` si gana el jugador y `0` si empata o pierde.

La acción no se selecciona consultando un buscador minimax. Se calcula el valor estimado del tablero resultante de cada casilla legal y se elige uno de mayor valor, rompiendo empates al azar.

## 3. Exploración y aprendizaje

Durante el entrenamiento, la política ε-greedy elige con alta probabilidad una jugada de máximo valor, pero a veces explora una alternativa. El algoritmo usa una tasa de aprendizaje `alpha=0.25` y una probabilidad de exploración `epsilon=0.10` por defecto.

La actualización TD utilizada es:

```text
V(s) = V(s) + alpha * (V(siguiente) - V(s))
```

El método `observar_movimiento` enlaza estados posteriores a jugadas consecutivas del mismo agente; el método `terminar_partida` transmite además la señal terminal cuando se conoce el desenlace. Esto último forma parte de la adaptación para dos aprendices.

## 4. Autojuego y evaluación

En cada episodio, un agente juega X y otro O. Ambos aprenden independientemente. Cada determinado número de episodios se congelan los valores para evaluar a cada rol contra un oponente aleatorio.

Durante la evaluación se desactiva la exploración y no se actualizan valores. Los porcentajes se calculan sobre partidas reales, con semillas fijadas para reproducir el experimento.

**Resultados de referencia (semilla 2026, 30 000 partidas):**

- X: tasa de victorias de 81,97 % antes a 99,17 % después.
- O: tasa de victorias de 52,77 % antes a 81,63 % después.

No confundir tasas de victoria frente a un rival aleatorio con una prueba de juego óptimo. La ventaja de mover primero y la información incorporada en estados terminales son factores relevantes.

## 5. Relación con Bellman y decisiones estocásticas

En clase, los procesos de decisión estocásticos usan estados, acciones, retornos y probabilidades de transición; la ecuación de Bellman incorpora retorno inmediato y valor futuro esperado:

```text
f_t(i) = max_a [ R_t(i,a) + sum_j p_t(j|i,a) f_(t+1)(j) ]
```

En el juego no proporcionamos al agente una matriz de transición del contrincante. En vez de resolver con probabilidades conocidas, ajusta estimaciones de valor observando partidas concretas. **La ecuación de Bellman no es idéntica a la regla de actualización TD**, aunque esta se inspira en su principio de relacionar valores actuales y futuros.

## 6. Estructura relevante del código

- `resultado`: detecta victoria, empate o continuación.
- `movimientos_legales` y `colocar`: reglas de transición del tablero.
- `AgenteTD.valor`: consulta el valor estimado de un estado.
- `AgenteTD.elegir`: política ε-greedy.
- `AgenteTD.actualizar`: actualización por diferencias temporales.
- `partida_entrenamiento`: autojuego de X contra O.
- `evaluar`: prueba congelada contra un adversario aleatorio.
- `hacer_graficas`: gráficas PNG y exportación CSV/JSON.

## 7. Límites y decisiones de implementación

Este proyecto no utiliza aprendizaje profundo, aproximación neuronal ni minimax. Usa un espacio pequeño y tabular: no se espera que generalice a tableros grandes. Explorar contra rivales adversariales nuevos puede reducir el rendimiento observado. La autoevaluación frente a otro rival, como uno que juega óptimamente, sería un experimento adicional válido.

Fuente: Sutton y Barto, *Reinforcement Learning: An Introduction*, 2.ª ed., capítulo 1, §1.5; apuntes de procesos de decisión estocásticos de Optimización (2026-II).
