# -----------------------------------------------------------------------
# Nombre del archivo: Software_FJ.py
# Fecha: 03/11/2026
# Version:0.2
# Estudiantes: Geraldyn Arboleda Usechy - Miguel Angel Guarnizo Calderon
# Grupo:213023_406
# -----------------------------------------------------------------------

# — Se importan las librerias necesarias para el funcionamiento del software —
from abc import ABC, abstractmethod
import datetime
import os

# =====================================================================
# 1. MÓDULO DE EXCEPCIONES PERSONALIZADAS
# =====================================================================


# — Se crea una clase padre para el manejo de errores —
class SistemaSoftwareFJError(Exception):
    """Excepción base para todos los errores del sistema Software FJ."""

    pass


# — Generamos los cuatro hijos del error base —
class ClienteError(SistemaSoftwareFJError):
    """Excepción lanzada ante datos de cliente inválidos."""

    pass


class ServicioError(SistemaSoftwareFJError):
    """Excepción lanzada ante fallos en la configuración o cálculo de servicios."""

    pass


class ServicioNoDisponibleError(ServicioError):
    """Se intenta reservar un servicio que no esta disponible."""

    pass


class ReservaError(SistemaSoftwareFJError):
    """Excepción lanzada ante intentos de reserva incorrectos o ilegales."""

    pass


# — Se crea una clase para el almacenamiento de datos mediante listas internas —
class GestorSoftwareFJ:
    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, nombre, identificacion, correo, telefono):
        for c in self.clientes:
            if c.identificacion == str(identificacion):
                raise ClienteError(
                    f"Ya existe un cliente con identificacion {identificacion}."
                )
        cliente = Cliente(nombre, identificacion, correo, telefono)
        self.clientes.append(cliente)
        registrar_log("INFO", f"Cliente registrado: {cliente.nombre}")
        return cliente

    def crear_reserva(self, cliente=None, servicio=None, duracion=None, **opciones):
        faltantes = []
        if cliente is None:
            faltantes.append("cliente")
        if servicio is None:
            faltantes.append("servicio")
        if duracion is None:
            faltantes.append("duracion")
        if faltantes:
            raise ReservaError(
                f"Faltan parametros obligatorios: {', '.join(faltantes)}."
            )
        reserva = Reserva(cliente, servicio, duracion, **opciones)
        self.reservas.append(reserva)
        return reserva

    def registrar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise ServicioError("Solo se pueden registrar objetos de tipo Servicio.")
        self.servicios.append(servicio)
        registrar_log("INFO", f"Servicio registrado: {servicio.nombre_servicio}")
        return servicio

    def cotizar(self, servicio, *valores):
        if len(valores) == 0:
            raise ServicioError("cotizar() necesita al menos la duracion.")
        if len(valores) > 3:
            raise ServicioError("cotizar() recibe maximo 3 valores.")
        return servicio.calcular_costo(*valores)


# — Se define la función para almacenar los registros del sistema —
def registrar_log(tipo: str, mensaje: str):
    """Registra eventos y errores en un archivo de texto plano (sistema_logs.txt)."""
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("sistema_logs.txt", "a", encoding="utf-8") as archivo_log:
            archivo_log.write(f"[{timestamp}] [{tipo.upper()}] {mensaje}\n")
    except Exception as e:
        print(f"[CRÍTICO] No se pudo escribir en el archivo de log: {e}")


# =====================================================================
# 2. CLASE ABSTRACTA BASE PARA ENTIDADES DEL SISTEMA
# =====================================================================


# — Se crea una clase abstracta heredada del ABC con la cual no se van a hacer objetos, sino que heredará información de sus clases hijos —
class EntidadBase(ABC):
    """Clase abstracta que representa entidades generales del sistema."""

    # — Se crea un decorador (@) para generar métodos abstractos que obligue a las clases hijas a reescribirlo —
    @abstractmethod
    def obtener_detalles(self) -> str:
        """Método abstracto obligatorio para retornar detalles de la entidad."""
        pass


