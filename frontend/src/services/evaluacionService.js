import { apiClient } from "./api"

export const EvaluacionService = {
    searchEvaluaciones: async ({ tipo_evaluacion_id, detalle_matricula_id } = {}) => {
        return apiClient.get("/evaluaciones", {
            params: {
                tipo_evaluacion_id,
                detalle_matricula_id
            }
        })
    },
    searchTipoEvaluaciones: async ({ seccion_id, nombre, evaluacion_id } = {}) => {
        return apiClient.get("/evaluaciones/tipo-evaluaciones", {
            params: {
                seccion_id,
                nombre,
                evaluacion_id
            }
        })
    },
    crearEvaluacion: async ({ detalle_matricula_id, nota, tipo_evaluacion_id }) => {
        return apiClient.post("/evaluaciones", {
            detalle_matricula_id,
            nota,
            tipo_evaluacion_id
        })
    },
    crearTipoEvaluacion: async ({ seccion_id, nombre, peso }) => {
        return apiClient.post("/evaluaciones/tipo-evaluaciones", {
            nombre,
            peso,
            seccion_id,
        })
    },
    searchNotasPorSeccion: async ({ seccion_id }) => {
        return apiClient.get(`/evaluaciones/seccion/${seccion_id}/notas`)
    },
    actualizarEvaluacion: async ({ id, nota }) => {
        return apiClient.put(`/evaluaciones/${id}`, { nota })
    },
    actualizarTipoEvaluacion: async ({ id, nombre, peso }) => {
        return apiClient.put(`/evaluaciones/tipo-evaluaciones/${id}`, { nombre, peso })
    },
    eliminarTipoEvaluacion: async ({ id }) => {
        return apiClient.delete(`/evaluaciones/tipo-evaluaciones/${id}`)
    },
    getMisNotas: async ({ periodo_academico_id }) => {
        return apiClient.get(`/evaluaciones/estudiante/mis-notas`, { params: { periodo_academico_id } })
    },
    validarPromedio: async ({ seccion_id, detalle_matricula_id }) => {
        return apiClient.post(`/evaluaciones/seccion/${seccion_id}/validar-promedio`, {
            detalle_matricula_id
        })
    },
    getRecordAcademico: async () => {
        return apiClient.get("/evaluaciones/estudiante/record-academico")
    },
    getEstadisticasDireccion: async ({ periodo_academico_id, curso_id, seccion_id } = {}) => {
        return apiClient.get("/evaluaciones/direccion/estadisticas", {
            params: { periodo_academico_id, curso_id, seccion_id }
        })
    }
}