import { apiClient } from "./api"

export const getDocumentRequests = async () => {
    return apiClient.get('/documentos/solicitudes')
}

export const createDocumentRequest = async (data) => {
    return apiClient.post('/documentos/solicitudes', data)
}

export const authorizeDocumentRequest = async (requestId, data) => {
    return apiClient.post(`/documentos/solicitudes/${requestId}/autorizar`, data)
}

export const issueDocument = async (requestId) => {
    return apiClient.post(`/documentos/solicitudes/${requestId}/emitir`)
}

export const getDocumentDownloadUrl = (requestId) => {
    return `/api/documentos/solicitudes/${requestId}/archivo`
}

export const verifyDocument = async (qrHash) => {
    return apiClient.get(`/documentos/verificar/${qrHash}`)
}