# =====================================================================
# 3. CLASE CLIENTE CON ENCAPSULACIÓN Y VALIDACIONES ROBUSTAS
# =====================================================================


# — Se crea la clase Cliente como hija de la clase EntidadBase —
class Cliente(EntidadBase):
    def __init__(self, nombre: str, identificacion: str, correo: str, telefono: str):
        self.nombre = nombre
        self.identificacion = identificacion
        self.correo = correo
        self.telefono = telefono

    # — Se agrega el decorador @property para acceder a un método como si fuera un atributo —
    @property
    def nombre(self):
        return self._nombre

    # — Mediante el setter se valida si los datos ingresados son correctos —
    @nombre.setter
    def nombre(self, value):
        if not value or not isinstance(value, str) or len(value.strip()) < 2:
            raise ClienteError(
                f"Nombre de cliente inválido: '{value}'. Debe tener al menos 2 caracteres."
            )
        self._nombre = value.strip()

    @property
    def identificacion(self):
        return self._identificacion

    @identificacion.setter
    def identificacion(self, value):
        if not value or not str(value).isdigit() or len(str(value)) < 6:
            raise ClienteError(
                f"Identificación inválida: '{value}'. Debe ser numérica y tener al menos 6 dígitos."
            )
        self._identificacion = str(value)

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, value):
        if not value or "@" not in value or "." not in value:
            raise ClienteError(f"Correo electrónico inválido: '{value}'.")
        self._correo = value.strip()

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, value):
        if not value or not str(value).isdigit() or len(str(value)) < 7:
            raise ClienteError(
                f"Teléfono inválido: '{value}'. Debe tener al menos 7 dígitos."
            )
        self._telefono = str(value)

    def obtener_detalles(self) -> str:
        return f"Cliente: {self.nombre} | ID: {self.identificacion} | Correo: {self.correo} | Tel: {self.telefono}"


# =====================================================================
# 4. CLASE ABSTRACTA SERVICIO Y SERVICIOS ESPECIALIZADOS (POLIMORFISMO)
# =====================================================================


# — Se crea la clase Servicio como hija de la clase EntidadBase, agregandole lógica de polimorfismo para que pueda ser utilizada en diferentes clases con un comportamiento diferente —
class Servicio(EntidadBase, ABC):
    def __init__(self, nombre_servicio: str, tarifa_base: float, disponible=True):
        self.nombre_servicio = nombre_servicio
        self.tarifa_base = tarifa_base
        self.disponible = disponible

    def verificar_disponibilidad(self):
        if not self.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self.nombre_servicio}' no esta disponible en este momento."
            )

    @property
    def tarifa_base(self):
        return self._tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ServicioError(f"La tarifa debe ser un numero, se recibio: '{value}'.")
        if value < 0:
            raise ServicioError("La tarifa base no puede ser un valor negativo.")
        self._tarifa_base = float(value)

    @abstractmethod
    def calcular_costo(self, duracion: float, *args, **kwargs) -> float:
        """Método polimórfico sobrecargado para calcular costos según reglas de negocio."""
        pass

    @abstractmethod
    def validar_parametros(self, duracion: float):
        """Valida que los parámetros de entrada del servicio sean correctos."""
        pass


# — Se crean las clases hijas de la clase Servicio para almacenar datos y darle manejo correspondiente a la funcionalidad que tenga cada clase —
class ReservaSala(Servicio):
    def __init__(
        self, nombre: str, tarifa_base: float, capacidad: int, disponible=True
    ):
        super().__init__(nombre, tarifa_base, disponible)
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise ServicioError(
                f"Capacidad invalida: '{capacidad}'. Debe ser un entero mayor a 0."
            )
        self.capacidad = capacidad

    def validar_parametros(self, duracion: float):
        if duracion <= 0:
            raise ServicioError("La duración de la sala debe ser mayor a 0 horas.")
        if self.capacidad <= 0:
            raise ServicioError("La capacidad de la sala debe ser mayor a 0 personas.")

    def calcular_costo(
        self, duracion: float, descuento: float = 0.0, impuesto: float = 0.19
    ) -> float:
        self.validar_parametros(duracion)
        try:
            if not (0.0 <= descuento <= 1.0):
                raise ValueError("El descuento debe estar entre 0.0 y 1.0 (0% a 100%).")
            subtotal = (self.tarifa_base * duracion) * (1.0 - descuento)
            total = subtotal * (1.0 + impuesto)
            return round(total, 2)
        except Exception as e:
            raise ServicioError(f"Error en cálculo de costo para Sala: {e}") from e

    def obtener_detalles(self) -> str:
        return f"[Servicio Sala] {self.nombre_servicio} | Capacidad: {self.capacidad} pers. | Tarifa/h: ${self.tarifa_base}"


