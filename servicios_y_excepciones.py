"""Módulo de excepciones personalizadas, registro en log y servicios de Software FJ."""

from abc import ABC, abstractmethod
import logging


# =====================================================================
# 1. CONFIGURACIÓN DEL ARCHIVO DE LOGS (SIN BASE DE DATOS)
# =====================================================================

def configurar_logger(nombre_archivo: str = "software_fj.log") -> logging.Logger:
    """Configura y devuelve un logger que guarda eventos y errores en un archivo .log."""
    logger = logging.getLogger("SoftwareFJLogger")  # Crea o recupera el logger del proyecto
    logger.setLevel(logging.INFO)  # Registra eventos informativos y errores

    # Evita agregar manejadores duplicados si se importa este archivo varias veces
    if not logger.handlers:
        manejador_archivo = logging.FileHandler(nombre_archivo, mode="a", encoding="utf-8")
        formato = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        manejador_archivo.setFormatter(formato)
        logger.addHandler(manejador_archivo)

    return logger


logger_fj = configurar_logger()


# =====================================================================
# 2. EXCEPCIONES PERSONALIZADAS DEL DOMINIO
# =====================================================================

class ErrorSistemaFJ(Exception):
    """Excepción base para los errores controlados del sistema Software FJ."""


class ParametroServicioInvalidoError(ErrorSistemaFJ):
    """Se lanza cuando un servicio recibe parámetros inválidos o fuera de rango."""


class CalculoCostoError(ErrorSistemaFJ):
    """Se lanza cuando ocurre un fallo al calcular o ajustar el costo de un servicio."""


class ServicioNoDisponibleError(ErrorSistemaFJ):
    """Se lanza cuando se intenta cotizar o usar un servicio no disponible."""


# =====================================================================
# 3. CLASE ABSTRACTA Y SERVICIOS ESPECIALIZADOS (POLIMORFISMO Y SOBRECARGA)
# =====================================================================

class Servicio(ABC):
    """Clase abstracta que define la estructura común de todos los servicios."""

    def __init__(self, codigo: str, nombre: str, tarifa_base: float, disponible: bool = True) -> None:
        # Valida que el código y el nombre existan y no sean espacios en blanco
        if not codigo or not codigo.strip():
            raise ParametroServicioInvalidoError("El código del servicio es obligatorio.")
        if not nombre or not nombre.strip():
            raise ParametroServicioInvalidoError("El nombre del servicio es obligatorio.")
        # Valida que la tarifa base sea positiva
        if tarifa_base <= 0:
            raise ParametroServicioInvalidoError("La tarifa base debe ser mayor que cero.")

        self.codigo = codigo.strip()
        self.nombre = nombre.strip()
        self.tarifa_base = float(tarifa_base)
        self.disponible = bool(disponible)
        # Llama al método sobrescrito de cada subclase para validar sus propios parámetros
        self.validar_parametros()

    @abstractmethod
    def validar_parametros(self) -> None:
        """Valida reglas específicas según el tipo de servicio."""

    @abstractmethod
    def calcular_costo_base(self, cantidad: float) -> float:
        """Calcula el subtotal según la cantidad, horas o días del servicio."""

    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción clara del servicio."""

    def calcular_costo(
        self,
        cantidad: float,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
    ) -> float:
        """
        Sobrecarga mediante parámetros opcionales:
        Permite calcular el costo solo con cantidad, o agregando descuento e impuesto.
        """
        try:
            # Verifica disponibilidad antes de calcular
            if not self.disponible:
                raise ServicioNoDisponibleError(f"El servicio '{self.nombre}' no está disponible.")
            # Valida rangos de descuento e impuesto
            if not (0.0 <= descuento_pct < 100.0):
                raise ParametroServicioInvalidoError("El descuento debe estar entre 0 y 99.9%.")
            if impuesto_pct < 0.0:
                raise ParametroServicioInvalidoError("El impuesto no puede ser negativo.")

            subtotal = self.calcular_costo_base(cantidad)  # Ejecuta la versión de cada subclase
            con_descuento = subtotal * (1.0 - descuento_pct / 100.0)
            total = con_descuento * (1.0 + impuesto_pct / 100.0)
            return round(total, 2)
        except ErrorSistemaFJ:
            # Propaga las excepciones de dominio ya construidas
            raise
        except Exception as exc:
            # Encadena errores inesperados conservando la causa original con 'from exc'
            raise CalculoCostoError(f"Error al calcular el costo de '{self.nombre}'.") from exc


class ReservaSala(Servicio):
    """Servicio especializado para reserva de salas."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        tarifa_base: float,
        capacidad_personas: int,
        disponible: bool = True,
    ) -> None:
        self.capacidad_personas = capacidad_personas
        super().__init__(codigo, nombre, tarifa_base, disponible)

    def validar_parametros(self) -> None:
        """Valida que la sala tenga capacidad mayor que cero."""
        if self.capacidad_personas <= 0:
            raise ParametroServicioInvalidoError("La capacidad de la sala debe ser mayor que 0.")

    def calcular_costo_base(self, cantidad: float) -> float:
        """Calcula el costo base multiplicando horas de reserva por tarifa por hora."""
        if cantidad <= 0:
            raise ParametroServicioInvalidoError("Las horas de reserva deben ser mayores que 0.")
        return self.tarifa_base * cantidad

    def describir(self) -> str:
        """Retorna la descripción de la sala."""
        estado = "Disponible" if self.disponible else "No disponible"
        return f"[Sala] {self.codigo} - {self.nombre} | Capacidad: {self.capacidad_personas} | {estado}"


