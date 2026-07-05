import axios from "axios";

const api = axios.create({
    baseURL: '/api'
})

export const healthCheck = async () => api.get('/health')
