import { apiClient } from "./api"

export const getMatriculas = async (estado) => {
    return apiClient.get('/matriculas/', { params: { estado } })
}

export const getMatricula = async (matriculaId) => {
    return apiClient.get(`/matriculas/${matriculaId}`)
}

export const createMatricula = async (data) => {
    return apiClient.post('/matriculas/', data)
}

export const validarMatricula = async (matriculaId, data) => {
    return apiClient.put(`/matriculas/${matriculaId}/validar`, data)
}

export const getMatriculaEstadisticas = async () => {
    return apiClient.get('/matriculas/estadisticas')
}

export const getFichaDownloadUrl = (matriculaId) => {
    return `/api/matriculas/${matriculaId}/ficha`
}