class AlquilerEquipo(Servicio):
    """Servicio especializado para alquiler de equipos."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        tarifa_base: float,
        dias_garantia: int = 1,
        disponible: bool = True,
    ) -> None:
        self.dias_garantia = dias_garantia
        super().__init__(codigo, nombre, tarifa_base, disponible)

    def validar_parametros(self) -> None:
        """Valida que los días de garantía no sean negativos."""
        if self.dias_garantia < 0:
            raise ParametroServicioInvalidoError("Los días de garantía no pueden ser negativos.")

    def calcular_costo_base(self, cantidad: float) -> float:
        """Calcula el costo base según los días de alquiler."""
        if cantidad <= 0:
            raise ParametroServicioInvalidoError("Los días de alquiler deben ser mayores que 0.")
        return self.tarifa_base * cantidad

    def describir(self) -> str:
        """Retorna la descripción del equipo."""
        estado = "Disponible" if self.disponible else "No disponible"
        return (
            f"[Equipo] {self.codigo} - {self.nombre} | "
            f"Garantía: {self.dias_garantia} día(s) | {estado}"
        )


class AsesoriaEspecializada(Servicio):
    """Servicio especializado para asesorías técnicas o de software."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        tarifa_base: float,
        especialidad: str,
        disponible: bool = True,
    ) -> None:
        if not especialidad or not especialidad.strip():
            raise ParametroServicioInvalidoError("La especialidad de la asesoría es obligatoria.")
        self.especialidad = especialidad.strip()
        super().__init__(codigo, nombre, tarifa_base, disponible)

    def validar_parametros(self) -> None:
        """Valida que exista una especialidad."""
        if not self.especialidad:
            raise ParametroServicioInvalidoError("Debe indicar una especialidad válida.")

    def calcular_costo_base(self, cantidad: float) -> float:
        """Calcula el costo base según la cantidad de sesiones."""
        if cantidad <= 0:
            raise ParametroServicioInvalidoError("La cantidad de sesiones debe ser mayor que 0.")
        return self.tarifa_base * cantidad

    def describir(self) -> str:
        """Retorna la descripción de la asesoría."""
        estado = "Disponible" if self.disponible else "No disponible"
        return (
            f"[Asesoría] {self.codigo} - {self.nombre} | "
            f"Especialidad: {self.especialidad} | {estado}"
        )


# =====================================================================
# 4. PRUEBA CON try / except / else / finally Y REGISTRO EN LOG
# =====================================================================

def ejecutar_cotizacion_segura(
    servicio: Servicio,
    cantidad: float,
    descuento: float = 0.0,
    impuesto: float = 0.0,
) -> None:
    """Ejecuta una cotización usando try/except/else/finally y registra el resultado en el log."""
    try:
        total = servicio.calcular_costo(cantidad, descuento_pct=descuento, impuesto_pct=impuesto)
    except ErrorSistemaFJ as error_dominio:
        logger_fj.error(f"Error controlado en cotización: {error_dominio}")
        print(f"Error controlado: {error_dominio}")
    except Exception as error_inesperado:
        logger_fj.critical(f"Error inesperado en cotización: {error_inesperado}")
        print(f"Error inesperado: {error_inesperado}")
    else:
        # Solo se ejecuta si no hubo errores en el bloque try
        mensaje_ok = f"Cotización exitosa ({servicio.describir()}) -> Total: ${total:,.2f}"
        logger_fj.info(mensaje_ok)
        print(mensaje_ok)
    finally:
        # Se ejecuta siempre para mantener la estabilidad del flujo
        print("--- Fin de operación de cotización ---")


if __name__ == "__main__":
    sala = ReservaSala("SAL-01", "Sala de Reuniones A", 50000, capacidad_personas=12)
    equipo = AlquilerEquipo("EQ-02", "Portátil de Pruebas", 35000, dias_garantia=2)
    asesoria = AsesoriaEspecializada("ASE-03", "Arquitectura de Software", 90000, "Backend y POO")

    ejecutar_cotizacion_segura(sala, cantidad=3)
    ejecutar_cotizacion_segura(equipo, cantidad=2, descuento=10.0, impuesto=19.0)
    ejecutar_cotizacion_segura(asesoria, cantidad=-1)
    