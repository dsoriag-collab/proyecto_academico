"""CONTROLADOR: validaciones, CRUD y relaciones. Sin input() ni print()."""

import os
from datetime import date

from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido

CARPETA = os.path.join(os.path.dirname(__file__), "data")
gestor_estudiantes = GestorJSON(os.path.join(CARPETA, "estudiantes.json"))
gestor_materias = GestorJSON(os.path.join(CARPETA, "materias.json"))
gestor_matriculas = GestorJSON(os.path.join(CARPETA, "matriculas.json"))


# =====================================================================
# FUNCIONES GENÉRICAS: sirven para cualquier entidad
# =====================================================================
def leer_objetos(gestor, clase):
    # LISTA: conserva todos los registros y permite recorrerlos en orden.
    return [clase.desde_diccionario(registro) for registro in gestor.leer()]


def obtener_por_id(gestor, clase, id_registro):
    for objeto in leer_objetos(gestor, clase):
        if objeto.id == id_registro:
            return objeto
    return None


def buscar(gestor, clase, texto, campos):
    # TUPLA de campos: define nombres fijos que no necesitan modificarse.
    texto = str(texto).strip().lower()
    if not texto:
        return []
    encontrados = []
    for objeto in leer_objetos(gestor, clase):
        if any(texto in str(getattr(objeto, campo)).lower() for campo in campos):
            encontrados.append(objeto)
    return encontrados


def siguiente_id(gestor):
    registros = gestor.leer()
    return max((registro["id"] for registro in registros), default=0) + 1


def guardar_nuevo(gestor, objeto):
    registros = gestor.leer()
    registros.append(objeto.a_diccionario())
    return gestor.guardar(registros)


def reemplazar(gestor, objeto):
    registros = gestor.leer()
    for indice, registro in enumerate(registros):
        if registro["id"] == objeto.id:
            registros[indice] = objeto.a_diccionario()
            return gestor.guardar(registros)
    return False


def eliminar(gestor, id_registro):
    registros = gestor.leer()
    restantes = [r for r in registros if r["id"] != id_registro]
    if len(restantes) == len(registros):
        return False
    return gestor.guardar(restantes)


def ids_registrados(gestor):
    # CONJUNTO: permite saber rápidamente si ya existe un id, sin repetidos.
    return {registro["id"] for registro in gestor.leer()}


def indice_por_id(objetos):
    # DICCIONARIO ÍNDICE: permite ubicar el objeto directamente por su id.
    return {objeto.id: objeto for objeto in objetos}


# =====================================================================
# ESTUDIANTES
# =====================================================================
def carnets_registrados(excepto_id=None):
    # CONJUNTO: para evitar carnets repetidos al crear y actualizar.
    return {r["carnet"].upper() for r in gestor_estudiantes.leer()
            if r["id"] != excepto_id}


def validar_estudiante(datos, id_actual=None):
    permitidos = {"nombre", "apellido", "email", "carnet", "carrera"}
    desconocidos = set(datos) - permitidos
    if desconocidos:
        return f"Campos no válidos: {', '.join(sorted(desconocidos))}"

    for campo in ("nombre", "apellido", "email", "carnet"):
        if (id_actual is None or campo in datos) and not str(datos.get(campo, "")).strip():
            return f"El campo {campo} es obligatorio"

    if "email" in datos:
        email = str(datos["email"]).strip().lower()
        if not es_email_valido(email):
            return "Email inválido"
        # CONJUNTO: email único, sin incluir al estudiante editado.
        usados = {r["email"].lower() for r in gestor_estudiantes.leer()
                  if r["id"] != id_actual}
        if email in usados:
            return "Ese email ya está registrado"

    if "carnet" in datos:
        carnet = str(datos["carnet"]).strip().upper()
        if carnet in carnets_registrados(id_actual):
            return "Ese carnet ya está registrado"
    return None


def crear_estudiante(datos):
    error = validar_estudiante(datos)
    if error:
        return False, error  # TUPLA: devuelve resultado y mensaje a la Vista.
    estudiante = Estudiante(
        siguiente_id(gestor_estudiantes),
        str(datos["nombre"]).strip().title(),
        str(datos["apellido"]).strip().title(),
        str(datos["email"]).strip().lower(),
        str(datos["carnet"]).strip().upper(),
        str(datos.get("carrera", "")).strip().title(),
    )
    if not guardar_nuevo(gestor_estudiantes, estudiante):
        return False, "No se pudo guardar el estudiante"
    return True, f"Estudiante creado: {estudiante.etiqueta()}"


def obtener_estudiantes():
    return leer_objetos(gestor_estudiantes, Estudiante)


def obtener_estudiante(id_estudiante):
    return obtener_por_id(gestor_estudiantes, Estudiante, id_estudiante)


def buscar_estudiantes(termino):
    campos = ("nombre", "apellido", "email", "carnet", "carrera")
    return buscar(gestor_estudiantes, Estudiante, termino, campos)


