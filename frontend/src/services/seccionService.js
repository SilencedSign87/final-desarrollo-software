import { apiClient } from "./api"

export const SeccionService = {
    Search: async({curso_id, docente_id, periodo_academico_id} = {}) => {
        return apiClient.get('secciones/', {
            params: {
                curso_id,
                docente_id,
                periodo_academico_id
            }
        })
    },

    Get: async (seccionId) => {
        return apiClient.get(`secciones/${seccionId}`)
    },

    Create: async (data) => {
        return apiClient.post('secciones/', data)
    },

    Update: async (seccionId, data) => {
        return apiClient.put(`secciones/${seccionId}`, data)
    },

    UploadSilabo: async (seccionId, silabo_url) => {
        return apiClient.put(`secciones/${seccionId}/silabo`, { silabo_url })
    },

    Delete: async (seccionId) => {
        return apiClient.delete(`secciones/${seccionId}`)
    },
}