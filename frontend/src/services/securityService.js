import { apiClient } from "./api"

export const getRoles = async () => {
    return apiClient.get('/seguridad/roles')
}

export const getUsers = async () => {
    return apiClient.get('/seguridad/usuarios')
}

export const updateUserRole = async (userId, data) => {
    return apiClient.put(`/seguridad/usuarios/${userId}/rol`, data)
}

export const getAuditSummary = async () => {
    return apiClient.get('/seguridad/auditorias/resumen')
}
