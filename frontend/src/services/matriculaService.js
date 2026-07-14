import { apiClient, resolveApiUrl } from "./api"

export const getMatriculas = async (estado) => {
    return apiClient.get('/matriculas/', { params: { estado } })
}

export const getMisMatriculas = async () => {
    return apiClient.get('/matriculas/mias')
}

export const getMatricula = async (matriculaId) => {
    return apiClient.get(`/matriculas/${matriculaId}`)
}

export const createMatricula = async ({ periodo_academico_id, secciones_ids, comprobante }) => {
    const formData = new FormData()
    formData.append('periodo_academico_id', String(periodo_academico_id))
    formData.append('secciones_ids', JSON.stringify(secciones_ids))
    if (comprobante) {
        formData.append('comprobante', comprobante)
    }
    return apiClient.post('/matriculas/', formData)
}

export const validarMatricula = async (matriculaId, data) => {
    return apiClient.put(`/matriculas/${matriculaId}/validar`, data)
}

export const getMatriculaEstadisticas = async () => {
    return apiClient.get('/matriculas/estadisticas')
}

export const getFichaDownloadUrl = (matriculaId) => {
    return resolveApiUrl(`/matriculas/${matriculaId}/ficha`)
}

export const getComprobanteDownloadUrl = (matriculaId) => {
    return resolveApiUrl(`/matriculas/${matriculaId}/comprobante`)
}