def actualizar_estudiante(id_estudiante, cambios):
    estudiante = obtener_estudiante(id_estudiante)
    if estudiante is None:
        return False, "No existe el estudiante"
    if not cambios:
        return False, "No se indicó ningún cambio"
    error = validar_estudiante(cambios, id_estudiante)
    if error:
        return False, error
    for campo, valor in cambios.items():
        valor = str(valor).strip()
        if campo in ("nombre", "apellido", "carrera"):
            valor = valor.title()
        if campo == "email":
            valor = valor.lower()
        if campo == "carnet":
            valor = valor.upper()
        setattr(estudiante, campo, valor)
    if not reemplazar(gestor_estudiantes, estudiante):
        return False, "No se pudo actualizar el estudiante"
    return True, "Estudiante actualizado correctamente"


def eliminar_estudiante(id_estudiante):
    if obtener_estudiante(id_estudiante) is None:
        return False, "No existe el estudiante"
    if any(m.estudiante_id == id_estudiante for m in obtener_matriculas()):
        return False, "El estudiante tiene matrículas. Retírelas primero"
    if not eliminar(gestor_estudiantes, id_estudiante):
        return False, "No se pudo eliminar el estudiante"
    return True, "Estudiante eliminado correctamente"


# =====================================================================
# MATERIAS
# =====================================================================
def codigos_registrados(excepto_id=None):
    # CONJUNTO: un código de materia no puede repetirse.
    return {r["codigo"].upper() for r in gestor_materias.leer()
            if r["id"] != excepto_id}


def validar_materia(datos, id_actual=None):
    permitidos = {"nombre", "codigo", "creditos", "cupos"}
    desconocidos = set(datos) - permitidos
    if desconocidos:
        return f"Campos no válidos: {', '.join(sorted(desconocidos))}"

    for campo in ("nombre", "codigo", "creditos", "cupos"):
        if (id_actual is None or campo in datos) and not str(datos.get(campo, "")).strip():
            return f"El campo {campo} es obligatorio"

    if "codigo" in datos:
        codigo = str(datos["codigo"]).strip().upper()
        if codigo in codigos_registrados(id_actual):
            return "Ese código ya está registrado"

    if "creditos" in datos:
        try:
            creditos = int(datos["creditos"])
        except (ValueError, TypeError):
            return "Los créditos deben ser un número entero entre 1 y 10"
        if not 1 <= creditos <= 10:
            return "Los créditos deben estar entre 1 y 10"

    if "cupos" in datos:
        try:
            cupos = int(datos["cupos"])
        except (ValueError, TypeError):
            return f"Los cupos deben ser enteros entre 0 y {Materia.CUPOS_MAXIMOS}"
        if not 0 <= cupos <= Materia.CUPOS_MAXIMOS:
            return f"Los cupos deben estar entre 0 y {Materia.CUPOS_MAXIMOS}"
    return None


def crear_materia(datos):
    error = validar_materia(datos)
    if error:
        return False, error
    materia = Materia(
        siguiente_id(gestor_materias),
        str(datos["nombre"]).strip().title(),
        str(datos["codigo"]).strip().upper(),
        int(datos["creditos"]),
        int(datos["cupos"]),
    )
    if not guardar_nuevo(gestor_materias, materia):
        return False, "No se pudo guardar la materia"
    return True, f"Materia creada: {materia.etiqueta()}"


def obtener_materias():
    return leer_objetos(gestor_materias, Materia)


def obtener_materia(id_materia):
    return obtener_por_id(gestor_materias, Materia, id_materia)


def buscar_materias(termino):
    campos = ("nombre", "codigo")  # TUPLA: campos de búsqueda fijos.
    return buscar(gestor_materias, Materia, termino, campos)


def actualizar_materia(id_materia, cambios):
    materia = obtener_materia(id_materia)
    if materia is None:
        return False, "No existe la materia"
    if not cambios:
        return False, "No se indicó ningún cambio"
    error = validar_materia(cambios, id_materia)
    if error:
        return False, error
    for campo, valor in cambios.items():
        if campo == "nombre":
            valor = str(valor).strip().title()
        elif campo == "codigo":
            valor = str(valor).strip().upper()
        else:
            valor = int(valor)
        setattr(materia, campo, valor)
    if not reemplazar(gestor_materias, materia):
        return False, "No se pudo actualizar la materia"
    return True, "Materia actualizada correctamente"


def eliminar_materia(id_materia):
    if obtener_materia(id_materia) is None:
        return False, "No existe la materia"
    if any(m.materia_id == id_materia for m in obtener_matriculas()):
        return False, "La materia tiene matrículas. Retírelas primero"
    if not eliminar(gestor_materias, id_materia):
        return False, "No se pudo eliminar la materia"
    return True, "Materia eliminada correctamente"


def materias_sin_cupo():
    return [materia for materia in obtener_materias() if not materia.hay_cupo()]