class AlquilerEquipos(Servicio):
    def __init__(
        self, nombre: str, tarifa_base: float, tipo_equipo: str, disponible=True
    ):
        super().__init__(nombre, tarifa_base, disponible)
        self.tipo_equipo = tipo_equipo

    def validar_parametros(self, duracion: float):
        if duracion <= 0:
            raise ServicioError(
                "El tiempo de alquiler de equipos debe ser mayor a 0 días."
            )

    def calcular_costo(
        self, duracion: float, seguro: float = 15.0, impuesto: float = 0.19
    ) -> float:
        self.validar_parametros(duracion)
        try:
            if seguro < 0:
                raise ValueError("El costo del seguro no puede ser negativo.")
            subtotal = (self.tarifa_base * duracion) + seguro
            total = subtotal * (1.0 + impuesto)
            return round(total, 2)
        except Exception as e:
            raise ServicioError(f"Error en cálculo de costo para Equipos: {e}") from e

    def obtener_detalles(self) -> str:
        return f"[Servicio Equipos] {self.nombre_servicio} | Tipo: {self.tipo_equipo} | Tarifa/día: ${self.tarifa_base}"


class AsesoriaEspecializada(Servicio):
    def __init__(
        self, nombre: str, tarifa_base: float, especialista: str, disponible=True
    ):
        super().__init__(nombre, tarifa_base, disponible)
        self.especialista = especialista

    def validar_parametros(self, duracion: float):
        if duracion <= 0:
            raise ServicioError("Las horas de asesoría deben ser mayores a 0.")

    def calcular_costo(
        self, duracion: float, factor_complejidad: float = 1.0, impuesto: float = 0.19
    ) -> float:
        self.validar_parametros(duracion)
        try:
            if factor_complejidad < 1.0:
                raise ValueError(
                    "El factor de complejidad no puede ser inferior a 1.0."
                )
            subtotal = (self.tarifa_base * duracion) * factor_complejidad
            total = subtotal * (1.0 + impuesto)
            return round(total, 2)
        except Exception as e:
            raise ServicioError(f"Error en cálculo de costo para Asesoría: {e}") from e

    def obtener_detalles(self) -> str:
        return f"[Servicio Asesoría] {self.nombre_servicio} | Consultor: {self.especialista} | Tarifa/h: ${self.tarifa_base}"


# =====================================================================
# 5. CLASE RESERVA CON MANEJO AVANZADO DE EXCEPCIONES
# =====================================================================


