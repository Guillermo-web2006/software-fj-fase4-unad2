"""Demostración integrada de al menos diez operaciones válidas e inválidas."""
from cliente import GestorClientes
from reserva import Reserva
from servicios_y_excepciones import ReservaSala, AlquilerEquipo, AsesoriaEspecializada, logger_fj

def ejecutar_demo():
    gestor = GestorClientes()
    resultados = []
    def operar(nombre, funcion, debe_fallar=False):
        try:
            resultado = funcion()
        except Exception as error:
            logger_fj.error('Operación %s: %s', nombre, error)
            estado = 'CORRECTO (error controlado)' if debe_fallar else 'FALLO'
            resultados.append((nombre, estado))
            print(f'{nombre}: {estado} - {error}')
        else:
            estado = 'FALLO (se esperaba error)' if debe_fallar else 'CORRECTO'
            resultados.append((nombre, estado))
            print(f'{nombre}: {estado} - {resultado}')
    operar('01 Registro válido', lambda: gestor.registrar('101','Ana Torres','ana@example.com','3001234567'))
    operar('02 Registro correo inválido', lambda: gestor.registrar('102','Luis','invalido','3001234567'), True)
    operar('03 Registro duplicado', lambda: gestor.registrar('101','Otra Ana','otra@example.com','3001234567'), True)
    operar('04 Registro segundo cliente', lambda: gestor.registrar('103','Luis Pérez','luis@example.com','3002223344'))
    operar('05 Buscar cliente', lambda: gestor.buscar('101').nombre)
    operar('06 Actualizar correo', lambda: gestor.buscar('101').actualizar_contacto(correo='ana.nueva@example.com'))
    operar('07 Crear sala válida', lambda: ReservaSala('S01','Sala principal',50000,12).describir())
    operar('08 Crear sala inválida', lambda: ReservaSala('S02','Sala inválida',50000,0), True)
    sala = ReservaSala('S03','Sala de juntas',50000,10)
    equipo = AlquilerEquipo('E01','Portátil',35000,2)
    asesoria = AsesoriaEspecializada('A01','Asesoría Python',90000,'POO')
    operar('09 Cotizar sala', lambda: sala.calcular_costo(2))
    operar('10 Cotizar equipo con descuento', lambda: equipo.calcular_costo(2,10,19))
    operar('11 Cotizar asesoría inválida', lambda: asesoria.calcular_costo(-1), True)
    reserva = Reserva('R01', gestor.buscar('101'), sala, 2)
    operar('12 Confirmar reserva', reserva.confirmar)
    operar('13 Confirmación repetida', reserva.confirmar, True)
    operar('14 Cancelar reserva', reserva.cancelar)
    operar('15 Procesar cancelada', reserva.procesar, True)
    print(f'RESUMEN: {sum("CORRECTO" in estado for _, estado in resultados)}/{len(resultados)} operaciones según lo esperado')
    return resultados

if __name__ == '__main__':
    ejecutar_demo()
