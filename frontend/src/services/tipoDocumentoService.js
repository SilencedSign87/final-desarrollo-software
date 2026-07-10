import { apiClient } from "./api"

export const getTiposDocumento = async () => {
    return apiClient.get("/tipos-documento/")
}

export const createTipoDocumento = async (data) => {
    return apiClient.post("/tipos-documento/", data)
}

export const updateTipoDocumento = async (tipoId, data) => {
    return apiClient.put(`/tipos-documento/${tipoId}`, data)
}

export const deleteTipoDocumento = async (tipoId) => {
    return apiClient.delete(`/tipos-documento/${tipoId}`)
}
