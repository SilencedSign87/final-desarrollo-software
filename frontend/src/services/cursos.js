import { apiClient } from "./api"

export const getCursos = async ({ plan_estudios_id, semestre_num } = {}) => {
    return apiClient.get('/cursos/', { params: { plan_estudios_id, semestre_num } })
}

export const getCurso = async (cursoId) => {
    return apiClient.get(`/cursos/${cursoId}`)
}

export const createCurso = async (data) => {
    return apiClient.post('/cursos/', data)
}

export const updateCurso = async (cursoId, data) => {
    return apiClient.put(`/cursos/${cursoId}`, data)
}

export const deleteCurso = async (cursoId) => {
    return apiClient.delete(`/cursos/${cursoId}`)
}

// Se mantiene por compatibilidad con el stub previo (GetCursos)
export const GetCursos = getCursos