import { useCallback, useEffect, useState } from 'react'
import { Plus, Shield } from 'lucide-react'
import Dialog from '../../components/Dialog'
import Spinner from '../../components/Spinner'
import { getPlanesEstudio } from '../../services/cursos'
import { createUser, getUsers, updateUserRole } from '../../services/securityService'

const ROLES = [
    { value: 'estudiante', label: 'Estudiante' },
    { value: 'docente', label: 'Docente' },
    { value: 'administrador', label: 'Administrador' },
    { value: 'direccion', label: 'Dirección' },
]

const EMPTY_FORM = {
    nombres: '',
    apellidos: '',
    email: '',
    dni: '',
    password: '',
    rol: 'estudiante',
    plan_estudios_id: '',
    categoria: 'auxiliar',
}

export default function AdministrativoSeguridad() {
    const [users, setUsers] = useState([])
    const [planes, setPlanes] = useState([])
    const [isLoading, setIsLoading] = useState(true)
    const [updatingUserId, setUpdatingUserId] = useState(null)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [dialogOpen, setDialogOpen] = useState(false)
    const [form, setForm] = useState(EMPTY_FORM)
    const [error, setError] = useState(null)
    const [success, setSuccess] = useState(null)

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

        Promise.all([getUsers(), getPlanesEstudio()])
            .then(([usersResponse, planesResponse]) => {
                if (!active) return
                setUsers(usersResponse.data.data ?? [])
                setPlanes(planesResponse.data ?? [])
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
        setSuccess(null)

        try {
            await updateUserRole(userId, { rol })
            await loadUsers({ showLoading: true })
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudo actualizar el rol')
        } finally {
            setUpdatingUserId(null)
        }
    }

    const openCreate = () => {
        setForm({
            ...EMPTY_FORM,
            plan_estudios_id: planes[0]?.id ? String(planes[0].id) : '',
        })
        setError(null)
        setSuccess(null)
        setDialogOpen(true)
    }

    const updateField = (field, value) => {
        setForm((current) => ({ ...current, [field]: value }))
    }

    const handleCreateUser = async (event) => {
        event.preventDefault()
        setIsSubmitting(true)
        setError(null)
        setSuccess(null)

        if (!/^\d{8}$/.test(form.dni.trim())) {
            setError('El DNI debe tener exactamente 8 dígitos numéricos')
            setIsSubmitting(false)
            return
        }

        if (form.password.length < 6) {
            setError('La contraseña debe tener al menos 6 caracteres')
            setIsSubmitting(false)
            return
        }

        const payload = {
            nombres: form.nombres.trim(),
            apellidos: form.apellidos.trim(),
            email: form.email.trim(),
            dni: form.dni.trim(),
            password: form.password,
            rol: form.rol,
        }

        if (form.rol === 'estudiante') {
            payload.plan_estudios_id = Number(form.plan_estudios_id)
        }
        if (form.rol === 'docente') {
            payload.categoria = form.categoria
        }

        try {
            await createUser(payload)
            setDialogOpen(false)
            setSuccess('Usuario creado correctamente')
            await loadUsers({ showLoading: true })
        } catch (requestError) {
            const apiError = requestError.response?.data?.error
            const validation = requestError.response?.data?.message
            setError(apiError || validation || 'No se pudo crear el usuario')
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <section className="space-y-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <h2 className="text-2xl font-semibold text-slate-900">Administración y seguridad</h2>
                    <p className="mt-1 text-sm text-neutral-600">
                        Crea usuarios, define perfiles de acceso y gestiona roles del sistema.
                    </p>
                </div>
                <button type="button" className="primary inline-flex items-center gap-2" onClick={openCreate}>
                    <Plus className="h-4 w-4" />
                    Crear usuario
                </button>
            </div>

            {error && (
                <p className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                </p>
            )}
            {success && (
                <p className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
                    {success}
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

            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <Dialog.Surface>
                    <Dialog.Header>Crear usuario</Dialog.Header>
                    <Dialog.Content>
                        <form id="create-user-form" className="grid min-w-[320px] gap-3 sm:min-w-[420px]" onSubmit={handleCreateUser}>
                            <div className="grid gap-3 sm:grid-cols-2">
                                <label className="flex flex-col gap-1 text-sm">
                                    Nombres
                                    <input
                                        type="text"
                                        required
                                        value={form.nombres}
                                        onChange={(event) => updateField('nombres', event.target.value)}
                                    />
                                </label>
                                <label className="flex flex-col gap-1 text-sm">
                                    Apellidos
                                    <input
                                        type="text"
                                        required
                                        value={form.apellidos}
                                        onChange={(event) => updateField('apellidos', event.target.value)}
                                    />
                                </label>
                            </div>
                            <label className="flex flex-col gap-1 text-sm">
                                Correo
                                <input
                                    type="email"
                                    required
                                    value={form.email}
                                    onChange={(event) => updateField('email', event.target.value)}
                                />
                            </label>
                            <label className="flex flex-col gap-1 text-sm">
                                DNI
                                <input
                                    type="text"
                                    inputMode="numeric"
                                    pattern="\d{8}"
                                    maxLength={8}
                                    required
                                    title="Exactamente 8 dígitos"
                                    value={form.dni}
                                    onChange={(event) => {
                                        const onlyDigits = event.target.value.replace(/\D/g, '').slice(0, 8)
                                        updateField('dni', onlyDigits)
                                    }}
                                />
                            </label>
                            <label className="flex flex-col gap-1 text-sm">
                                Contraseña
                                <input
                                    type="password"
                                    required
                                    minLength={6}
                                    value={form.password}
                                    onChange={(event) => updateField('password', event.target.value)}
                                />
                            </label>
                            <label className="flex flex-col gap-1 text-sm">
                                Rol
                                <select
                                    value={form.rol}
                                    onChange={(event) => updateField('rol', event.target.value)}
                                >
                                    {ROLES.map((role) => (
                                        <option key={role.value} value={role.value}>
                                            {role.label}
                                        </option>
                                    ))}
                                </select>
                            </label>
                            {form.rol === 'estudiante' && (
                                <label className="flex flex-col gap-1 text-sm">
                                    Plan de estudios
                                    <select
                                        required
                                        value={form.plan_estudios_id}
                                        onChange={(event) => updateField('plan_estudios_id', event.target.value)}
                                    >
                                        {planes.length === 0 && (
                                            <option value="">No hay planes disponibles</option>
                                        )}
                                        {planes.map((plan) => (
                                            <option key={plan.id} value={plan.id}>
                                                {plan.especialidad_nombre} — {plan.version} ({plan.anio})
                                            </option>
                                        ))}
                                    </select>
                                </label>
                            )}
                            {form.rol === 'docente' && (
                                <label className="flex flex-col gap-1 text-sm">
                                    Categoría
                                    <select
                                        value={form.categoria}
                                        onChange={(event) => updateField('categoria', event.target.value)}
                                    >
                                        <option value="auxiliar">Auxiliar</option>
                                        <option value="asociado">Asociado</option>
                                        <option value="principal">Principal</option>
                                    </select>
                                </label>
                            )}
                        </form>
                    </Dialog.Content>
                    <Dialog.Footer>
                        <button
                            type="submit"
                            form="create-user-form"
                            className="primary"
                            disabled={isSubmitting || (form.rol === 'estudiante' && !planes.length)}
                        >
                            {isSubmitting ? 'Creando...' : 'Crear usuario'}
                        </button>
                        <Dialog.Trigger className="subtle">Cancelar</Dialog.Trigger>
                    </Dialog.Footer>
                </Dialog.Surface>
            </Dialog>
        </section>
    )
}