# =====================================================================
# MATRÍCULAS
# =====================================================================
def crear_matricula(datos):
    try:
        estudiante_id = int(datos.get("estudiante_id"))
        materia_id = int(datos.get("materia_id"))
    except (TypeError, ValueError):
        return False, "Los identificadores deben ser números enteros"

    periodo = str(datos.get("periodo", "")).strip()
    nota = datos.get("nota", 0)
    if not periodo:
        return False, "El periodo es obligatorio"
    if not Materia.es_nota_valida(nota):
        return False, "La nota debe estar entre 0 y 20"

    if estudiante_id not in ids_registrados(gestor_estudiantes):
        return False, "El estudiante no existe"
    if materia_id not in ids_registrados(gestor_materias):
        return False, "La materia no existe"
    materia = obtener_materia(materia_id)
    if not materia.hay_cupo():
        return False, "La materia no tiene cupos disponibles"

    for matricula in obtener_matriculas():
        if (matricula.estudiante_id == estudiante_id
                and matricula.materia_id == materia_id
                and matricula.periodo == periodo):
            return False, "El estudiante ya está matriculado en esa materia y periodo"

    matricula = Matricula(siguiente_id(gestor_matriculas), estudiante_id,
                          materia_id, periodo, float(nota), date.today().isoformat())
    materia.ocupar_cupo()
    if not reemplazar(gestor_materias, materia):
        return False, "No se pudieron actualizar los cupos de la materia"
    if not guardar_nuevo(gestor_matriculas, matricula):
        materia.liberar_cupo()
        reemplazar(gestor_materias, materia)
        return False, "No se pudo guardar la matrícula"
    return True, f"Matrícula {matricula.id} creada; queda(n) {materia.cupos} cupo(s)"


def obtener_matriculas():
    return leer_objetos(gestor_matriculas, Matricula)


def obtener_matricula(id_matricula):
    return obtener_por_id(gestor_matriculas, Matricula, id_matricula)


def registrar_nota(id_matricula, nota):
    matricula = obtener_matricula(id_matricula)
    if matricula is None:
        return False, "No existe la matrícula"
    if not Materia.es_nota_valida(nota):
        return False, "La nota debe estar entre 0 y 20"
    matricula.nota = float(nota)
    if not reemplazar(gestor_matriculas, matricula):
        return False, "No se pudo registrar la nota"
    return True, f"Nota registrada: {matricula.nota:g} ({matricula.estado()})"


def retirar_matricula(id_matricula):
    matricula = obtener_matricula(id_matricula)
    if matricula is None:
        return False, "No existe la matrícula"
    materia = obtener_materia(matricula.materia_id)
    if not eliminar(gestor_matriculas, id_matricula):
        return False, "No se pudo retirar la matrícula"
    if materia is not None:
        materia.liberar_cupo()
        if not reemplazar(gestor_materias, materia):
            guardar_nuevo(gestor_matriculas, matricula)
            return False, "No se pudo devolver el cupo; matrícula restaurada"
    return True, "Matrícula retirada y cupo devuelto"


def certificado(id_matricula):
    matricula = obtener_matricula(id_matricula)
    if matricula is None:
        return None

    # DICCIONARIO ÍNDICE: relaciona los ids de la matrícula con sus objetos.
    estudiantes_por_id = indice_por_id(obtener_estudiantes())
    materias_por_id = indice_por_id(obtener_materias())
    estudiante = estudiantes_por_id.get(matricula.estudiante_id)
    materia = materias_por_id.get(matricula.materia_id)

    nombre = estudiante.nombre_completo() if estudiante else "Estudiante no disponible"
    carnet = estudiante.carnet if estudiante else "SIN CARNET"
    materia_nombre = materia.nombre if materia else "Materia no disponible"
    codigo = materia.codigo if materia else "SIN CÓDIGO"
    creditos = materia.creditos if materia else "-"
    return (f"CERTIFICADO #{matricula.id}   periodo: {matricula.periodo}\n"
            f"Estudiante: {nombre}   ({carnet})\n"
            f"Materia   : {materia_nombre}   ({codigo}) · {creditos} créditos\n"
            + "-" * 42 + "\n"
            f"Nota      : {matricula.nota:g}\n"
            f"Estado    : {matricula.estado()}")


def matriculas_por_estudiante():
    # DICCIONARIO DE LISTAS: un estudiante puede tener varias matrículas.
    agrupadas = {}
    for matricula in obtener_matriculas():
        agrupadas.setdefault(matricula.estudiante_id, []).append(matricula)
    return agrupadas


def promedio_de_estudiante(id_estudiante):
    matriculas = matriculas_por_estudiante().get(id_estudiante, [])
    if not matriculas:
        return None
    return round(sum(m.nota for m in matriculas) / len(matriculas), 2)


def resumen_academico():
    estudiantes = obtener_estudiantes()
    materias = obtener_materias()
    matriculas = obtener_matriculas()
    # CONJUNTO ordenado: carreras distintas, sin duplicados.
    carreras = sorted({e.carrera for e in estudiantes if e.carrera})
    return {
        "estudiantes": len(estudiantes),
        "carreras": carreras,
        "materias_sin_cupo": [m for m in materias if not m.hay_cupo()],
        "matriculas_aprobadas": sum(m.esta_aprobada() for m in matriculas),
    }
