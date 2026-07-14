import { apiClient, resolveApiUrl } from "./api"

export const getDocumentRequests = async ({ page = 1, per_page = 10, estado } = {}) => {
    return apiClient.get('/documentos/solicitudes', {
        params: {
            page,
            per_page,
            ...(estado ? { estado } : {}),
        },
    })
}

export const createDocumentRequest = async ({ tipo_documento_id, tipo_documento, comprobante }) => {
    const formData = new FormData()
    if (tipo_documento_id != null) {
        formData.append('tipo_documento_id', String(tipo_documento_id))
    }
    if (tipo_documento) {
        formData.append('tipo_documento', tipo_documento)
    }
    if (comprobante) {
        formData.append('comprobante', comprobante)
    }
    return apiClient.post('/documentos/solicitudes', formData)
}

export const authorizeDocumentRequest = async (requestId, data) => {
    return apiClient.post(`/documentos/solicitudes/${requestId}/autorizar`, data)
}

export const issueDocument = async (requestId) => {
    return apiClient.post(`/documentos/solicitudes/${requestId}/emitir`)
}

export const getDocumentDownloadUrl = (requestId) => {
    return resolveApiUrl(`/documentos/solicitudes/${requestId}/archivo`)
}

export const getDocumentComprobanteUrl = (requestId) => {
    return resolveApiUrl(`/documentos/solicitudes/${requestId}/comprobante`)
}

export const verifyDocument = async (qrHash) => {
    return apiClient.get(`/documentos/verificar/${qrHash}`)
}
