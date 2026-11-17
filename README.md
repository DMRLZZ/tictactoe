# Tic-Tac-Toe con aprendizaje por refuerzo (TD)

Implementación educativa de **Triqui (Tic-Tac-Toe)** inspirada en la sección **1.5, Tic-Tac-Toe**, del capítulo 1 de Sutton y Barto, *Reinforcement Learning: An Introduction* (2.ª edición).

Proyecto del examen final de **Optimización — Ciencia de Datos, Universidad Externado de Colombia (2026-II)**.

## Ejecución rápida

Se necesita **Python 3.9 o superior**.

```bash
python -m pip install -r requirements.txt
python triqui_refuerzo.py
```

Por defecto se ejecutan **30 000 partidas de autojuego**, con tasa de aprendizaje `alpha=0.25`, exploración `epsilon=0.10`, y semilla `2026`. Se evalúa cada rol (X y O) contra un adversario aleatorio, tanto antes como después del entrenamiento, usando **3 000 partidas** en cada evaluación final.

```bash
python triqui_refuerzo.py --partidas 60000 --evaluacion 3000 --cada 5000
python -m unittest discover -s tests -v
```

Puedes ajustar: `--partidas`, `--evaluacion`, `--cada`, `--alpha`, `--epsilon`, `--semilla` y `--salida`.

## Qué hace el programa

1. Representa el tablero como nueve celdas: `1` para X, `-1` para O y `0` para vacío.
2. Inicializa `V(s)=0.5` para estados no terminales, `1` para victoria y `0` para derrota o empate.
3. Entrena **dos agentes TD tabulares** de forma independiente por **autojuego**; uno juega siempre X y otro O.
4. Selecciona jugadas con política **ε-greedy** durante el entrenamiento y únicamente greedy en evaluación.
5. Actualiza los valores de los estados posteriores a cada jugada (*afterstates*) usando diferencias temporales:
   
   `V(s) ← V(s) + α [V(s') − V(s)]`
6. Guarda una curva de aprendizaje, una comparación de desempeño antes/después, estadísticas en CSV y métricas JSON.

No se utiliza minimax ni reglas estratégicas manuales: el agente aprende estimaciones de estado a partir de partidas.

**Adaptación respecto del libro:** el ejemplo de Sutton y Barto presenta un aprendiz ante un oponente; aquí se usan **dos aprendices entrenados por autojuego**, con actualización terminal y una evaluación adicional ante un rival aleatorio. Es una implementación inspirada en el procedimiento de la sección 1.5, **no una reproducción literal** de toda su configuración.

## Evidencia experimental

Una ejecución reproducible con semilla `2026`, 30 000 partidas de autojuego y 3 000 partidas por rol para la comparación antes/después obtuvo:

| Rol | Victorias antes | Victorias después | Evaluación |
| --- | ---: | ---: | --- |
| X (primero) | 81.97 % | **99.17 %** | Contra jugador aleatorio |
| O (segundo) | 52.77 % | **81.63 %** | Contra jugador aleatorio |

Estos porcentajes no prueban que el agente sea invencible: reflejan únicamente el desempeño contra un **rival que juega aleatoriamente**. X tiene ventaja por jugar primero. Los valores iniciales de estados terminales ya contienen información básica sobre ganar, perder y empatar.

Los datos originales de la curva se encuentran en [`evidencias/curva_aprendizaje.csv`](evidencias/curva_aprendizaje.csv). Los gráficos de evidencia en formato SVG están en [`evidencias/`](evidencias/); al ejecutar Python se vuelven a generar los PNG originales en `resultados_triqui/`.

## Estructura del repositorio

```text
triqui_refuerzo.py          # Implementación, evaluación y exportación
requirements.txt            # Dependencia de gráficos
tests/test_triqui.py        # Pruebas automáticas con unittest
evidencias/
  curva_aprendizaje.csv     # Mediciones por etapas
  metricas.json             # Comparación final y parámetros
  curva_aprendizaje.svg     # Curva visible en GitHub
  comparacion.svg           # Antes y después visible en GitHub
docs/
  explicacion.md            # Guía para explicar diseño y resultados
  guion_video.md            # Plan individual del video
  declaracion_ia.md         # Transparencia sobre herramientas de IA
.gitignore                  # Archivos temporales y gráficos regenerables
```

## Referencias

- Richard S. Sutton y Andrew G. Barto. *Reinforcement Learning: An Introduction*, 2.ª edición (2018), capítulo 1, §1.5.
- Universidad Externado de Colombia. *Optimización — Examen Final* (2026-II), archivo `3-EFCDOP.pdf` (enunciado del curso).

## Uso de inteligencia artificial

Se utilizó **ChatGPT (OpenAI)** para apoyar el desarrollo, documentación y organización de la implementación y su evaluación. El estudiante debe **declararlo explícitamente en el video** y verificar personalmente el código y la evidencia. El archivo [`docs/declaracion_ia.md`](docs/declaracion_ia.md) amplía esta información.

## Entrega académica

El enunciado solicita **video de 25–35 minutos más código fuente**, antes del **viernes 20 de noviembre de 2026 a las 9:00 p. m.**, y exige que el estudiante aparezca en cámara. El video **no está incluido** en este repositorio: debe entregarse también por el medio indicado por la asignatura.

