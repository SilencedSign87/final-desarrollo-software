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
    }
}