# — Se crea la clase Reserva como hija de la clase EntidadBase, en la que implementaremos la lógica básica para el manejo de errores —
class Reserva(EntidadBase):
    def __init__(
        self, cliente: Cliente, servicio: Servicio, duracion: float, **opciones_costo
    ):
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"
        self.costo_total = 0.0
        self.opciones_costo = opciones_costo

    # — Confirma la reserva aplicando try/except/finally y encadenamiento de excepciones —
    def confirmar(self):
        # — Se intenta la lógica esperando que nos arroje un resultado —
        try:
            if self.estado == "Confirmada":
                raise ReservaError("La reserva ya se encuentra confirmada previamente.")
            if self.estado == "Cancelada":
                raise ReservaError(
                    "No se puede confirmar una reserva que ha sido cancelada."
                )

            self.servicio.verificar_disponibilidad()
            self.costo_total = self.servicio.calcular_costo(
                self.duracion, **self.opciones_costo
            )
            self.costo_total = self.servicio.calcular_costo(
                self.duracion, **self.opciones_costo
            )
            self.estado = "Confirmada"
            registrar_log(
                "INFO",
                f"Reserva confirmada con éxito para {self.cliente.nombre} en {self.servicio.nombre_servicio}. Total: ${self.costo_total}",
            )
            return f"Reserva exitosa. Total a pagar: ${self.costo_total}"
        # — En caso de que hayamos tenido un error, lo controlaremos indicando el fallo operativo —
        except ReservaError as err_reserva:
            registrar_log("ADVERTENCIA", f"Operacion no permitida: {err_reserva}")
            raise
        except (ServicioError, ValueError) as err_negocio:
            self.estado = "Fallida"
            registrar_log(
                "ERROR", f"Fallo operativo al procesar reserva: {err_negocio}"
            )
            raise ReservaError(
                f"Error operativo en reserva: {err_negocio}"
            ) from err_negocio

        except Exception as err_inesperado:
            self.estado = "Fallida"
            registrar_log(
                "CRITICO", f"Error inesperado al confirmar reserva: {err_inesperado}"
            )
            raise ReservaError(
                f"Error crítico no controlado: {err_inesperado}"
            ) from err_inesperado
        # — Si hay error o no, ejecutamos esta lógica —
        finally:
            print(
                f"   [LOG INTERNO] Intento de procesamiento finalizado. Estado actual: {self.estado}"
            )

    # — Cancela la reserva demostrando el uso de try/except/else —
    def cancelar(self):
        # — Se intenta la lógica esperando que nos arroje un resultado —
        try:
            if self.estado == "Cancelada":
                raise ReservaError("La reserva ya se encuentra cancelada.")
            self.estado = "Cancelada"
            registrar_log(
                "INFO", f"Reserva cancelada para el cliente {self.cliente.nombre}."
            )
        # — En caso de que hayamos tenido un error, lo controlaremos indicando el fallo operativo —
        except Exception as e:
            registrar_log("ERROR", f"Fallo al intentar cancelar reserva: {e}")
            raise ReservaError(f"No se pudo cancelar: {e}") from e
        # — Como no tuvimos error continuaríamos el flujo correspondiente que tiene el sistema —
        else:
            print(
                "   [INFO] Operación de cancelación completada sin excepciones previas."
            )

    # — Procesa la reserva demostrando el uso de try/except/else —
    def procesar(self):
        try:
            if self.estado != "Confirmada":
                raise ReservaError(
                    f"Solo se procesan reservas confirmadas (estado actual: {self.estado})."
                )
            if self.costo_total <= 0:
                raise ValueError(
                    "El costo total calculado es inconsistente (menor o igual a 0)."
                )
        except ValueError as e:
            registrar_log("ERROR", f"Calculo inconsistente al procesar: {e}")
            raise ReservaError("No se pudo procesar la reserva.") from e
        except ReservaError as e:
            registrar_log("ERROR", f"Procesamiento rechazado: {e}")
            raise
        else:
            self.estado = "Procesada"
            registrar_log("INFO", f"Reserva procesada y cobrada: ${self.costo_total}")
            return f"Reserva procesada. Cobro realizado: ${self.costo_total}"
        finally:
            print(f"   [LOG INTERNO] Procesamiento terminado. Estado: {self.estado}")

    def obtener_detalles(self) -> str:
        return f"Reserva [{self.estado}] | Cliente: {self.cliente.nombre} | Servicio: {self.servicio.nombre_servicio} | Duración: {self.duracion} | Costo: ${self.costo_total}"


# =====================================================================
# 6. SIMULACIÓN DE 10 OPERACIONES (VÁLIDAS E INVÁLIDAS)
# =====================================================================


