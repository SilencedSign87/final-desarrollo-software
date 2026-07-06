import { apiClient } from "./api"

export const Login = async (credentials) => {
    if (!credentials.email || !credentials.password) {
        throw new Error("Email and password are required")
    }

    return apiClient.post('/auth/login', credentials)
}

export const Logout = async () => {
    return apiClient.post('/auth/logout')
}

export const CheckAuth = async () => {
    return await apiClient.get('/auth/current_user')
}