import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { CheckAuth, Login as loginRequest, Logout as logoutRequest } from '../services/authService'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null)
    const [isLoading, setIsLoading] = useState(true)

    const fetchUser = useCallback(async () => {
        try {
            const response = await CheckAuth()
            if (response?.data?.id) {
                setUser(response.data)
            }
        } catch {
            setUser(null)
        } finally {
            setIsLoading(false)
        }
    }, [])

    useEffect(() => {
        fetchUser()
    }, [fetchUser])

    const login = async (credentials) => {
        const response = await loginRequest(credentials)
        if (response?.data) {
            setUser(response.data)
        }
        return response
    }

    const logout = async () => {
        setIsLoading(true)
        await logoutRequest()
        setUser(null)
        setIsLoading(false)
    }

    return (
        <AuthContext.Provider value={{ user, isLoading, isAuthenticated: !!user, login, logout, fetchUser }}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => {
    const context = useContext(AuthContext)
    if (!context) throw new Error('useAuth debe usarse dentro de AuthProvider')
    return context
}
