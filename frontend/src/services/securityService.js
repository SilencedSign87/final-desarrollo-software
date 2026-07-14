import { apiClient } from "./api"

export const getRoles = async () => {
    return apiClient.get('/seguridad/roles')
}

export const getUsers = async () => {
    return apiClient.get('/seguridad/usuarios')
}

export const createUser = async (data) => {
    return apiClient.post('/seguridad/usuarios', data)
}

export const updateUserRole = async (userId, data) => {
    return apiClient.put(`/seguridad/usuarios/${userId}/rol`, data)
}

export const getAuditSummary = async () => {
    return apiClient.get('/seguridad/auditorias/resumen')
}

export const getAuditLogs = async ({ page = 1, per_page = 15, accion } = {}) => {
    return apiClient.get('/seguridad/auditorias/logs', {
        params: {
            page,
            per_page,
            ...(accion ? { accion } : {}),
        },
    })
}

export const getRoleChangeHistory = async ({ page = 1, per_page = 10 } = {}) => {
    return apiClient.get('/seguridad/auditorias/cambios-rol', {
        params: { page, per_page },
    })
}
