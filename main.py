"""VISTA: menús, input() y print(). Todas las reglas están en views.py."""

from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
import views


# =====================================================================
# AYUDAS DE PANTALLA: las dos funciones de presentación son genéricas
# =====================================================================
def pausa():
    input("\nPresione Enter para continuar...")


def pedir_entero(etiqueta):
    try:
        return int(input(etiqueta))
    except ValueError:
        return None


def mostrar_resultado(exito, mensaje):
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)


def mostrar_lista(objetos, vacio="No hay registros todavía."):
    """Sirve para estudiantes, materias y matrículas: cada modelo sabe mostrarse."""
    if not objetos:
        imprimir_info(vacio)
        return
    for objeto in objetos:
        print(f"  {objeto}")
    imprimir_info(f"Total: {len(objetos)}")


def mostrar_detalle(objeto):
    # Recorre el DICCIONARIO del objeto: clave y valor a la vez
    for clave, valor in objeto.a_diccionario().items():
        print(f"  {str(clave).replace('_', ' ').capitalize():<16}: {valor}")


def pedir_cambios(objeto, campos):
    print("Deje vacío el campo que no desee modificar.\n")
    cambios = {}
    for campo in campos:
        actual = getattr(objeto, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo
    return cambios


# =====================================================================
# ESTUDIANTES
# =====================================================================
def crear_estudiante():
    imprimir_titulo("CREAR ESTUDIANTE")
    datos = {
        "nombre": input("Nombre: "),
        "apellido": input("Apellido: "),
        "email": input("Email: "),
        "carnet": input("Carnet: "),
        "carrera": input("Carrera: "),
    }
    mostrar_resultado(*views.crear_estudiante(datos))
    pausa()


def listar_estudiantes():
    imprimir_titulo("ESTUDIANTES")
    mostrar_lista(views.obtener_estudiantes(), "Todavía no hay estudiantes.")
    pausa()


def buscar_estudiante():
    imprimir_titulo("BUSCAR ESTUDIANTES")
    termino = input("Nombre, apellido, email, carnet o carrera: ")
    mostrar_lista(views.buscar_estudiantes(termino), "No se encontraron estudiantes.")
    pausa()


def ver_estudiante():
    imprimir_titulo("VER ESTUDIANTE POR ID")
    estudiante = views.obtener_estudiante(pedir_entero("Id: "))
    if estudiante is None:
        imprimir_error("Estudiante no encontrado")
    else:
        mostrar_detalle(estudiante)
    pausa()


def actualizar_estudiante():
    imprimir_titulo("ACTUALIZAR ESTUDIANTE")
    id_estudiante = pedir_entero("Id: ")
    estudiante = views.obtener_estudiante(id_estudiante)
    if estudiante is None:
        imprimir_error("Estudiante no encontrado")
    else:
        imprimir_info(f"Editando: {estudiante.etiqueta()}")
        cambios = pedir_cambios(estudiante, ("nombre", "apellido", "email", "carnet", "carrera"))
        mostrar_resultado(*views.actualizar_estudiante(id_estudiante, cambios))
    pausa()


def eliminar_estudiante():
    imprimir_titulo("ELIMINAR ESTUDIANTE")
    id_estudiante = pedir_entero("Id: ")
    estudiante = views.obtener_estudiante(id_estudiante)
    if estudiante is None:
        imprimir_error("Estudiante no encontrado")
    else:
        imprimir_info(f"Se eliminará: {estudiante.etiqueta()}")
        if confirmar("¿Confirma?"):
            mostrar_resultado(*views.eliminar_estudiante(id_estudiante))
        else:
            imprimir_info("Operación cancelada")
    pausa()


# =====================================================================
# MATERIAS
# =====================================================================
def crear_materia():
    imprimir_titulo("CREAR MATERIA")
    datos = {
        "nombre": input("Nombre: "),
        "codigo": input("Código (ej. MAT101): "),
        "creditos": input("Créditos (1 a 10): "),
        "cupos": input("Cupos (0 a 30): "),
    }
    mostrar_resultado(*views.crear_materia(datos))
    pausa()


def listar_materias():
    imprimir_titulo("MATERIAS")
    mostrar_lista(views.obtener_materias(), "Todavía no hay materias.")
    pausa()


def buscar_materia():
    imprimir_titulo("BUSCAR MATERIAS")
    termino = input("Nombre o código: ")
    mostrar_lista(views.buscar_materias(termino), "No se encontraron materias.")
    pausa()


def ver_materia():
    imprimir_titulo("VER MATERIA POR ID")
    materia = views.obtener_materia(pedir_entero("Id: "))
    if materia is None:
        imprimir_error("Materia no encontrada")
    else:
        mostrar_detalle(materia)
    pausa()


def actualizar_materia():
    imprimir_titulo("ACTUALIZAR MATERIA")
    id_materia = pedir_entero("Id: ")
    materia = views.obtener_materia(id_materia)
    if materia is None:
        imprimir_error("Materia no encontrada")
    else:
        imprimir_info(f"Editando: {materia.etiqueta()}")
        cambios = pedir_cambios(materia, ("nombre", "codigo", "creditos", "cupos"))
        mostrar_resultado(*views.actualizar_materia(id_materia, cambios))
    pausa()


def eliminar_materia():
    imprimir_titulo("ELIMINAR MATERIA")
    id_materia = pedir_entero("Id: ")
    materia = views.obtener_materia(id_materia)
    if materia is None:
        imprimir_error("Materia no encontrada")
    else:
        imprimir_info(f"Se eliminará: {materia.etiqueta()}")
        if confirmar("¿Confirma?"):
            mostrar_resultado(*views.eliminar_materia(id_materia))
        else:
            imprimir_info("Operación cancelada")
    pausa()


# =====================================================================
# MATRÍCULAS
# =====================================================================
def matricular():
    imprimir_titulo("CREAR MATRÍCULA")
    datos = {
        "estudiante_id": pedir_entero("Id del estudiante: "),
        "materia_id": pedir_entero("Id de la materia: "),
        "periodo": input("Periodo (ej. 2026-1): "),
    }
    mostrar_resultado(*views.crear_matricula(datos))
    pausa()


def listar_matriculas():
    imprimir_titulo("MATRÍCULAS")
    mostrar_lista(views.obtener_matriculas(), "Todavía no hay matrículas.")
    pausa()


def registrar_nota():
    imprimir_titulo("REGISTRAR NOTA")
    id_matricula = pedir_entero("Id de la matrícula: ")
    nota = input("Nueva nota (0 a 20): ")
    mostrar_resultado(*views.registrar_nota(id_matricula, nota))
    pausa()


def ver_certificado():
    imprimir_titulo("CERTIFICADO DE MATRÍCULA")
    id_matricula = pedir_entero("Id de la matrícula: ")
    resultado = views.certificado(id_matricula)
    if resultado is None:
        imprimir_error("Matrícula no encontrada")
    else:
        print(resultado)
    pausa()


def retirar_matricula():
    imprimir_titulo("RETIRAR MATRÍCULA")
    id_matricula = pedir_entero("Id de la matrícula: ")
    matricula = views.obtener_matricula(id_matricula)
    if matricula is None:
        imprimir_error("Matrícula no encontrada")
    else:
        imprimir_info(f"Se retirará: {matricula.etiqueta()}")
        if confirmar("¿Confirma?"):
            mostrar_resultado(*views.retirar_matricula(id_matricula))
        else:
            imprimir_info("Operación cancelada")
    pausa()


def resumen():
    imprimir_titulo("RESUMEN ACADÉMICO")
    datos = views.resumen_academico()
    print(f"Estudiantes registrados: {datos['estudiantes']}")
    print(f"Carreras distintas: {', '.join(datos['carreras']) or 'ninguna'}")
    print(f"Materias sin cupo: {len(datos['materias_sin_cupo'])}")
    mostrar_lista(datos["materias_sin_cupo"], "Ninguna materia está sin cupo.")
    print(f"Matrículas aprobadas: {datos['matriculas_aprobadas']}")
    pausa()


# =====================================================================
# MENÚS
# =====================================================================
def ejecutar_menu(titulo, opciones):
    # DICCIONARIO: vincula cada número del menú con texto y función.
    while True:
        imprimir_titulo(titulo)
        for clave, (descripcion, _) in opciones.items():
            print(f"  {clave}. {descripcion}")
        print("  0. Volver / salir")
        eleccion = input("\nElija una opción: ").strip()
        if eleccion == "0":
            return
        if eleccion in opciones:
            opciones[eleccion][1]()
        else:
            imprimir_error("Opción no válida")
            pausa()


def menu_estudiantes():
    ejecutar_menu("ESTUDIANTES", {
        "1": ("Crear", crear_estudiante),
        "2": ("Ver todos", listar_estudiantes),
        "3": ("Buscar", buscar_estudiante),
        "4": ("Ver por ID", ver_estudiante),
        "5": ("Actualizar", actualizar_estudiante),
        "6": ("Eliminar", eliminar_estudiante),
    })


def menu_materias():
    ejecutar_menu("MATERIAS", {
        "1": ("Crear", crear_materia),
        "2": ("Ver todas", listar_materias),
        "3": ("Buscar", buscar_materia),
        "4": ("Ver por ID", ver_materia),
        "5": ("Actualizar", actualizar_materia),
        "6": ("Eliminar", eliminar_materia),
    })


def menu_matriculas():
    ejecutar_menu("MATRÍCULAS", {
        "1": ("Matricular", matricular),
        "2": ("Ver todas", listar_matriculas),
        "3": ("Registrar nota", registrar_nota),
        "4": ("Ver certificado", ver_certificado),
        "5": ("Retirar matrícula", retirar_matricula),
    })


def main():
    ejecutar_menu("SISTEMA ACADÉMICO", {
        "1": ("Estudiantes", menu_estudiantes),
        "2": ("Materias", menu_materias),
        "3": ("Matrículas", menu_matriculas),
        "4": ("Resumen", resumen),
    })


if __name__ == "__main__":
    main()
