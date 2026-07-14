import axios from "axios";

/**
 * @description Instancia de Axios con la URL base configurada a '/api'
 */
export const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    withCredentials: true
})

/**
 * Resuelve rutas de la API a una URL usable en el navegador (enlaces, descargas).
 * En producción apunta al backend (VITE_API_URL); en local sigue usando /api vía proxy.
 * Si el backend devolvió una URL absoluta a localhost, la reescribe con VITE_API_URL.
 */
export const resolveApiUrl = (pathOrUrl) => {
    if (!pathOrUrl) return pathOrUrl

    let path = pathOrUrl

    if (pathOrUrl.startsWith('http://') || pathOrUrl.startsWith('https://')) {
        try {
            const url = new URL(pathOrUrl)
            const isLocal = url.hostname === 'localhost' || url.hostname === '127.0.0.1'
            if (!isLocal) {
                return pathOrUrl
            }
            path = `${url.pathname}${url.search}`
        } catch {
            return pathOrUrl
        }
    }

    const base = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '')

    if (path.startsWith('/api/')) {
        return `${base}${path.slice(4)}`
    }

    const normalized = path.startsWith('/') ? path : `/${path}`
    return `${base}${normalized}`
}

export const healthCheck = async () => apiClient.get('/health')
