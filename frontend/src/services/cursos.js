import { apiClient } from "./api"

export const GetCursos = ({ plan_estudios_id, semestre_num } = {}) => {
    return apiClient.get('/cursos/', {
        params: { plan_estudios_id, semestre_num },
    })
}

export const GetCursosDisponibles = () => {
    return apiClient.get('/cursos/disponibles')
}