# — Crea servicios, prueba 10 clientes y reservas (unos buenos y otros malos) y al final muestra un resumen —
def ejecutar_simulacion_software_fj():
    print("==========================================================")
    print(" INICIANDO SIMULACIÓN DE OPERACIONES - SOFTWARE FJ")
    print("==========================================================")

    if os.path.exists("sistema_logs.txt"):
        os.remove("sistema_logs.txt")

    # — El gestor guarda clientes, servicios y reservas en listas internas —
    gestor = GestorSoftwareFJ()

    sala = gestor.registrar_servicio(
        ReservaSala("Sala Creativa Alfa", tarifa_base=50.0, capacidad=12)
    )
    equipo = gestor.registrar_servicio(
        AlquilerEquipos(
            "Servidor Portátil de Pruebas",
            tarifa_base=120.0,
            tipo_equipo="Hardware High-End",
        )
    )
    asesoria = gestor.registrar_servicio(
        AsesoriaEspecializada(
            "Arquitectura Cloud y DevOps",
            tarifa_base=90.0,
            especialista="Ing. Carlos Mendoza",
        )
    )
    # — Servicio creado a propósito como NO disponible —
    sala_mantenimiento = gestor.registrar_servicio(
        ReservaSala(
            "Sala Beta (en mantenimiento)",
            tarifa_base=40.0,
            capacidad=8,
            disponible=False,
        )
    )

    operaciones_exitosas = 0
    operaciones_fallidas_controladas = 0

    pruebas = [
        (
            "valida",
            "Cliente 1",
            "Ana María Gómez",
            "10852346",
            "ana.gomez@softwarefj.com",
            "3104567890",
            sala,
            4.0,
            {"descuento": 0.10},
        ),
        (
            "invalida_cliente",
            "Cliente 2",
            "Pedro Pérez",
            "ABC12345",
            "pedro@mail.com",
            "3201234567",
            sala,
            2.0,
            {},
        ),
        (
            "valida",
            "Cliente 3",
            "Lucía Martínez",
            "79451238",
            "lucia.martinez@softwarefj.com",
            "3157891234",
            equipo,
            3.0,
            {"seguro": 25.0},
        ),
        (
            "valida",
            "Cliente 4",
            "Jorge Eliécer Rueda",
            "94123654",
            "jorge.rueda@softwarefj.com",
            "3001112233",
            asesoria,
            -2.0,
            {"factor_complejidad": 1.2},
        ),
        (
            "valida",
            "Cliente 5",
            "Sofía Valentina Roa",
            "1122334455",
            "sofia.roa@softwarefj.com",
            "3112223344",
            asesoria,
            5.0,
            {"factor_complejidad": 1.5},
        ),
        (
            "invalida_cliente",
            "Cliente 6",
            "Carlos Vives",
            "5544332211",
            "carlos.vives-sin-arroba",
            "3189998877",
            sala,
            1.0,
            {},
        ),
        (
            "valida_error_servicio",
            "Cliente 7",
            "Mariana Cifuentes",
            "8877665544",
            "mariana.cifuentes@softwarefj.com",
            "3145556677",
            equipo,
            0.0,
            {},
        ),
        (
            "valida",
            "Cliente 8",
            "Felipe Andrés Morales",
            "3322114455",
            "felipe.morales@softwarefj.com",
            "3190001122",
            sala,
            6.0,
            {"impuesto": 0.16},
        ),
        (
            "cancelacion_prueba",
            "Cliente 9",
            "Diana Marcela Torres",
            "7788990011",
            "diana.torres@softwarefj.com",
            "3123334455",
            asesoria,
            2.0,
            {},
        ),
        (
            "valida",
            "Cliente 10",
            "Santiago Martinez",
            "109587423",
            "santimartz@softwarefj.com",
            "3217532359",
            sala,
            7.0,
            {"descuento": 10.0},
        ),
    ]

    for idx, (
        tipo_prueba,
        id_op,
        nombre,
        cedula,
        correo,
        tel,
        servicio_obj,
        duracion,
        params,
    ) in enumerate(pruebas, start=1):
        print(f"\n--- Ejecutando Operación #{idx} [{tipo_prueba.upper()}] ---")
        try:
            # — Se registra por el gestor para que detecte cédulas repetidas —
            cliente_actual = gestor.registrar_cliente(nombre, cedula, correo, tel)
            print(f" > Cliente registrado: {cliente_actual.nombre}")

            reserva_actual = gestor.crear_reserva(
                cliente_actual, servicio_obj, duracion, **params
            )

            if tipo_prueba == "cancelacion_prueba":
                reserva_actual.cancelar()
            else:
                print(f" > {reserva_actual.confirmar()}")
                print(f" > {reserva_actual.procesar()}")

            operaciones_exitosas += 1

        except (
            ClienteError,
            ServicioError,
            ReservaError,
            ValueError,
        ) as exc_controlada:
            operaciones_fallidas_controladas += 1
            print(f" [EXCEPCIÓN CONTROLADA CAPTURADA]: {exc_controlada}")
            registrar_log(
                "CONTROLADO", f"Op #{idx} falló controladamente: {exc_controlada}"
            )
        except Exception as exc_inesperada:
            operaciones_fallidas_controladas += 1
            print(f" [ERROR GRAVE NO PREVISTO]: {exc_inesperada}")
            registrar_log(
                "CRITICO", f"Op #{idx} falló por error desconocido: {exc_inesperada}"
            )

    # =================================================================
    # GENERACIÓN DE PRUEBAS
    # =================================================================
    print("\n==========================================================")
    print(" PRUEBAS DEL SISTEMA")
    print("==========================================================")
    cliente_prueba = gestor.clientes[0]  

    # — Creación incorrecta de un servicio (tarifa negativa) —
    print("\n--- A. Creación incorrecta de servicio ---")
    try:
        gestor.registrar_servicio(
            ReservaSala("Sala Fantasma", tarifa_base=-10, capacidad=5)
        )
    except ServicioError as e:
        print(f" [EXCEPCIÓN CONTROLADA CAPTURADA]: {e}")
        registrar_log("CONTROLADO", f"Creación de servicio rechazada: {e}")

    # — Reserva de un servicio no disponible —
    print("\n--- B. Servicio no disponible ---")
    try:
        gestor.crear_reserva(cliente_prueba, sala_mantenimiento, 2.0).confirmar()
    except ReservaError as e:
        print(f" [EXCEPCIÓN CONTROLADA CAPTURADA]: {e}")
        registrar_log("CONTROLADO", f"Reserva de servicio no disponible: {e}")

    # — Reserva con parámetros faltantes (sin duración) —
    print("\n--- C. Parámetros faltantes ---")
    try:
        gestor.crear_reserva(cliente_prueba, sala)
    except ReservaError as e:
        print(f" [EXCEPCIÓN CONTROLADA CAPTURADA]: {e}")
        registrar_log("CONTROLADO", f"Reserva incompleta: {e}")

    # — Sobrecarga: el mismo método con 1, 2 y 3 valores —
    print("\n--- D. Sobrecarga de cotizar() ---")
    try:
        print(f" > Sala 3h:                       ${gestor.cotizar(sala, 3)}")
        print(f" > Sala 3h con 20% de descuento:  ${gestor.cotizar(sala, 3, 0.2)}")
        print(
            f" > Sala 3h, 20% desc., IVA 16%:   ${gestor.cotizar(sala, 3, 0.2, 0.16)}"
        )
        gestor.cotizar(sala)  # sin duración → error controlado
    except ServicioError as e:
        print(f" [EXCEPCIÓN CONTROLADA CAPTURADA]: {e}")
        registrar_log("CONTROLADO", f"Cotización rechazada: {e}")

    print("\n==========================================================")
    print(" RESUMEN FINAL DE LA SIMULACIÓN")
    print("==========================================================")
    print(f" Total de operaciones evaluadas: {len(pruebas)}")
    print(f" Operaciones exitosas procesadas: {operaciones_exitosas}")
    print(
        f" Errores atrapados y controlados profesionalmente: {operaciones_fallidas_controladas}"
    )
    print(
        f" Clientes: {len(gestor.clientes)} | Servicios: {len(gestor.servicios)} | Reservas: {len(gestor.reservas)}"
    )
    print(" El sistema se mantuvo estable y generó el log en 'sistema_logs.txt'.")
    print("==========================================================")


if __name__ == "__main__":
    ejecutar_simulacion_software_fj()
