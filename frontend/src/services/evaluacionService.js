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

    }
}