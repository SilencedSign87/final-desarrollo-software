import { apiClient } from "./api"

export const DocenteService = {
    Search: async () => {
        return apiClient.get('docentes/')
    },

    Get: async (docenteId) => {
        return apiClient.get(`docentes/${docenteId}`)
    },

    Me: async () => {
        return apiClient.get('docentes/me')
    },

    Create: async (data) => {
        return apiClient.post('docentes/', data)
    },

    Update: async (docenteId, data) => {
        return apiClient.put(`docentes/${docenteId}`, data)
    },

    Secciones: async (docenteId, { periodo_academico_id } = {}) => {
        return apiClient.get(`docentes/${docenteId}/secciones`, {
            params: { periodo_academico_id }
        })
    },

    CargaDocente: async () => {
        return apiClient.get('docentes/carga-docente')
    },
}