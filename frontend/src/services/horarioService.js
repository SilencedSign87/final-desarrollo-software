import { apiClient } from "./api"

export const HorarioService = {
    Search: async ({ seccion_id } = {}) => {
        return apiClient.get('horarios/', { params: { seccion_id } })
    },

    Create: async (data) => {
        return apiClient.post('horarios/', data)
    },

    Update: async (horarioId, data) => {
        return apiClient.put(`horarios/${horarioId}`, data)
    },

    Delete: async (horarioId) => {
        return apiClient.delete(`horarios/${horarioId}`)
    },
}