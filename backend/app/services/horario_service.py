from ..extensions import db
from ..models.horario import Horario
from ..models.seccion import Seccion


class HorarioService:

    @staticmethod
    def _hay_cruce(seccion, dia_semana, hora_inicio, hora_final, excluir_horario_id=None):
        """
        Revisa si ya existe otro horario en la MISMA aula, el MISMO día,
        que se cruce en el rango de horas con el nuevo horario propuesto.
        """
        candidatos = Horario.query.filter_by(dia_semana=dia_semana).all()
        for h in candidatos:
            if excluir_horario_id and h.id == excluir_horario_id:
                continue
            # Solo importa el cruce si es la misma aula
            if h.aula != seccion["aula"]:
                continue
            # Dos rangos de horas se cruzan si uno empieza antes de que el otro termine
            if hora_inicio < h.hora_final and hora_final > h.hora_inicio:
                return h
        return None

    @staticmethod
    def _hay_cruce_docente(seccion, dia_semana, hora_inicio, hora_final, excluir_horario_id=None):
        if seccion["docente_id"] is None:
            return None

        candidatos = (
            Horario.query.join(Seccion, Horario.seccion_id == Seccion.id)
            .filter(
                Horario.dia_semana == dia_semana,
                Seccion.docente_id == seccion["docente_id"],
                Seccion.periodo_academico_id == seccion["periodo_academico_id"],
                Seccion.id != seccion["seccion_id"],
            )
            .all()
        )
        for h in candidatos:
            if excluir_horario_id and h.id == excluir_horario_id:
                continue
            if hora_inicio < h.hora_final and hora_final > h.hora_inicio:
                return h
        return None

    @staticmethod
    def crear_horario(data):
        seccion = Seccion.query.get(data["seccion_id"])
        if not seccion:
            raise ValueError("La sección no existe")

        cruce = HorarioService._hay_cruce(
            {"aula": data["aula"]},
            data["dia_semana"],
            data["hora_inicio"],
            data["hora_final"],
        )
        if cruce:
            raise ValueError(
                f"El aula '{data['aula']}' ya está ocupada ese día en ese horario"
            )

        cruce_docente = HorarioService._hay_cruce_docente(
            {
                "docente_id": seccion.docente_id,
                "periodo_academico_id": seccion.periodo_academico_id,
                "seccion_id": seccion.id,
            },
            data["dia_semana"],
            data["hora_inicio"],
            data["hora_final"],
        )
        if cruce_docente:
            cruce_seccion = Seccion.query.get(cruce_docente.seccion_id)
            raise ValueError(
                f"El docente ya tiene una clase en la sección '{cruce_seccion.nombre}' "
                f"ese día en un horario que se cruza"
            )

        horario = Horario(
            seccion_id=data["seccion_id"],
            dia_semana=data["dia_semana"],
            hora_inicio=data["hora_inicio"],
            hora_final=data["hora_final"],
            aula=data["aula"],
        )
        db.session.add(horario)
        db.session.commit()
        return horario

    @staticmethod
    def listar_horarios(seccion_id=None):
        query = Horario.query
        if seccion_id:
            query = query.filter_by(seccion_id=seccion_id)
        return query.all()

    @staticmethod
    def obtener_horario(horario_id):
        return Horario.query.get(horario_id)

    @staticmethod
    def actualizar_horario(horario_id, data):
        horario = Horario.query.get(horario_id)
        if not horario:
            return None

        seccion = Seccion.query.get(horario.seccion_id)

        nuevo_dia = data.get("dia_semana") if data.get("dia_semana") is not None else horario.dia_semana
        nueva_hora_inicio = data.get("hora_inicio") if data.get("hora_inicio") is not None else horario.hora_inicio
        nueva_hora_final = data.get("hora_final") if data.get("hora_final") is not None else horario.hora_final
        nueva_aula = data.get("aula") if data.get("aula") is not None else horario.aula

        cruce = HorarioService._hay_cruce(
            {"aula": nueva_aula},
            nuevo_dia,
            nueva_hora_inicio,
            nueva_hora_final,
            excluir_horario_id=horario.id,
        )
        if cruce:
            raise ValueError(
                f"El aula '{nueva_aula}' ya está ocupada ese día en ese horario"
            )

        cruce_docente = HorarioService._hay_cruce_docente(
            {
                "docente_id": seccion.docente_id,
                "periodo_academico_id": seccion.periodo_academico_id,
                "seccion_id": seccion.id,
            },
            nuevo_dia,
            nueva_hora_inicio,
            nueva_hora_final,
            excluir_horario_id=horario.id,
        )
        if cruce_docente:
            cruce_seccion = Seccion.query.get(cruce_docente.seccion_id)
            raise ValueError(
                f"El docente ya tiene una clase en la sección '{cruce_seccion.nombre}' "
                f"ese día en un horario que se cruza"
            )

        horario.dia_semana = nuevo_dia
        horario.hora_inicio = nueva_hora_inicio
        horario.hora_final = nueva_hora_final
        horario.aula = nueva_aula

        db.session.commit()
        return horario

    @staticmethod
    def eliminar_horario(horario_id):
        horario = Horario.query.get(horario_id)
        if not horario:
            return False
        db.session.delete(horario)
        db.session.commit()
        return True