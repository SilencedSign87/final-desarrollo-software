import { apiClient } from "./api"

export const PeriodoAcademicoService = {
    search: async ({ semestre, estado } = {}) => {
        return apiClient.get("/periodos-academicos", { params: { semestre, estado } })
    },

    getById: async (id) => {
        return apiClient.get(`/periodos-academicos/${id}`)
    },
    getCursosByPeriodoAcademico: async (periodoAcademicoId) => {
        return apiClient.get(`/periodos-academicos/${periodoAcademicoId}/cursos`)
    },
    getPeriodosMatriculados: async (estudianteId) => {
        return apiClient.get(`/periodos-academicos/me`)
    }
}