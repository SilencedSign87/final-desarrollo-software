import { useCallback, useEffect, useState } from 'react'
import { Shield } from 'lucide-react'
import Spinner from '../../components/Spinner'
import { getUsers, updateUserRole } from '../../services/securityService'

const ROLES = [
    { value: 'estudiante', label: 'Estudiante' },
    { value: 'docente', label: 'Docente' },
    { value: 'administrador', label: 'Administrador' },
    { value: 'direccion', label: 'Dirección' },
]

export default function AdministrativoSeguridad() {
    const [users, setUsers] = useState([])
    const [isLoading, setIsLoading] = useState(true)
    const [updatingUserId, setUpdatingUserId] = useState(null)
    const [error, setError] = useState(null)

    const loadUsers = useCallback(async ({ showLoading = false } = {}) => {
        if (showLoading) {
            setIsLoading(true)
        }
        setError(null)
        try {
            const response = await getUsers()
            setUsers(response.data.data ?? [])
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudieron cargar los usuarios')
        } finally {
            if (showLoading) {
                setIsLoading(false)
            }
        }
    }, [])

    useEffect(() => {
        let active = true

        getUsers()
            .then((response) => {
                if (active) {
                    setUsers(response.data.data ?? [])
                }
            })
            .catch((requestError) => {
                if (active) {
                    setError(requestError.response?.data?.error ?? 'No se pudieron cargar los usuarios')
                }
            })
            .finally(() => {
                if (active) {
                    setIsLoading(false)
                }
            })

        return () => {
            active = false
        }
    }, [])

    const handleRoleChange = async (userId, rol) => {
        setUpdatingUserId(userId)
        setError(null)

        try {
            await updateUserRole(userId, { rol })
            await loadUsers({ showLoading: true })
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudo actualizar el rol')
        } finally {
            setUpdatingUserId(null)
        }
    }

    return (
        <section className="space-y-6">
            <div>
                <h2 className="text-2xl font-semibold text-slate-900">Administración y seguridad</h2>
                <p className="mt-1 text-sm text-neutral-600">
                    Define perfiles de acceso y gestiona roles del sistema.
                </p>
            </div>

            {error && (
                <p className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                </p>
            )}

            {isLoading ? (
                <div className="flex justify-center py-10">
                    <Spinner />
                </div>
            ) : (
                <div className="overflow-x-auto rounded-lg border border-neutral-300">
                    <table className="min-w-full divide-y divide-neutral-200 text-sm">
                        <thead className="bg-neutral-50">
                            <tr>
                                <th className="px-4 py-3 text-left font-medium text-neutral-600">Usuario</th>
                                <th className="px-4 py-3 text-left font-medium text-neutral-600">Correo</th>
                                <th className="px-4 py-3 text-left font-medium text-neutral-600">Rol actual</th>
                                <th className="px-4 py-3 text-left font-medium text-neutral-600">Asignar rol</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-neutral-200 bg-white">
                            {users.map((user) => (
                                <tr key={user.id}>
                                    <td className="px-4 py-3 text-neutral-900">
                                        {user.nombres} {user.apellidos}
                                    </td>
                                    <td className="px-4 py-3 text-neutral-600">{user.email}</td>
                                    <td className="px-4 py-3">
                                        <span className="inline-flex items-center gap-2 rounded-full bg-neutral-100 px-2.5 py-1 text-xs font-medium text-neutral-700">
                                            <Shield className="h-3.5 w-3.5" />
                                            {user.rol}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3">
                                        <select
                                            value={user.rol}
                                            disabled={updatingUserId === user.id}
                                            onChange={(event) => handleRoleChange(user.id, event.target.value)}
                                        >
                                            {ROLES.map((role) => (
                                                <option key={role.value} value={role.value}>
                                                    {role.label}
                                                </option>
                                            ))}
                                        </select>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </section>
    )
}
