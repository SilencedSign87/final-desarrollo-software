import axios from "axios";

/**
 * @description Instancia de Axios con la URL base configurada a '/api'
 */
export const apiClient = axios.create({
    baseURL: '/api',
    withCredentials: true
})

export const healthCheck = async () => apiClient.get('/health')
