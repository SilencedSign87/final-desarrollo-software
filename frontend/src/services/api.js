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
 */
export const resolveApiUrl = (pathOrUrl) => {
    if (!pathOrUrl) return pathOrUrl
    if (pathOrUrl.startsWith('http://') || pathOrUrl.startsWith('https://')) {
        return pathOrUrl
    }

    const base = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '')

    if (pathOrUrl.startsWith('/api/')) {
        return `${base}${pathOrUrl.slice(4)}`
    }

    const path = pathOrUrl.startsWith('/') ? pathOrUrl : `/${pathOrUrl}`
    return `${base}${path}`
}

export const healthCheck = async () => apiClient.get('/health')
