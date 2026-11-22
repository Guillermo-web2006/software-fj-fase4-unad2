"""Pruebas automáticas del aporte individual: gestión de clientes."""
import unittest
from cliente import ClienteInvalidoError, ClienteDuplicadoError, GestorClientes


class PruebasClientes(unittest.TestCase):
    def setUp(self):
        self.gestor = GestorClientes()

    def test_registro_valido(self):
        cliente = self.gestor.registrar("1001", "Ana Pérez", "ana@example.com", "3001234567")
        self.assertEqual(cliente.nombre, "Ana Pérez")
        self.assertEqual(len(self.gestor.listar()), 1)

    def test_nombre_vacio(self):
        with self.assertRaises(ClienteInvalidoError):
            self.gestor.registrar("1001", " ", "ana@example.com", "3001234567")

    def test_correo_invalido(self):
        with self.assertRaises(ClienteInvalidoError):
            self.gestor.registrar("1001", "Ana", "correo_invalido", "3001234567")

    def test_telefono_invalido(self):
        with self.assertRaises(ClienteInvalidoError):
            self.gestor.registrar("1001", "Ana", "ana@example.com", "abc")

    def test_duplicado(self):
        self.gestor.registrar("1001", "Ana", "ana@example.com", "3001234567")
        with self.assertRaises(ClienteDuplicadoError):
            self.gestor.registrar("1001", "Luis", "luis@example.com", "3009876543")

    def test_busqueda(self):
        self.gestor.registrar("1001", "Ana", "ana@example.com", "3001234567")
        self.assertEqual(self.gestor.buscar("1001").nombre, "Ana")
        self.assertIsNone(self.gestor.buscar("9999"))

    def test_actualizacion_valida(self):
        cliente = self.gestor.registrar("1001", "Ana", "ana@example.com", "3001234567")
        cliente.actualizar_contacto(correo="nuevo@example.com")
        self.assertEqual(cliente.correo, "nuevo@example.com")

    def test_actualizacion_invalida_no_modifica(self):
        cliente = self.gestor.registrar("1001", "Ana", "ana@example.com", "3001234567")
        with self.assertRaises(ClienteInvalidoError):
            cliente.actualizar_contacto(correo="nuevo@example.com", telefono="mal")
        self.assertEqual(cliente.correo, "ana@example.com")


if __name__ == "__main__":
    unittest.main(verbosity=2)
