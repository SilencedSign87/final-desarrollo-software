import { apiClient } from "./api"

export const Login = (credentials) => {
    if (!credentials.email || !credentials.password) {
        throw new Error("Email and password are required")
    }

    return apiClient.post('/auth/login', credentials)
}

export const Register = (userData) => {
    if (!userData.nombres || !userData.apellidos || !userData.email || !userData.password || !userData.dni || !userData.rol) {
        throw new Error("Todos los campos son obligatorios")
    }

    return apiClient.post('/auth/register', userData)
}

export const Logout = () => {
    return apiClient.post('/auth/logout')
}

export const CheckAuth = () => {
    return apiClient.get('/auth/current_user')
}