"""Reservas con estados, validaciones y control de excepciones."""
from abc import ABC, abstractmethod
from servicios_y_excepciones import Servicio, ErrorSistemaFJ, logger_fj
from cliente import Cliente

class Entidad(ABC):
    @abstractmethod
    def resumen(self):
        """Descripción de la entidad."""

class ReservaError(ErrorSistemaFJ):
    """Operación de reserva inválida."""

class Reserva(Entidad):
    def __init__(self, codigo, cliente, servicio, duracion):
        if not isinstance(cliente, Cliente):
            raise ReservaError('El cliente debe ser una instancia de Cliente.')
        if not isinstance(servicio, Servicio):
            raise ReservaError('El servicio debe ser una instancia de Servicio.')
        if not isinstance(codigo, str) or not codigo.strip():
            raise ReservaError('El código de reserva es obligatorio.')
        if isinstance(duracion, bool) or not isinstance(duracion, (int,float)) or duracion <= 0:
            raise ReservaError('La duración debe ser numérica y positiva.')
        self.codigo, self.cliente, self.servicio = codigo.strip(), cliente, servicio
        self.duracion = duracion
        self.estado = 'pendiente'

    def resumen(self):
        return f'Reserva {self.codigo}: {self.cliente.nombre}, {self.servicio.nombre}, estado={self.estado}'

    def procesar(self, descuento=0, impuesto=0):
        try:
            if self.estado == 'cancelada':
                raise ReservaError('No se puede procesar una reserva cancelada.')
            costo = self.servicio.calcular_costo(self.duracion, descuento, impuesto)
        except ErrorSistemaFJ as error:
            logger_fj.error('Error al procesar reserva %s: %s', self.codigo, error)
            raise
        else:
            logger_fj.info('Reserva %s procesada: %.2f', self.codigo, costo)
            return costo
        finally:
            logger_fj.info('Finalizó intento de procesamiento %s', self.codigo)

    def confirmar(self):
        if self.estado != 'pendiente':
            raise ReservaError('Solo se pueden confirmar reservas pendientes.')
        total = self.procesar()
        self.estado = 'confirmada'
        logger_fj.info('Reserva %s confirmada', self.codigo)
        return total

    def cancelar(self):
        if self.estado == 'cancelada':
            raise ReservaError('La reserva ya fue cancelada.')
        self.estado = 'cancelada'
        logger_fj.info('Reserva %s cancelada', self.codigo)
