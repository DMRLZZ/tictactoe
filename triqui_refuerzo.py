#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# DECLARACIÓN DE USO DE INTELIGENCIA ARTIFICIAL: usamos Codex y Claude Code como apoyo
# para el desarrollo de este código. Los autores lo revisaron, lo ejecutaron y verificaron
# sus resultados (30.000 partidas: 99,17 % de victorias como X y 81,63 % como O
# contra un rival aleatorio).
"""
TRIQUI CON APRENDIZAJE POR REFUERZO (TD, aprendizaje por diferencias temporales)

Basado en la idea del ejemplo 1.5 de Sutton y Barto (2.ª edición):
- Cada estado tiene un valor V(s), estimación de probabilidad de ganar.
- Inicialmente V(s)=0.5 para estados no terminales, 1 para victoria, 0 para
  derrota/empate. Los terminales se consideran valores fijos.
- Política epsilon-greedy: casi siempre elige el movimiento de mayor V(s').
- Actualización: V(s) <- V(s) + alpha * (V(s') - V(s)).
- Las jugadas exploratorias no generan la actualización TD de esa jugada.

Adaptación explícita: en lugar de un aprendiz contra un rival fijo, dos
aprendices (X y O) entrenan mediante AUTOJUEGO. Cada uno mantiene su propia
V de estados DESPUÉS de sus movimientos (afterstates). Entre dos afterstates
hay una respuesta del rival. Se actualiza también al terminar una partida por
victoria/derrota/empate. El rival aleatorio se usa SOLO para medir resultados.

Dependencias: matplotlib (solo para las gráficas); Python 3.9+.
Ejecutar: python triqui_refuerzo.py
Opciones: python triqui_refuerzo.py --partidas 60000 --evaluacion 3000
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

Tablero = Tuple[int, ...]  # 9 celdas: 1=X, -1=O, 0=libre
VACIO: Tablero = (0,) * 9
LINEAS = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)


def resultado(tablero: Tablero) -> Optional[int]:
    """None: continúa; 1 gana X; -1 gana O; 0: empate."""
    for a, b, c in LINEAS:
        if tablero[a] != 0 and tablero[a] == tablero[b] == tablero[c]:
            return tablero[a]
    return 0 if 0 not in tablero else None


def movimientos_legales(tablero: Tablero) -> List[int]:
    return [i for i, casilla in enumerate(tablero) if casilla == 0]


def colocar(tablero: Tablero, indice: int, ficha: int) -> Tablero:
    if tablero[indice] != 0:
        raise ValueError(f"Casilla ocupada: {indice}")
    nuevo = list(tablero)
    nuevo[indice] = ficha
    return tuple(nuevo)


def imprimir_tablero(tablero: Tablero) -> None:
    simbolos = {1: 'X', -1: 'O', 0: '·'}
    for fila in range(3):
        print(' ' + ' | '.join(simbolos[c] for c in tablero[3*fila:3*fila+3]))
        if fila != 2:
            print('-----------')


class AgenteTD:
    """Aprendiz tabular por TD con política epsilon-greedy."""

    def __init__(self, ficha: int, alpha: float, epsilon: float, rng: random.Random):
        self.ficha = ficha
        self.alpha = alpha
        self.epsilon = epsilon
        self.rng = rng
        self.valores: Dict[Tablero, float] = {}
        self.estado_anterior: Optional[Tablero] = None
        self.actualizaciones = 0
        self.exploraciones = 0

    def valor(self, tablero: Tablero) -> float:
        fin = resultado(tablero)
        if fin is not None:
            return 1.0 if fin == self.ficha else 0.0
        return self.valores.get(tablero, 0.5)

    def iniciar_partida(self) -> None:
        self.estado_anterior = None

    def elegir(self, tablero: Tablero, entrenamiento: bool) -> Tuple[int, Tablero, bool]:
        candidatos = [(j, colocar(tablero, j, self.ficha)) for j in movimientos_legales(tablero)]
        mejor_valor = max(self.valor(posterior) for _, posterior in candidatos)
        optimos = [(j, posterior) for j, posterior in candidatos
                   if abs(self.valor(posterior) - mejor_valor) < 1e-12]
        elegido_greedy = self.rng.choice(optimos)
        # El libro describe explorar mediante movimientos alternativos.
        alternativas = [par for par in candidatos if par != elegido_greedy]
        explorar = bool(entrenamiento and alternativas and self.rng.random() < self.epsilon)
        if explorar:
            indice, siguiente = self.rng.choice(alternativas)
            self.exploraciones += 1
        else:
            indice, siguiente = elegido_greedy
        return indice, siguiente, not explorar

    def actualizar(self, origen: Tablero, objetivo: float) -> None:
        if resultado(origen) is not None:
            return  # Terminales tienen V fija: victoria=1, derrota/empate=0.
        actual = self.valor(origen)
        self.valores[origen] = actual + self.alpha * (objetivo - actual)
        self.actualizaciones += 1

    def observar_movimiento(self, posterior: Tablero, greedy: bool) -> None:
        # TD entre dos turnos del MISMO jugador, incluyendo respuesta rival.
        if greedy and self.estado_anterior is not None:
            self.actualizar(self.estado_anterior, self.valor(posterior))
        self.estado_anterior = posterior

    def terminar_partida(self, desenlace: int) -> None:
        # Al finalizar ya conocemos el resultado incluso si el rival jugó último.
        # Es una adaptación para propagar señales terminales a los afterstates.
        if self.estado_anterior is not None:
            recompensa = 1.0 if desenlace == self.ficha else 0.0
            self.actualizar(self.estado_anterior, recompensa)
        self.estado_anterior = None


@dataclass
class Estadisticas:
    ganadas: int = 0
    empatadas: int = 0
    perdidas: int = 0

    @property
    def total(self) -> int:
        return self.ganadas + self.empatadas + self.perdidas

    def porcentajes(self) -> dict:
        n = self.total
        return {
            'ganadas': round(100 * self.ganadas / n, 2),
            'empatadas': round(100 * self.empatadas / n, 2),
            'perdidas': round(100 * self.perdidas / n, 2),
        }


def partida_entrenamiento(x: AgenteTD, o: AgenteTD) -> int:
    tablero = VACIO
    turno = 1
    agentes = {1: x, -1: o}
    for agente in agentes.values():
        agente.iniciar_partida()
    while True:
        agente = agentes[turno]
        _, tablero, greedy = agente.elegir(tablero, entrenamiento=True)
        agente.observar_movimiento(tablero, greedy)
        fin = resultado(tablero)
        if fin is not None:
            for a in agentes.values():
                a.terminar_partida(fin)
            return fin
        turno *= -1


def partida_contra_aleatorio(agente: AgenteTD, rng: random.Random) -> int:
    """Devuelve 1 si gana agente, 0 si empata, -1 si pierde."""
    tablero = VACIO
    turno = 1  # X siempre empieza; agente puede jugar X u O
    while True:
        if turno == agente.ficha:
            _, tablero, _ = agente.elegir(tablero, entrenamiento=False)
        else:
            tablero = colocar(tablero, rng.choice(movimientos_legales(tablero)), turno)
        fin = resultado(tablero)
        if fin is not None:
            return 0 if fin == 0 else (1 if fin == agente.ficha else -1)
        turno *= -1


def evaluar(agente: AgenteTD, n: int, semilla: int) -> Estadisticas:
    # No se explora ni se actualiza ningún valor durante la evaluación.
    evaluacion_rng = random.Random(semilla)
    # RNG de la elección greedy separado para no alterar el entrenamiento.
    rng_original = agente.rng
    agente.rng = random.Random(semilla + 99991)
    conteo = Estadisticas()
    try:
        for _ in range(n):
            r = partida_contra_aleatorio(agente, evaluacion_rng)
            if r == 1:
                conteo.ganadas += 1
            elif r == 0:
                conteo.empatadas += 1
            else:
                conteo.perdidas += 1
    finally:
        agente.rng = rng_original
    return conteo


def resumen(nombre: str, est: Estadisticas) -> None:
    p = est.porcentajes()
    print(f"{nombre:20s} | N={est.total:5d} | victorias {p['ganadas']:6.2f}%"
          f" | empates {p['empatadas']:6.2f}% | derrotas {p['perdidas']:6.2f}%")


def hacer_graficas(historia: List[dict], antes: dict, despues: dict, destino: Path) -> None:
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise SystemExit('Instala matplotlib para generar las gráficas: pip install matplotlib') from exc

    # Gráfico 1: ganados durante el entrenamiento, evaluados contra random.
    fig, ax = plt.subplots(figsize=(9, 5.4))
    for ficha, etiqueta in [('X', 'Agente X (primero)'), ('O', 'Agente O (segundo)')]:
        xs = [h['partidas_entrenadas'] for h in historia]
        ys = [h[f'{ficha}_ganadas'] for h in historia]
        ax.plot(xs, ys, marker='o', linewidth=2, label=etiqueta)
    ax.set(title='Aprendizaje TD por autojuego — evaluación contra rival aleatorio',
           xlabel='Partidas de autojuego acumuladas', ylabel='Porcentaje de victorias')
    ax.set_ylim(0, 100)
    ax.grid(alpha=.25)
    ax.legend(loc='lower right')
    fig.tight_layout()
    fig.savefig(destino / 'curva_aprendizaje.png', dpi=170)
    plt.close(fig)

    # Gráfico 2: comparación antes vs. después (4 grupos, tres desenlaces).
    fig, ax = plt.subplots(figsize=(9, 5.4))
    etiquetas = ['X antes', 'X después', 'O antes', 'O después']
    casos = [antes['X'], despues['X'], antes['O'], despues['O']]
    colores = {'ganadas': '#237a57', 'empatadas': '#9e9d24', 'perdidas': '#ba4747'}
    abajo = [0.0] * 4
    for tipo, nombre in [('ganadas', 'Victorias'), ('empatadas', 'Empates'), ('perdidas', 'Derrotas')]:
        vals = [caso.porcentajes()[tipo] for caso in casos]
        ax.bar(etiquetas, vals, bottom=abajo, label=nombre, color=colores[tipo])
        abajo = [a+b for a, b in zip(abajo, vals)]
    ax.set(title='Desempeño contra rival aleatorio: antes y después', ylabel='Porcentaje de partidas', ylim=(0, 110))
    ax.legend(loc='upper center', ncol=3)
    fig.tight_layout()
    fig.savefig(destino / 'comparacion_antes_despues.png', dpi=170)
    plt.close(fig)


def demostrar_jugada(x: AgenteTD) -> None:
    """Ejemplo de acción con un tablero táctico válido: X puede ganar."""
    tablero: Tablero = (1, 1, 0,
                        -1, -1, 0,
                         0, 0, 0)
    print('\nDEMOSTRACIÓN: tablero antes del turno de X')
    imprimir_tablero(tablero)
    posibles = []
    for i in movimientos_legales(tablero):
        despues = colocar(tablero, i, 1)
        posibles.append((i+1, x.valor(despues)))
    print('Casilla (1-9) y V estimado:', posibles)
    indice, nuevo, _ = x.elegir(tablero, entrenamiento=False)
    print(f'X elige casilla {indice+1}:')
    imprimir_tablero(nuevo)
    print('Resultado de esta jugada:', 'X gana' if resultado(nuevo) == 1 else 'partida sigue')


def mostrar_partida(agente: AgenteTD, semilla: int, pausa: float = 0.8) -> int:
    """Una partida del agente entrenado contra el rival aleatorio, jugada a jugada.

    En cada turno del agente se imprime el valor V que le da a cada casilla libre
    (el valor del tablero que quedaría) y la casilla que escoge: la de mayor valor.
    No explora ni aprende: es la política greedy aprendida.
    """
    rng = random.Random(semilla)
    rng_original = agente.rng
    agente.rng = random.Random(semilla + 1)
    nombre = {1: 'X', -1: 'O'}
    yo, rival = nombre[agente.ficha], nombre[-agente.ficha]
    print(f'\nPARTIDA DE DEMOSTRACIÓN: agente entrenado ({yo}) contra rival aleatorio ({rival})')
    print('Casillas numeradas así:  1 | 2 | 3   /   4 | 5 | 6   /   7 | 8 | 9')
    tablero, turno, jugada = VACIO, 1, 1
    try:
        while True:
            time.sleep(pausa)
            if turno == agente.ficha:
                valores = {i: agente.valor(colocar(tablero, i, turno)) for i in movimientos_legales(tablero)}
                print(f'\nJugada {jugada} · turno del agente ({yo}). Valor de cada casilla libre:')
                celdas = [f'{valores[i]:.2f}' if i in valores else f' {nombre[tablero[i]]}  '
                          for i in range(9)]
                for fila in range(3):
                    print('   ' + ' | '.join(celdas[3 * fila:3 * fila + 3]))
                indice, tablero, _ = agente.elegir(tablero, entrenamiento=False)
                print(f'   -> escoge la casilla {indice + 1} (la de mayor valor)')
            else:
                indice = rng.choice(movimientos_legales(tablero))
                tablero = colocar(tablero, indice, turno)
                print(f'\nJugada {jugada} · el rival aleatorio ({rival}) juega en la casilla {indice + 1}')
            imprimir_tablero(tablero)
            fin = resultado(tablero)
            if fin is not None:
                texto = 'empate' if fin == 0 else ('gana el agente' if fin == agente.ficha else 'gana el rival')
                print(f'\nResultado: {texto}.')
                return fin
            turno *= -1
            jugada += 1
    finally:
        agente.rng = rng_original


def main() -> None:
    p = argparse.ArgumentParser(description='Triqui TD(0) con autojuego y evidencia.')
    p.add_argument('--partidas', type=int, default=30000, help='Número de partidas de autojuego')
    p.add_argument('--evaluacion', type=int, default=3000, help='Partidas por evaluación y ficha')
    p.add_argument('--cada', type=int, default=5000, help='Intervalo de evaluación')
    p.add_argument('--alpha', type=float, default=.25, help='Tasa de aprendizaje TD')
    p.add_argument('--epsilon', type=float, default=.10, help='Probabilidad de explorar')
    p.add_argument('--semilla', type=int, default=2026, help='Semilla para reproducir resultados')
    p.add_argument('--salida', type=Path, default=Path('resultados_triqui'), help='Carpeta de resultados')
    p.add_argument('--partida', action='store_true',
                   help='Al final, muestra una partida del agente X entrenado contra el rival aleatorio')
    p.add_argument('--pausa', type=float, default=0.8, help='Segundos entre jugadas en --partida')
    a = p.parse_args()
    if a.partidas <= 0 or a.evaluacion <= 0 or a.cada <= 0:
        p.error('partidas, evaluacion y cada deben ser > 0')
    if not (0 < a.alpha <= 1 and 0 <= a.epsilon <= 1):
        p.error('Se requiere 0 < alpha <= 1 y 0 <= epsilon <= 1')
    a.salida.mkdir(parents=True, exist_ok=True)

    x = AgenteTD(1, a.alpha, a.epsilon, random.Random(a.semilla+1))
    o = AgenteTD(-1, a.alpha, a.epsilon, random.Random(a.semilla+2))
    agentes = {'X': x, 'O': o}
    print('SECCIÓN 1.5 — TRIQUI CON APRENDIZAJE TD POR AUTOJUEGO')
    print(f'Parámetros: alpha={a.alpha}, epsilon={a.epsilon}, partidas={a.partidas}, semilla={a.semilla}')
    print('\nANTES DEL ENTRENAMIENTO (política greedy con V(s)=0.5):')
    antes = {f: evaluar(ag, a.evaluacion, a.semilla+100+j)
             for j, (f, ag) in enumerate(agentes.items())}
    for f, est in antes.items():
        resumen(f'Agente {f}', est)

    historia: List[dict] = []
    def registrar(n: int) -> None:
        e = {f: evaluar(ag, min(a.evaluacion, 1000), a.semilla+500+j)
             for j, (f, ag) in enumerate(agentes.items())}
        fila = {'partidas_entrenadas': n}
        for f, st in e.items():
            for tipo, porcentaje in st.porcentajes().items():
                fila[f'{f}_{tipo}'] = porcentaje
        historia.append(fila)
        if n > 0:
            print(f"  tras {n:6d} partidas | X gana {fila['X_ganadas']:5.1f}%"
                  f" | O gana {fila['O_ganadas']:5.1f}%")

    registrar(0)
    print('\nENTRENAMIENTO:')
    for n in range(1, a.partidas+1):
        partida_entrenamiento(x, o)
        if n % a.cada == 0 or n == a.partidas:
            registrar(n)

    print('\nDESPUÉS DEL ENTRENAMIENTO (misma configuración de evaluación):')
    despues = {f: evaluar(ag, a.evaluacion, a.semilla+100+j)
               for j, (f, ag) in enumerate(agentes.items())}
    for f, est in despues.items():
        resumen(f'Agente {f}', est)
        print(f'  Estados aprendidos: {len(agentes[f].valores)}; actualizaciones: {agentes[f].actualizaciones};'
              f' exploraciones: {agentes[f].exploraciones}')

    hacer_graficas(historia, antes, despues, a.salida)
    with (a.salida / 'curva_aprendizaje.csv').open('w', newline='', encoding='utf-8') as fh:
        escritor = csv.DictWriter(fh, fieldnames=list(historia[0]))
        escritor.writeheader()
        escritor.writerows(historia)
    reporte = {
        'parametros': {k: v for k, v in vars(a).items() if k not in ('partida', 'pausa')} | {'salida': str(a.salida)},
        'antes': {f: st.porcentajes() | {'n': st.total} for f, st in antes.items()},
        'despues': {f: st.porcentajes() | {'n': st.total} for f, st in despues.items()},
        'estados_aprendidos': {f: len(ag.valores) for f, ag in agentes.items()},
        'nota': 'Evaluación greedy, epsilon=0, sin actualizaciones contra rival aleatorio. '
                'Empates y derrotas tienen utilidad 0 (según ejemplo del libro).',
    }
    (a.salida / 'metricas.json').write_text(json.dumps(reporte, ensure_ascii=False, indent=2), encoding='utf-8')
    demostrar_jugada(x)
    if a.partida:
        mostrar_partida(x, a.semilla + 7, a.pausa)
    print('\nArchivos guardados en:', a.salida.resolve())
    print('  curva_aprendizaje.png, comparacion_antes_despues.png,')
    print('  curva_aprendizaje.csv, metricas.json')


if __name__ == '__main__':
    main()
