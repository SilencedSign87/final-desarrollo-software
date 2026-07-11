import { useEffect, useState } from 'react'
import { BookOpen, Pencil, Plus, Trash2 } from 'lucide-react'
import Dialog from '../../components/Dialog'
import Spinner from '../../components/spinner'
import { getCursos, createCurso, updateCurso, deleteCurso } from '../../services/cursos'

const EMPTY_FORM = {
    plan_estudios_id: 1,
    nombre: '',
    horas_teoria: 2,
    horas_practica: 2,
    semestre_num: 1,
}

export default function AdministrativoCursos() {
    const [cursos, setCursos] = useState([])
    const [form, setForm] = useState(EMPTY_FORM)
    const [editingId, setEditingId] = useState(null)
    const [isLoading, setIsLoading] = useState(true)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [error, setError] = useState(null)
    const [dialogOpen, setDialogOpen] = useState(false)

    useEffect(() => {
        let active = true

        getCursos()
            .then((response) => {
                if (active) {
                    setCursos(response.data ?? [])
                }
            })
            .catch((requestError) => {
                if (active) {
                    setError(requestError.response?.data?.error ?? 'No se pudieron cargar los cursos')
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
            const response = await getCursos()
            setCursos(response.data ?? [])
            setError(null)
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudieron cargar los cursos')
        } finally {
            setIsLoading(false)
        }
    }

    const openCreate = () => {
        setEditingId(null)
        setForm(EMPTY_FORM)
        setDialogOpen(true)
    }

    const openEdit = (curso) => {
        setEditingId(curso.id)
        setForm({
            plan_estudios_id: curso.plan_estudios_id,
            nombre: curso.nombre,
            horas_teoria: curso.horas_teoria,
            horas_practica: curso.horas_practica,
            semestre_num: curso.semestre_num,
        })
        setDialogOpen(true)
    }

    const handleSubmit = async (event) => {
        event.preventDefault()
        setIsSubmitting(true)
        setError(null)

        try {
            if (editingId) {
                await updateCurso(editingId, {
                    nombre: form.nombre,
                    horas_teoria: Number(form.horas_teoria),
                    horas_practica: Number(form.horas_practica),
                    semestre_num: Number(form.semestre_num),
                })
            } else {
                await createCurso({
                    ...form,
                    horas_teoria: Number(form.horas_teoria),
                    horas_practica: Number(form.horas_practica),
                    semestre_num: Number(form.semestre_num),
                    plan_estudios_id: Number(form.plan_estudios_id),
                })
            }
            setDialogOpen(false)
            await reload()
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudo guardar el curso')
        } finally {
            setIsSubmitting(false)
        }
    }

    const handleDelete = async (cursoId) => {
        setError(null)
        try {
            await deleteCurso(cursoId)
            await reload()
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudo eliminar el curso')
        }
    }

    return (
        <section className="space-y-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <h2 className="text-2xl font-semibold text-slate-900">Cursos</h2>
                    <p className="mt-1 text-sm text-neutral-600">
                        Administra los cursos del plan de estudios.
                    </p>
                </div>
                <button type="button" className="primary inline-flex items-center gap-2" onClick={openCreate}>
                    <Plus className="h-4 w-4" />
                    Nuevo curso
                </button>
            </div>

            {error && (
                <p className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                </p>
            )}

            <div className="rounded-lg border border-neutral-300 bg-neutral-50 p-4">
                <div className="mb-4 flex items-center gap-2 text-sm text-neutral-600">
                    <BookOpen className="h-4 w-4" />
                    <span>Listado de cursos</span>
                </div>

                {isLoading ? (
                    <div className="flex justify-center py-10">
                        <Spinner />
                    </div>
                ) : !cursos.length ? (
                    <p className="rounded-lg border border-dashed border-neutral-300 px-4 py-8 text-center text-sm text-neutral-500">
                        No hay cursos registrados.
                    </p>
                ) : (
                    <div className="overflow-x-auto rounded-lg border border-neutral-300">
                        <table className="min-w-full divide-y divide-neutral-200 text-sm">
                            <thead className="bg-neutral-50">
                                <tr>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">ID</th>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Nombre</th>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Semestre</th>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">H. Teoría</th>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">H. Práctica</th>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Acciones</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-neutral-200 bg-white">
                                {cursos.map((curso) => (
                                    <tr key={curso.id}>
                                        <td className="px-4 py-3 text-neutral-900">{curso.id}</td>
                                        <td className="px-4 py-3 text-neutral-900">{curso.nombre}</td>
                                        <td className="px-4 py-3 text-neutral-700">{curso.semestre_num}</td>
                                        <td className="px-4 py-3 text-neutral-700">{curso.horas_teoria}</td>
                                        <td className="px-4 py-3 text-neutral-700">{curso.horas_practica}</td>
                                        <td className="px-4 py-3">
                                            <div className="flex gap-2">
                                                <button type="button" className="subtle inline-flex items-center gap-1" onClick={() => openEdit(curso)}>
                                                    <Pencil className="h-4 w-4" />
                                                </button>
                                                <button type="button" className="subtle inline-flex items-center gap-1 text-red-700" onClick={() => handleDelete(curso.id)}>
                                                    <Trash2 className="h-4 w-4" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <Dialog.Surface>
                    <Dialog.Header>{editingId ? 'Editar curso' : 'Nuevo curso'}</Dialog.Header>
                    <Dialog.Content>
                        <form id="curso-form" className="space-y-4" onSubmit={handleSubmit}>
                            <label className="flex flex-col gap-2 text-sm">
                                Nombre del curso
                                <input
                                    type="text"
                                    value={form.nombre}
                                    onChange={(event) => setForm((prev) => ({ ...prev, nombre: event.target.value }))}
                                    required
                                />
                            </label>

                            {!editingId && (
                                <label className="flex flex-col gap-2 text-sm">
                                    ID del plan de estudios
                                    <input
                                        type="number"
                                        min="1"
                                        value={form.plan_estudios_id}
                                        onChange={(event) => setForm((prev) => ({ ...prev, plan_estudios_id: event.target.value }))}
                                        required
                                    />
                                </label>
                            )}

                            <label className="flex flex-col gap-2 text-sm">
                                Semestre (1-12)
                                <input
                                    type="number"
                                    min="1"
                                    max="12"
                                    value={form.semestre_num}
                                    onChange={(event) => setForm((prev) => ({ ...prev, semestre_num: event.target.value }))}
                                    required
                                />
                            </label>

                            <div className="grid grid-cols-2 gap-3">
                                <label className="flex flex-col gap-2 text-sm">
                                    Horas teoría
                                    <input
                                        type="number"
                                        min="0"
                                        value={form.horas_teoria}
                                        onChange={(event) => setForm((prev) => ({ ...prev, horas_teoria: event.target.value }))}
                                        required
                                    />
                                </label>
                                <label className="flex flex-col gap-2 text-sm">
                                    Horas práctica
                                    <input
                                        type="number"
                                        min="0"
                                        value={form.horas_practica}
                                        onChange={(event) => setForm((prev) => ({ ...prev, horas_practica: event.target.value }))}
                                        required
                                    />
                                </label>
                            </div>
                        </form>
                    </Dialog.Content>
                    <Dialog.Footer>
                        <button type="submit" form="curso-form" className="primary" disabled={isSubmitting}>
                            {isSubmitting ? 'Guardando...' : 'Guardar'}
                        </button>
                        <Dialog.Trigger className="subtle">Cancelar</Dialog.Trigger>
                    </Dialog.Footer>
                </Dialog.Surface>
            </Dialog>
        </section>
    )
}