"""Pruebas básicas del juego, aprendizaje y evaluación sin cambios de valores."""
import random
import unittest

from triqui_refuerzo import (
    AgenteTD, VACIO, colocar, evaluar, movimientos_legales,
    partida_entrenamiento, resultado,
)


class TestReglas(unittest.TestCase):
    def test_tablero_vacio(self):
        self.assertIsNone(resultado(VACIO))
        self.assertEqual(movimientos_legales(VACIO), list(range(9)))

    def test_victorias_filas_columnas_diagonales(self):
        ejemplos = [
            (1, 1, 1, -1, -1, 0, 0, 0, 0),
            (-1, 1, 0, -1, 1, 0, -1, 0, 0),
            (1, -1, 0, 0, 1, -1, 0, 0, 1),
        ]
        self.assertEqual([resultado(t) for t in ejemplos], [1, -1, 1])

    def test_empate(self):
        self.assertEqual(resultado((1, -1, 1, 1, -1, -1, -1, 1, 1)), 0)

    def test_colocar_no_modifica_original(self):
        nuevo = colocar(VACIO, 4, 1)
        self.assertEqual(VACIO, (0,) * 9)
        self.assertEqual(nuevo[4], 1)
        self.assertEqual(len(movimientos_legales(nuevo)), 8)
        with self.assertRaises(ValueError):
            colocar(nuevo, 4, -1)


class TestAprendizaje(unittest.TestCase):
    def crear(self, ficha, semilla):
        return AgenteTD(ficha, alpha=0.25, epsilon=0.1, rng=random.Random(semilla))

    def test_valores_iniciales_y_terminales(self):
        agente = self.crear(1, 5)
        self.assertEqual(agente.valor(VACIO), 0.5)
        self.assertEqual(agente.valor((1, 1, 1, -1, -1, 0, 0, 0, 0)), 1)
        self.assertEqual(agente.valor((-1, -1, -1, 1, 1, 0, 0, 0, 0)), 0)

    def test_actualizacion_temporal(self):
        agente = self.crear(1, 5)
        estado = colocar(VACIO, 0, 1)
        agente.actualizar(estado, 1)
        self.assertAlmostEqual(agente.valor(estado), 0.625)
        self.assertEqual(agente.actualizaciones, 1)

    def test_evaluacion_no_entrena(self):
        agente = self.crear(1, 5)
        resultados = evaluar(agente, 40, 2026)
        self.assertEqual(resultados.total, 40)
        self.assertEqual(agente.actualizaciones, 0)
        self.assertEqual(agente.exploraciones, 0)
        self.assertEqual(len(agente.valores), 0)

    def test_autojuego_termina(self):
        x, o = self.crear(1, 10), self.crear(-1, 11)
        for _ in range(20):
            self.assertIn(partida_entrenamiento(x, o), (-1, 0, 1))
        self.assertGreater(x.actualizaciones + o.actualizaciones, 0)


if __name__ == "__main__":
    unittest.main()
