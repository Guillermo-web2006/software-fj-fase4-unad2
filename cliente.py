"""Módulo de clientes para Software FJ (Fase 4, UNAD)."""
import re


class ClienteInvalidoError(ValueError):
    """Indica que un dato del cliente no cumple las validaciones."""


class ClienteDuplicadoError(ValueError):
    """Indica que ya existe un cliente con la identificación indicada."""


class Cliente:
    """Representa un cliente y encapsula sus datos personales."""

    def __init__(self, identificacion: str, nombre: str, correo: str, telefono: str):
        self.__identificacion = self._texto(identificacion, "Identificación")
        self.__nombre = self._texto(nombre, "Nombre")
        self.__correo = self._validar_correo(correo)
        self.__telefono = self._validar_telefono(telefono)

    @staticmethod
    def _texto(valor, campo):
        if not isinstance(valor, str) or not valor.strip():
            raise ClienteInvalidoError(f"{campo} debe ser un texto no vacío")
        return valor.strip()

    @classmethod
    def _validar_correo(cls, correo):
        correo = cls._texto(correo, "Correo")
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", correo):
            raise ClienteInvalidoError("El correo no tiene un formato válido")
        return correo

    @classmethod
    def _validar_telefono(cls, telefono):
        telefono = cls._texto(telefono, "Teléfono")
        if not re.fullmatch(r"\+?[0-9]{7,15}", telefono):
            raise ClienteInvalidoError("El teléfono debe tener entre 7 y 15 dígitos (puede iniciar con +)")
        return telefono

    @property
    def identificacion(self):
        return self.__identificacion

    @property
    def nombre(self):
        return self.__nombre

    @property
    def correo(self):
        return self.__correo

    @property
    def telefono(self):
        return self.__telefono

    def actualizar_contacto(self, correo=None, telefono=None):
        """Valida primero los cambios para no dejar actualizaciones parciales."""
        nuevo_correo = self.__correo if correo is None else self._validar_correo(correo)
        nuevo_telefono = self.__telefono if telefono is None else self._validar_telefono(telefono)
        self.__correo, self.__telefono = nuevo_correo, nuevo_telefono

    def __repr__(self):
        return f"Cliente(identificacion={self.__identificacion!r}, nombre={self.__nombre!r})"


class GestorClientes:
    """Gestiona clientes en una lista interna, sin base de datos."""

    def __init__(self):
        self.__clientes = []

    def registrar(self, identificacion, nombre, correo, telefono):
        cliente = Cliente(identificacion, nombre, correo, telefono)
        if any(c.identificacion == cliente.identificacion for c in self.__clientes):
            raise ClienteDuplicadoError("Ya existe un cliente con esa identificación")
        self.__clientes.append(cliente)
        return cliente

    def buscar(self, identificacion):
        return next((c for c in self.__clientes if c.identificacion == identificacion), None)

    def listar(self):
        return tuple(self.__clientes)
