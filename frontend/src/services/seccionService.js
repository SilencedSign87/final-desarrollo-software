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

    UploadSilabo: async (seccionId, file) => {
        const formData = new FormData()
        formData.append('silabo', file)
        return apiClient.put(`secciones/${seccionId}/silabo`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        })
    },

    VerSilabo: async (seccionId) => {
        const response = await apiClient.get(`secciones/${seccionId}/silabo`, {
            responseType: 'blob',
        })
        const blobUrl = URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
        window.open(blobUrl, '_blank')
    },

    Delete: async (seccionId) => {
        return apiClient.delete(`secciones/${seccionId}`)
    },
}