from io import BytesIO
from decimal import Decimal

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from ..extensions import db
from ..models.evaluacion import Evaluacion
from ..models.tipo_evaluacion import TipoEvaluacion
from ..models.matricula import Matricula
from ..models.detalle_matricula import DetalleMatricula
from ..models.seccion import Seccion
from ..models.curso import Curso
from ..models.estudiante import Estudiante
from ..models.periodo_academico import PeriodoAcademico


class TipoEvaluacionService:

    @staticmethod
    def crear_tipo_evaluacion(data):
        seccion = Seccion.query.get(data["seccion_id"])
        if not seccion:
            raise ValueError("La sección no existe")

        tipo = TipoEvaluacion(
            seccion_id=data["seccion_id"],
            nombre=data["nombre"],
            peso=data["peso"],
        )
        db.session.add(tipo)
        db.session.commit()
        return tipo

    @staticmethod
    def obtener_tipo_evaluacion(tipo_evaluacion_id):
        return TipoEvaluacion.query.get(tipo_evaluacion_id)

    @staticmethod
    def actualizar_tipo_evaluacion(tipo_evaluacion_id, data):
        tipo = TipoEvaluacion.query.get(tipo_evaluacion_id)
        if not tipo:
            return None
        if data.get("nombre") is not None:
            tipo.nombre = data["nombre"]
        if data.get("peso") is not None:
            tipo.peso = data["peso"]
        db.session.commit()
        return tipo

    @staticmethod
    def eliminar_tipo_evaluacion(tipo_evaluacion_id):
        tipo = TipoEvaluacion.query.get(tipo_evaluacion_id)
        if not tipo:
            return False

        # Eliminar todas las notas
        Evaluacion.query.filter_by(tipo_evaluacion_id=tipo_evaluacion_id).delete()

        db.session.delete(tipo)
        db.session.commit()
        return True

    @staticmethod
    def listar_tipos_evaluacion(seccion_id=None, nombre=None, evaluacion_id=None):
        query = TipoEvaluacion.query
        if seccion_id is not None:
            query = query.filter_by(seccion_id=seccion_id)
        if nombre:
            query = query.filter(TipoEvaluacion.nombre.ilike(f"%{nombre}%"))
        if evaluacion_id is not None:
            query = query.join(TipoEvaluacion.evaluaciones).filter(
                Evaluacion.id == evaluacion_id
            )
        return query.all()


