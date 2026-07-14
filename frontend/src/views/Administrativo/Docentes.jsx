import { useEffect, useState } from 'react'
import { GraduationCap, Plus } from 'lucide-react'
import Dialog from '../../components/Dialog'
import Spinner from '../../components/Spinner'
import { DocenteService } from '../../services/docenteService'
import { getUsers } from '../../services/securityService'

export default function AdministrativoDocentes() {
    const [docentes, setDocentes] = useState([])
    const [usuariosDocente, setUsuariosDocente] = useState([])
    const [userId, setUserId] = useState('')
    const [categoria, setCategoria] = useState('auxiliar')
    const [isLoading, setIsLoading] = useState(true)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [error, setError] = useState(null)
    const [dialogOpen, setDialogOpen] = useState(false)

    useEffect(() => {
        let active = true

        DocenteService.Search()
            .then((response) => {
                if (active) {
                    setDocentes(response.data ?? [])
                }
            })
            .catch((requestError) => {
                if (active) {
                    setError(requestError.response?.data?.error ?? 'No se pudieron cargar los docentes')
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

    const reload = async () => {
        setIsLoading(true)
        try {
            const response = await DocenteService.Search()
            setDocentes(response.data ?? [])
            setError(null)
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudieron cargar los docentes')
        } finally {
            setIsLoading(false)
        }
    }

    const openCreate = async () => {
        setDialogOpen(true)
        setCategoria('auxiliar')
        try {
            const response = await getUsers()
            const soloDocentes = (response.data?.data ?? []).filter((u) => u.rol === 'docente')
            setUsuariosDocente(soloDocentes)
            setUserId(soloDocentes[0]?.id ?? '')
        } catch {
            setUsuariosDocente([])
        }
    }

    const handleSubmit = async (event) => {
        event.preventDefault()
        setIsSubmitting(true)
        setError(null)

        try {
            await DocenteService.Create({ user_id: Number(userId), categoria })
            setDialogOpen(false)
            await reload()
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudo crear el perfil de docente')
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <section className="space-y-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <h2 className="text-2xl font-semibold text-slate-900">Docentes</h2>
                    <p className="mt-1 text-sm text-neutral-600">
                        Crea el perfil de docente para usuarios ya registrados con rol "docente".
                    </p>
                </div>
                <button type="button" className="primary inline-flex items-center gap-2" onClick={openCreate}>
                    <Plus className="h-4 w-4" />
                    Nuevo perfil de docente
                </button>
            </div>

            {error && (
                <p className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                </p>
            )}

            <div className="rounded-lg border border-neutral-300 bg-neutral-50 p-4">
                <div className="mb-4 flex items-center gap-2 text-sm text-neutral-600">
                    <GraduationCap className="h-4 w-4" />
                    <span>Listado de docentes</span>
                </div>

                {isLoading ? (
                    <div className="flex justify-center py-10">
                        <Spinner />
                    </div>
                ) : !docentes.length ? (
                    <p className="rounded-lg border border-dashed border-neutral-300 px-4 py-8 text-center text-sm text-neutral-500">
                        No hay docentes registrados.
                    </p>
                ) : (
                    <div className="overflow-x-auto rounded-lg border border-neutral-300">
                        <table className="min-w-full divide-y divide-neutral-200 text-sm">
                            <thead className="bg-neutral-50">
                                <tr>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">ID</th>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Nombre</th>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Categoría</th>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Secciones asignadas</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-neutral-200 bg-white">
                                {docentes.map((docente) => (
                                    <tr key={docente.id}>
                                        <td className="px-4 py-3 text-neutral-900">{docente.id}</td>
                                        <td className="px-4 py-3 text-neutral-900">{docente.user_nombre ?? docente.user_id}</td>
                                        <td className="px-4 py-3 text-neutral-700 capitalize">{docente.categoria}</td>
                                        <td className="px-4 py-3 text-neutral-700">{docente.total_secciones}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <Dialog.Surface>
                    <Dialog.Header>Nuevo perfil de docente</Dialog.Header>
                    <Dialog.Content>
                        {usuariosDocente.length === 0 ? (
                            <p className="text-sm text-neutral-500">
                                No hay usuarios con rol "docente" sin perfil aún. Regístralos primero desde Seguridad.
                            </p>
                        ) : (
                            <form id="docente-form" className="space-y-4" onSubmit={handleSubmit}>
                                <label className="flex flex-col gap-2 text-sm">
                                    Usuario
                                    <select value={userId} onChange={(event) => setUserId(event.target.value)} required>
                                        {usuariosDocente.map((u) => (
                                            <option key={u.id} value={u.id}>
                                                {u.nombres} {u.apellidos} ({u.email})
                                            </option>
                                        ))}
                                    </select>
                                </label>
                                <label className="flex flex-col gap-2 text-sm">
                                    Categoría
                                    <select value={categoria} onChange={(event) => setCategoria(event.target.value)}>
                                        <option value="auxiliar">Auxiliar</option>
                                        <option value="asociado">Asociado</option>
                                        <option value="principal">Principal</option>
                                    </select>
                                </label>
                            </form>
                        )}
                    </Dialog.Content>
                    <Dialog.Footer>
                        {usuariosDocente.length > 0 && (
                            <button type="submit" form="docente-form" className="primary" disabled={isSubmitting}>
                                {isSubmitting ? 'Guardando...' : 'Guardar'}
                            </button>
                        )}
                        <Dialog.Trigger className="subtle">Cerrar</Dialog.Trigger>
                    </Dialog.Footer>
                </Dialog.Surface>
            </Dialog>
        </section>
    )
}