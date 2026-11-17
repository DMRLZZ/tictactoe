# Plan de exposición individual — 31 minutos y 30 segundos

**Entrega oficial:** video + código, a más tardar el viernes 20 de noviembre de 2026 a las 9:00 p. m. La duración permitida es de 25 a 35 minutos; debes aparecer en cámara y explicar, no limitarte a leer diapositivas.

| Intervalo | Duración | Contenido |
| --- | --- | --- |
| 00:00–01:00 | 1:00 | Pregunta motivadora: ¿cómo aprende una máquina a jugar Triqui sin recibir la mejor acción de cada tablero? |
| 01:00–04:30 | 3:30 | Qué es RL, problemas secuenciales, recompensas y diferencia con aprendizaje supervisado y no supervisado |
| 04:30–07:30 | 3:00 | Ejemplos: bandido de varios brazos, robot en laberinto y péndulo invertido |
| 07:30–12:00 | 4:30 | Agente, entorno, estados, acciones, recompensas, política y valores; ejemplificar cada uno en Triqui |
| 12:00–15:30 | 3:30 | Exploración frente a explotación (ε-greedy), ventajas y límites del RL |
| 15:30–17:30 | 2:00 | Breve historia: ensayo y error, Bellman, diferencias temporales y aplicaciones modernas |
| 17:30–23:00 | 5:30 | Relación con procesos de decisión estocásticos del curso, Bellman y actualización TD |
| 23:00–24:30 | 1:30 | **Pantalla compartida:** estructura del código y reglas del tablero |
| 24:30–26:00 | 1:30 | **Pantalla compartida:** métodos elegir, observar_movimiento y actualizar |
| 26:00–27:30 | 1:30 | **Ejecutar:** `python triqui_refuerzo.py` (preparar dependencias antes de grabar) |
| 27:30–29:00 | 1:30 | **Mostrar gráficas:** `curva_aprendizaje.png` y `comparacion_antes_despues.png` |
| 29:00–30:00 | 1:00 | Interpretar porcentajes, limitaciones del oponente aleatorio y ventaja de X |
| 30:00–31:30 | 1:30 | Conclusiones, referencias y declaración explícita del apoyo de ChatGPT |

## Ideas para explicar con tus propias palabras

- **Inicio:** «¿Qué pasaría si dejamos que un agente juegue miles de partidas y aprenda de los resultados en vez de programarle una estrategia ganadora?».
- **RL:** observar un estado, decidir, actuar y aprender de recompensas y experiencias.
- **Valor frente a recompensa:** la recompensa indica lo ocurrido, mientras el valor estima qué tan favorable es un estado para el resultado futuro.
- **Exploración/explotación:** elegir siempre lo conocido impide descubrir alternativas prometedoras.
- **Bellman:** el valor de una decisión depende tanto de hoy como del futuro; TD aproxima ese razonamiento mediante experiencias, sin necesitar toda la matriz de probabilidades.
- **Código:** mostrar el flujo y no leer línea por línea. Describir qué cambia tras cada episodio.
- **Evidencia:** comparar antes/después y explicar por qué el rival aleatorio es una prueba limitada y reproducible.

## Preparación técnica

1. Ejecutar `python -m pip install -r requirements.txt`.
2. Ejecutar `python -m unittest discover -s tests -v`.
3. Ejecutar `python triqui_refuerzo.py` y revisar que se creen todos los archivos en `resultados_triqui/`.
4. Mostrar código, consola y ambas gráficas en pantalla compartida manteniendo cámara encendida.
5. Comprobar que el archivo de video final se abre, se escucha y se reproduce completo.

## Rúbrica oficial

| Criterio | Puntos |
| --- | ---: |
| Comprensión del tema | 25 |
| Implementación y evidencia | 25 |
| Relación con procesos estocásticos y Bellman | 15 |
| Claridad | 15 |
| Ejemplos adicionales | 10 |
| Manejo del tiempo | 10 |
| **Total** | **100** |

**Fuente:** Universidad Externado de Colombia, *Examen Final de Optimización 2026-II*, `3-EFCDOP.pdf`, páginas 1–2.