class EvaluacionService:

    @staticmethod
    def crear_evaluacion(data):
        tipo = TipoEvaluacion.query.get(data["tipo_evaluacion_id"])
        if not tipo:
            raise ValueError("El tipo de evaluación no existe")

        detalle = DetalleMatricula.query.get(data["detalle_matricula_id"])
        if not detalle:
            raise ValueError("El detalle de matrícula no existe")

        evaluacion = Evaluacion(
            tipo_evaluacion_id=data["tipo_evaluacion_id"],
            detalle_matricula_id=data["detalle_matricula_id"],
            nota=data["nota"],
        )
        db.session.add(evaluacion)
        db.session.commit()
        return evaluacion

    @staticmethod
    def listar_evaluaciones(tipo_evaluacion_id=None, detalle_matricula_id=None):
        query = Evaluacion.query
        if tipo_evaluacion_id is not None:
            query = query.filter_by(tipo_evaluacion_id=tipo_evaluacion_id)
        if detalle_matricula_id is not None:
            query = query.filter_by(detalle_matricula_id=detalle_matricula_id)
        return query.all()

    @staticmethod
    def obtener_evaluacion(evaluacion_id):
        return Evaluacion.query.get(evaluacion_id)

    @staticmethod
    def actualizar_evaluacion(evaluacion_id, data):
        evaluacion = Evaluacion.query.get(evaluacion_id)
        if not evaluacion:
            return None
        if data.get("nota") is not None:
            evaluacion.nota = data["nota"]
        db.session.commit()
        return evaluacion

    @staticmethod
    def eliminar_evaluacion(evaluacion_id):
        evaluacion = Evaluacion.query.get(evaluacion_id)
        if not evaluacion:
            return False
        db.session.delete(evaluacion)
        db.session.commit()
        return True

    @staticmethod
    def obtener_estudiante(evaluacion_id):
        evaluacion = Evaluacion.query.get(evaluacion_id)
        if not evaluacion:
            return None
        detalle = evaluacion.detalle_matricula
        if not detalle:
            return None
        return detalle.matricula.estudiante

    @staticmethod
    def _calcular_promedio_por_detalle(detalle_matricula_id):
        detalle = DetalleMatricula.query.get(detalle_matricula_id)
        if not detalle:
            return None

        tipos = TipoEvaluacion.query.filter_by(seccion_id=detalle.seccion_id).all()
        evaluaciones = Evaluacion.query.filter_by(
            detalle_matricula_id=detalle_matricula_id
        ).all()

        eval_map = {e.tipo_evaluacion_id: e for e in evaluaciones}

        suma_ponderada = Decimal("0")
        suma_pesos = Decimal("0")
        for t in tipos:
            e = eval_map.get(t.id)
            if e and e.nota is not None:
                suma_ponderada += e.nota * t.peso
                suma_pesos += t.peso

        if suma_pesos > 0:
            promedio = (suma_ponderada / suma_pesos).quantize(Decimal("0.00"))
        else:
            promedio = None

        return float(promedio) if promedio else None

    @staticmethod
    def validar_promedio(detalle_matricula_id):
        detalle = DetalleMatricula.query.get(detalle_matricula_id)
        if not detalle:
            raise ValueError("El detalle de matrícula no existe")

        promedio = EvaluacionService._calcular_promedio_por_detalle(detalle_matricula_id)
        detalle.promedio_final = promedio
        detalle.is_validated = True
        db.session.commit()
        return float(promedio) if promedio else None

    @staticmethod
    def validar_todos_promedio(seccion_id):
        detalles = DetalleMatricula.query.filter_by(
            seccion_id=seccion_id,
            is_validated=False,
        ).all()

        count = 0
        for detalle in detalles:
            try:
                EvaluacionService.validar_promedio(detalle.id)
                count += 1
            except ValueError:
                continue

        return count

    @staticmethod
    def listar_notas_por_seccion(seccion_id):
        from ..models import Matricula, Estudiante, User

        # Tipos de evaluación de la sección
        tipos = TipoEvaluacion.query.filter_by(seccion_id=seccion_id).all()

        # if not tipos:
        #     return {"tipos_evaluacion": [], "estudiantes": []}

        # Detalles de matrícula de la sección con datos del estudiante
        detalles = (
            db.session.query(
                DetalleMatricula.id,
                Estudiante.id,
                User.nombres,
                User.apellidos,
                DetalleMatricula.promedio_final,
                DetalleMatricula.is_validated,
            )
            .join(Matricula, Matricula.id == DetalleMatricula.matricula_id)
            .join(Estudiante, Estudiante.id == Matricula.estudiante_id)
            .join(User, User.id == Estudiante.user_id)
            .filter(DetalleMatricula.seccion_id == seccion_id)
            .all()
        )

        detalle_ids = [d[0] for d in detalles]
        tipo_ids = [t.id for t in tipos]

        # Evaluaciones existentes → lookup (detalle_id, tipo_id) -> evaluacion
        evaluaciones = Evaluacion.query.filter(
            Evaluacion.detalle_matricula_id.in_(detalle_ids),
            Evaluacion.tipo_evaluacion_id.in_(tipo_ids),
        ).all()

        eval_map: dict[tuple[int, int], Evaluacion] = {
            (e.detalle_matricula_id, e.tipo_evaluacion_id): e for e in evaluaciones
        }

        estudiantes = []
        for detalle_id, est_id, nombres, apellidos, promedio, is_validated in detalles:
            notas = []
            suma_ponderada = Decimal("0")
            suma_pesos = Decimal("0")

            for t in tipos:
                e = eval_map.get((detalle_id, t.id))
                nota_valor = e.nota if e else None
                notas.append(
                    {
                        "tipo_evaluacion_id": t.id,
                        "evaluacion_id": e.id if e else None,
                        "nota": nota_valor,
                    }
                )
                if nota_valor is not None:
                    suma_ponderada += nota_valor * t.peso
                    suma_pesos += t.peso

            promedio_calculado = (
                (suma_ponderada / suma_pesos).quantize(Decimal("0.00"))
                if suma_pesos > 0
                else None
            )

            estudiantes.append(
                {
                    "detalle_matricula_id": detalle_id,
                    "estudiante_id": est_id,
                    "estudiante_nombre": f"{nombres} {apellidos}",
                    "notas": notas,
                    "promedio_final": promedio or promedio_calculado,
                    "is_validated": is_validated,
                }
            )

        return {
            "tipos_evaluacion": [
                {
                    "id": t.id,
                    "seccion_id": t.seccion_id,
                    "nombre": t.nombre,
                    "peso": t.peso,
                }
                for t in tipos
            ],
            "estudiantes": estudiantes,
        }

    @staticmethod
    def listar_notas_estudiante(id_estudiante, periodo_academico_id):
    
        matricula = Matricula.query.filter_by(
            estudiante_id=id_estudiante, periodo_academico_id=periodo_academico_id
        ).first()

        if not matricula:
            return []

        detalles = (
            db.session.query(DetalleMatricula, Seccion, Curso)
            .join(Seccion, Seccion.id == DetalleMatricula.seccion_id)
            .join(Curso, Curso.id == Seccion.curso_id)
            .filter(DetalleMatricula.matricula_id == matricula.id)
            .all()
        )
        result = []
        for detalle, seccion, curso in detalles:
            tipos = TipoEvaluacion.query.filter_by(seccion_id=seccion.id).all()
            evaluaciones = Evaluacion.query.filter_by(detalle_matricula_id=detalle.id).all()

            eval_map = {e.tipo_evaluacion_id: e for e in evaluaciones}

            evaluaciones_list = [
                {
                    "nombre": t.nombre,
                    "nota": (
                        float(eval_map[t.id].nota) if t.id in eval_map else Decimal("0")
                    ),
                    "peso": float(t.peso),
                }
                for t in tipos
            ]

            promedio_calculado = EvaluacionService._calcular_promedio_por_detalle(detalle.id)
            result.append(
                {
                    "curso": curso.nombre,
                    "seccion": seccion.nombre,
                    "promedio": (
                        float(detalle.promedio_final) if detalle.promedio_final else None
                    ),
                    "promedio_calculado": promedio_calculado,
                    "is_validated": detalle.is_validated,
                    "evaluaciones": evaluaciones_list,
                }
            )

        return result

    @staticmethod
    def estadisticas_notas(periodo_academico_id, curso_id=None, seccion_id=None):
        from ..models.docente import Docente
        from ..models.user import User

        query = (
            db.session.query(
                DetalleMatricula,
                Seccion,
                Curso,
                Docente,
                User,
                Matricula,
            )
            .join(Seccion, Seccion.id == DetalleMatricula.seccion_id)
            .join(Curso, Curso.id == Seccion.curso_id)
            .join(Docente, Docente.id == Seccion.docente_id)
            .join(User, User.id == Docente.user_id)
            .join(Matricula, Matricula.id == DetalleMatricula.matricula_id)
            .filter(Seccion.periodo_academico_id == periodo_academico_id)
        )

        if curso_id:
            query = query.filter(Seccion.curso_id == curso_id)
        if seccion_id:
            query = query.filter(Seccion.id == seccion_id)

        rows = query.all()
        total = len(rows)
        periodo = PeriodoAcademico.query.get(periodo_academico_id)

        if not rows:
            return {
                "periodo": periodo.semestre if periodo else "",
                "periodo_id": periodo_academico_id,
                "resumen": {
                    "total_estudiantes": 0,
                    "promedio_general": None,
                    "aprobados": 0,
                    "aprobados_porcentaje": None,
                    "desaprobados": 0,
                    "desaprobados_porcentaje": None,
                    "distribucion": {"00-05": 0, "05-10": 0, "10-15": 0, "15-20": 0},
                },
                "detalle": [],
            }

        promedios = []
        aprobados = 0
        distribucion = {"00-05": 0, "05-10": 0, "10-15": 0, "15-20": 0}

        for detalle, _, _, _, _, _ in rows:
            p = float(detalle.promedio_final) if detalle.promedio_final is not None else None
            if p is not None:
                promedios.append(p)
                if p >= 10.5:
                    aprobados += 1
                if p < 5:
                    distribucion["00-05"] += 1
                elif p < 10:
                    distribucion["05-10"] += 1
                elif p < 15:
                    distribucion["10-15"] += 1
                else:
                    distribucion["15-20"] += 1
            else:
                distribucion["00-05"] += 1

        desaprobados = total - aprobados
        promedio_general = round(sum(promedios) / len(promedios), 2) if promedios else None
        aprobados_pct = round(aprobados / total * 100, 1) if total else None
        desaprobados_pct = round(desaprobados / total * 100, 1) if total else None

        resumen = {
            "total_estudiantes": total,
            "promedio_general": promedio_general,
            "aprobados": aprobados,
            "aprobados_porcentaje": aprobados_pct,
            "desaprobados": desaprobados,
            "desaprobados_porcentaje": desaprobados_pct,
            "distribucion": distribucion,
        }

        if seccion_id:
            detalle_result = []
            for detalle, _, _, _, _, matricula in rows:
                estudiante = matricula.estudiante
                detalle_result.append({
                    "estudiante_id": estudiante.id,
                    "estudiante": f"{estudiante.user.nombres} {estudiante.user.apellidos}",
                    "promedio": float(detalle.promedio_final) if detalle.promedio_final is not None else None,
                    "estado": detalle.estado_curso,
                })
            detalle_result.sort(key=lambda x: x["promedio"] or 0, reverse=True)
        elif curso_id:
            from collections import defaultdict
            grupos = defaultdict(lambda: {"seccion_id": None, "seccion": "", "curso": "", "docente": "", "total": 0, "promedios": [], "aprobados": 0})
            for detalle, seccion, curso, _, user, _ in rows:
                key = seccion.id
                g = grupos[key]
                g["seccion_id"] = seccion.id
                g["seccion"] = seccion.nombre
                g["curso"] = curso.nombre
                g["docente"] = f"{user.nombres} {user.apellidos}"
                g["total"] += 1
                p = float(detalle.promedio_final) if detalle.promedio_final is not None else None
                if p is not None:
                    g["promedios"].append(p)
                    if p >= 10.5:
                        g["aprobados"] += 1
            detalle_result = [
                {
                    "seccion_id": g["seccion_id"],
                    "seccion": g["seccion"],
                    "curso": g["curso"],
                    "docente": g["docente"],
                    "total_estudiantes": g["total"],
                    "promedio": round(sum(g["promedios"]) / len(g["promedios"]), 2) if g["promedios"] else None,
                    "aprobados": g["aprobados"],
                    "desaprobados": g["total"] - g["aprobados"],
                }
                for g in sorted(grupos.values(), key=lambda x: x["seccion"])
            ]
        else:
            from collections import defaultdict
            grupos = defaultdict(lambda: {"curso_id": None, "curso": "", "total": 0, "promedios": [], "aprobados": 0})
            for detalle, seccion, curso, _, _, _ in rows:
                key = curso.id
                g = grupos[key]
                g["curso_id"] = curso.id
                g["curso"] = curso.nombre
                g["total"] += 1
                p = float(detalle.promedio_final) if detalle.promedio_final is not None else None
                if p is not None:
                    g["promedios"].append(p)
                    if p >= 10.5:
                        g["aprobados"] += 1
            detalle_result = [
                {
                    "curso_id": g["curso_id"],
                    "curso": g["curso"],
                    "total_estudiantes": g["total"],
                    "promedio": round(sum(g["promedios"]) / len(g["promedios"]), 2) if g["promedios"] else None,
                    "aprobados": g["aprobados"],
                    "desaprobados": g["total"] - g["aprobados"],
                }
                for g in sorted(grupos.values(), key=lambda x: x["curso"])
            ]

        return {
            "periodo": periodo.semestre if periodo else "",
            "periodo_id": periodo_academico_id,
            "resumen": resumen,
            "detalle": detalle_result,
        }

    @staticmethod
    def record_academico(id_estudiante):
        matriculas = (
            Matricula.query
            .filter_by(estudiante_id=id_estudiante)
            .order_by(Matricula.periodo_academico_id)
            .all()
        )

        result = []
        for matricula in matriculas:
            detalles = (
                db.session.query(DetalleMatricula, Seccion, Curso)
                .join(Seccion, Seccion.id == DetalleMatricula.seccion_id)
                .join(Curso, Curso.id == Seccion.curso_id)
                .filter(DetalleMatricula.matricula_id == matricula.id)
                .order_by(Curso.semestre_num)
                .all()
            )

            if not detalles:
                continue

            cursos = []
            for detalle, seccion, curso in detalles:
                prerequisitos = [p.nombre for p in curso.prerequisitos]
                cursos.append({
                    "nombre": curso.nombre,
                    "semestre_num": curso.semestre_num,
                    "prerequisitos": prerequisitos,
                    "promedio": float(detalle.promedio_final) if detalle.promedio_final else None,
                })

            result.append({
                "periodo": matricula.periodo_academico.semestre,
                "periodo_id": matricula.periodo_academico_id,
                "cursos": cursos,
            })

        return result

    @staticmethod
    def record_academico_stats(periodo_academico_id):
        from ..models.docente import Docente
        from ..models.user import User
        from collections import defaultdict

        query = (
            db.session.query(
                DetalleMatricula,
                Seccion,
                Curso,
                Docente,
                User,
            )
            .join(Seccion, Seccion.id == DetalleMatricula.seccion_id)
            .join(Curso, Curso.id == Seccion.curso_id)
            .join(Docente, Docente.id == Seccion.docente_id)
            .join(User, User.id == Docente.user_id)
            .filter(Seccion.periodo_academico_id == periodo_academico_id)
            .order_by(Curso.semestre_num, Curso.nombre, Seccion.nombre)
        )

        rows = query.all()
        periodo = PeriodoAcademico.query.get(periodo_academico_id)

        cursos_map = defaultdict(list)
        for detalle, seccion, curso, _, user in rows:
            p = float(detalle.promedio_final) if detalle.promedio_final is not None else None
            cursos_map[curso.id].append({
                "seccion_id": seccion.id,
                "seccion": seccion.nombre,
                "docente": f"{user.nombres} {user.apellidos}",
                "promedio": p,
                "estado": detalle.estado_curso,
            })

        cursos_result = []
        for curso_id, grupo in sorted(cursos_map.items()):
            curso = Curso.query.get(curso_id)
            secciones_map = defaultdict(list)
            for item in grupo:
                secciones_map[item["seccion_id"]].append(item)

            secciones_result = []
            for sec_id, items in sorted(secciones_map.items()):
                promedios = [i["promedio"] for i in items if i["promedio"] is not None]
                total = len(items)
                aprobados = sum(1 for i in items if i["estado"] == "aprobado")
                desaprobados = sum(1 for i in items if i["estado"] == "desaprobado")
                en_curso = sum(1 for i in items if i["estado"] not in ("aprobado", "desaprobado"))
                secciones_result.append({
                    "seccion_id": sec_id,
                    "seccion": items[0]["seccion"],
                    "docente": items[0]["docente"],
                    "total_estudiantes": total,
                    "promedio": round(sum(promedios) / len(promedios), 2) if promedios else None,
                    "aprobados": aprobados,
                    "desaprobados": desaprobados,
                    "en_curso": en_curso,
                })

            todos_promedios = [i["promedio"] for i in grupo if i["promedio"] is not None]
            cursos_result.append({
                "curso_id": curso.id,
                "curso": curso.nombre,
                "semestre_num": curso.semestre_num,
                "total_estudiantes": len(grupo),
                "promedio": round(sum(todos_promedios) / len(todos_promedios), 2) if todos_promedios else None,
                "secciones": secciones_result,
            })

        return {
            "periodo": periodo.semestre if periodo else "",
            "periodo_id": periodo_academico_id,
            "cursos": cursos_result,
        }

    @staticmethod
    def generar_reporte_record_academico_pdf(periodo_academico_id):
        stats = EvaluacionService.record_academico_stats(periodo_academico_id)
        periodo = PeriodoAcademico.query.get(periodo_academico_id)
        periodo_label = periodo.semestre if periodo else ""

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        y = height - 2 * cm

        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, y, "Reporte de Record Académico")
        y -= 0.8 * cm
        c.setFont("Helvetica", 10)
        c.drawCentredString(width / 2, y, "Universidad Nacional del Centro del Perú")
        y -= 1.2 * cm

        c.setFont("Helvetica", 10)
        c.drawString(2 * cm, y, f"Periodo académico: {periodo_label}")
        y -= 1 * cm

        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y, "Cursos y secciones")
        y -= 0.7 * cm

        for curso in stats["cursos"]:
            if y < 4 * cm:
                c.showPage()
                y = height - 2 * cm

            c.setFont("Helvetica-Bold", 11)
            c.drawString(2 * cm, y, f"{curso['curso']} (Sem. {curso['semestre_num']})")
            y -= 0.5 * cm
            c.setFont("Helvetica", 9)
            c.drawString(2 * cm, y, f"Promedio general: {curso['promedio'] if curso['promedio'] else '—'}  |  Total: {curso['total_estudiantes']}")
            y -= 0.4 * cm

            c.setFont("Helvetica-Bold", 9)
            col_widths = [2 * cm, 4 * cm, 2.5 * cm, 2 * cm, 2 * cm, 2 * cm, 2 * cm]
            headers = ["Sección", "Docente", "Estudiantes", "Promedio", "Aprob.", "Desap.", "En curso"]
            x_start = 3 * cm
            for i, h in enumerate(headers):
                c.drawString(x_start + sum(col_widths[:i]), y, h)
            y -= 0.3 * cm
            c.line(3 * cm, y, width - 2 * cm, y)
            y -= 0.4 * cm

            c.setFont("Helvetica", 8)
            for sec in curso["secciones"]:
                if y < 2 * cm:
                    c.showPage()
                    y = height - 2 * cm

                vals = [
                    sec["seccion"],
                    sec["docente"],
                    str(sec["total_estudiantes"]),
                    str(sec["promedio"]) if sec["promedio"] else "—",
                    str(sec["aprobados"]),
                    str(sec["desaprobados"]),
                    str(sec["en_curso"]),
                ]
                for i, v in enumerate(vals):
                    text = v[:30] if len(v) > 30 else v
                    c.drawString(x_start + sum(col_widths[:i]), y, text)
                y -= 0.4 * cm
            y -= 0.5 * cm

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    @staticmethod
    def generar_reporte_estadisticas_pdf(periodo_academico_id, curso_id=None, seccion_id=None, curso_nombre="", seccion_nombre=""):
        stats = EvaluacionService.estadisticas_notas(
            periodo_academico_id, curso_id=curso_id, seccion_id=seccion_id
        )
        periodo = PeriodoAcademico.query.get(periodo_academico_id)
        periodo_label = periodo.semestre if periodo else ""

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        y = height - 2 * cm

        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, y, "Reporte de Estadísticas de Notas")
        y -= 0.8 * cm
        c.setFont("Helvetica", 10)
        c.drawCentredString(width / 2, y, "Universidad Nacional del Centro del Perú")
        y -= 1.2 * cm

        c.setFont("Helvetica", 10)
        c.drawString(2 * cm, y, f"Periodo académico: {periodo_label}")
        y -= 0.5 * cm
        if curso_nombre:
            c.drawString(2 * cm, y, f"Curso: {curso_nombre}")
            y -= 0.5 * cm
        if seccion_nombre:
            c.drawString(2 * cm, y, f"Sección: {seccion_nombre}")
            y -= 0.5 * cm
        y -= 0.5 * cm

        resumen = stats["resumen"]
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y, "Resumen")
        y -= 0.7 * cm
        c.setFont("Helvetica", 10)
        c.drawString(2 * cm, y, f"Total estudiantes: {resumen['total_estudiantes']}")
        y -= 0.5 * cm
        pg = resumen["promedio_general"]
        c.drawString(2 * cm, y, f"Promedio general: {pg if pg is not None else '—'}")
        y -= 0.5 * cm
        c.drawString(2 * cm, y, f"Aprobados: {resumen['aprobados']} ({resumen.get('aprobados_porcentaje', '—')}%)")
        y -= 0.5 * cm
        c.drawString(2 * cm, y, f"Desaprobados: {resumen['desaprobados']} ({resumen.get('desaprobados_porcentaje', '—')}%)")
        y -= 0.5 * cm
        y -= 0.5 * cm

        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y, "Distribución de notas")
        y -= 0.7 * cm
        c.setFont("Helvetica", 10)
        distribucion = resumen.get("distribucion", {})
        for rango in ["00-05", "05-10", "10-15", "15-20"]:
            count = distribucion.get(rango, 0)
            c.drawString(3 * cm, y, f"{rango}: {count} estudiantes")
            y -= 0.5 * cm
        y -= 0.5 * cm

        detalle = stats.get("detalle", [])
        if detalle:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(2 * cm, y, "Detalle")
            y -= 0.7 * cm

            if seccion_id:
                col_widths = [10 * cm, 3 * cm, 3 * cm]
                headers = ["Estudiante", "Promedio", "Estado"]
            elif curso_id:
                col_widths = [3 * cm, 5 * cm, 3 * cm, 2 * cm, 2 * cm, 2 * cm]
                headers = ["Sección", "Curso", "Docente", "Est.", "Prom.", "Aprob."]
            else:
                col_widths = [8 * cm, 3 * cm, 3 * cm, 3 * cm, 3 * cm]
                headers = ["Curso", "Est.", "Prom.", "Aprob.", "Desap."]

            c.setFont("Helvetica-Bold", 8)
            x_start = 2 * cm
            for i, h in enumerate(headers):
                c.drawString(x_start + sum(col_widths[:i]), y, h)
            y -= 0.3 * cm
            c.line(2 * cm, y, width - 2 * cm, y)
            y -= 0.4 * cm

            c.setFont("Helvetica", 8)

            if y < 3 * cm:
                c.showPage()
                y = height - 2 * cm
                c.setFont("Helvetica-Bold", 8)
                for i, h in enumerate(headers):
                    c.drawString(x_start + sum(col_widths[:i]), y, h)
                y -= 0.3 * cm
                c.line(2 * cm, y, width - 2 * cm, y)
                y -= 0.4 * cm
                c.setFont("Helvetica", 8)

            for row in detalle:
                if y < 2 * cm:
                    c.showPage()
                    y = height - 2 * cm
                    c.setFont("Helvetica-Bold", 8)
                    for i, h in enumerate(headers):
                        c.drawString(x_start + sum(col_widths[:i]), y, h)
                    y -= 0.3 * cm
                    c.line(2 * cm, y, width - 2 * cm, y)
                    y -= 0.4 * cm
                    c.setFont("Helvetica", 8)

                if "estudiante" in row:
                    vals = [
                        row.get("estudiante", ""),
                        str(row.get("promedio", "—")),
                        row.get("estado", ""),
                    ]
                elif "seccion" in row:
                    vals = [
                        row.get("seccion", ""),
                        row.get("curso", ""),
                        row.get("docente", ""),
                        str(row.get("total_estudiantes", "")),
                        str(row.get("promedio", "—")),
                        str(row.get("aprobados", "")),
                    ]
                else:
                    vals = [
                        row.get("curso", ""),
                        str(row.get("total_estudiantes", "")),
                        str(row.get("promedio", "—")),
                        str(row.get("aprobados", "")),
                        str(row.get("desaprobados", "")),
                    ]

                for i, v in enumerate(vals):
                    text = v[:35] if len(v) > 35 else v
                    c.drawString(x_start + sum(col_widths[:i]), y, text)
                y -= 0.45 * cm

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer
