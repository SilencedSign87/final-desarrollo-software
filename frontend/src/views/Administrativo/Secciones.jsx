import { useEffect, useState } from 'react'
import { CalendarClock, Layers, Pencil, Plus, Trash2, Upload } from 'lucide-react'
import Dialog from '../../components/Dialog'
import Spinner from '../../components/spinner'
import { SeccionService } from '../../services/seccionService'
import { HorarioService } from '../../services/horarioService'
import { DocenteService } from '../../services/docenteService'
import { getCursos } from '../../services/cursos'
import { PeriodoAcademicoService } from '../../services/periodoAcademicoService'

const DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

export default function AdministrativoSecciones() {
    const [secciones, setSecciones] = useState([])
    const [cursos, setCursos] = useState([])
    const [docentes, setDocentes] = useState([])
    const [periodos, setPeriodos] = useState([])
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState(null)

    const [seccionDialogOpen, setSeccionDialogOpen] = useState(false)
    const [editingSeccion, setEditingSeccion] = useState(null)
    const [form, setForm] = useState({ curso_id: '', docente_id: '', periodo_academico_id: '', nombre: '', aforo: 30 })
    const [isSubmitting, setIsSubmitting] = useState(false)

    const [silaboDialogOpen, setSilaboDialogOpen] = useState(false)
    const [silaboSeccion, setSilaboSeccion] = useState(null)
    const [silaboUrl, setSilaboUrl] = useState('')

    const [horarioDialogOpen, setHorarioDialogOpen] = useState(false)
    const [horarioSeccion, setHorarioSeccion] = useState(null)
    const [horarios, setHorarios] = useState([])
    const [horarioForm, setHorarioForm] = useState({ dia_semana: 0, hora_inicio: '08:00', hora_final: '10:00', aula: '' })
    const [horarioError, setHorarioError] = useState(null)

    const reload = async () => {
        setIsLoading(true)
        try {
            const response = await SeccionService.Search()
            setSecciones(response.data ?? [])
            setError(null)
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudieron cargar las secciones')
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        let active = true

        SeccionService.Search()
            .then((response) => {
                if (active) setSecciones(response.data ?? [])
            })
            .catch((requestError) => {
                if (active) setError(requestError.response?.data?.error ?? 'No se pudieron cargar las secciones')
            })
            .finally(() => {
                if (active) setIsLoading(false)
            })

        getCursos().then((response) => active && setCursos(response.data ?? [])).catch(() => {})
        DocenteService.Search().then((response) => active && setDocentes(response.data ?? [])).catch(() => {})
        PeriodoAcademicoService.search().then((response) => active && setPeriodos(response.data ?? [])).catch(() => {})

        return () => {
            active = false
        }
    }, [])

    const openCreate = () => {
        setEditingSeccion(null)
        setForm({
            curso_id: cursos[0]?.id ?? '',
            docente_id: docentes[0]?.id ?? '',
            periodo_academico_id: periodos[0]?.id ?? '',
            nombre: '',
            aforo: 30,
        })
        setSeccionDialogOpen(true)
    }

    const openEdit = (seccion) => {
        setEditingSeccion(seccion)
        setForm({
            curso_id: seccion.curso_id,
            docente_id: seccion.docente_id,
            periodo_academico_id: seccion.periodo_academico_id,
            nombre: seccion.nombre,
            aforo: seccion.aforo,
        })
        setSeccionDialogOpen(true)
    }

    const handleSubmitSeccion = async (event) => {
        event.preventDefault()
        setIsSubmitting(true)
        setError(null)
        try {
            if (editingSeccion) {
                await SeccionService.Update(editingSeccion.id, {
                    docente_id: Number(form.docente_id),
                    aforo: Number(form.aforo),
                })
            } else {
                await SeccionService.Create({
                    curso_id: Number(form.curso_id),
                    docente_id: Number(form.docente_id),
                    periodo_academico_id: Number(form.periodo_academico_id),
                    nombre: form.nombre,
                    aforo: Number(form.aforo),
                })
            }
            setSeccionDialogOpen(false)
            await reload()
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudo guardar la sección')
        } finally {
            setIsSubmitting(false)
        }
    }

    const handleDeleteSeccion = async (seccionId) => {
        setError(null)
        try {
            await SeccionService.Delete(seccionId)
            await reload()
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudo eliminar la sección')
        }
    }

    const openSilabo = (seccion) => {
        setSilaboSeccion(seccion)
        setSilaboUrl(seccion.silabo_url ?? '')
        setSilaboDialogOpen(true)
    }

    const handleSubmitSilabo = async (event) => {
        event.preventDefault()
        setIsSubmitting(true)
        setError(null)
        try {
            await SeccionService.UploadSilabo(silaboSeccion.id, silaboUrl)
            setSilaboDialogOpen(false)
            await reload()
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudo subir el sílabo')
        } finally {
            setIsSubmitting(false)
        }
    }

    const openHorarios = async (seccion) => {
        setHorarioSeccion(seccion)
        setHorarioDialogOpen(true)
        setHorarioError(null)
        try {
            const response = await HorarioService.Search({ seccion_id: seccion.id })
            setHorarios(response.data ?? [])
        } catch {
            setHorarios([])
        }
    }

    const handleAddHorario = async (event) => {
        event.preventDefault()
        setHorarioError(null)
        try {
            await HorarioService.Create({
                seccion_id: horarioSeccion.id,
                dia_semana: Number(horarioForm.dia_semana),
                hora_inicio: `${horarioForm.hora_inicio}:00`,
                hora_final: `${horarioForm.hora_final}:00`,
                aula: horarioForm.aula,
            })
            const response = await HorarioService.Search({ seccion_id: horarioSeccion.id })
            setHorarios(response.data ?? [])
        } catch (requestError) {
            setHorarioError(requestError.response?.data?.error ?? 'No se pudo crear el horario (revisa cruces de aula/horario)')
        }
    }

    const handleDeleteHorario = async (horarioId) => {
        try {
            await HorarioService.Delete(horarioId)
            const response = await HorarioService.Search({ seccion_id: horarioSeccion.id })
            setHorarios(response.data ?? [])
        } catch (requestError) {
            setHorarioError(requestError.response?.data?.error ?? 'No se pudo eliminar el horario')
        }
    }

    return (
        <section className="space-y-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <h2 className="text-2xl font-semibold text-slate-900">Secciones</h2>
                    <p className="mt-1 text-sm text-neutral-600">
                        Asigna docentes a cursos y gestiona horarios por sección.
                    </p>
                </div>
                <button type="button" className="primary inline-flex items-center gap-2" onClick={openCreate}>
                    <Plus className="h-4 w-4" />
                    Nueva sección
                </button>
            </div>

            {error && (
                <p className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                </p>
            )}

            <div className="rounded-lg border border-neutral-300 bg-neutral-50 p-4">
                <div className="mb-4 flex items-center gap-2 text-sm text-neutral-600">
                    <Layers className="h-4 w-4" />
                    <span>Listado de secciones</span>
                </div>

                {isLoading ? (
                    <div className="flex justify-center py-10">
                        <Spinner />
                    </div>
                ) : !secciones.length ? (
                    <p className="rounded-lg border border-dashed border-neutral-300 px-4 py-8 text-center text-sm text-neutral-500">
                        No hay secciones registradas.
                    </p>
                ) : (
                    <div className="overflow-x-auto rounded-lg border border-neutral-300">
                        <table className="min-w-full divide-y divide-neutral-200 text-sm">
                            <thead className="bg-neutral-50">
                                <tr>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Sección</th>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Curso</th>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Docente</th>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Periodo</th>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Cupos</th>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Sílabo</th>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Acciones</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-neutral-200 bg-white">
                                {secciones.map((seccion) => (
                                    <tr key={seccion.id}>
                                        <td className="px-4 py-3 text-neutral-900">{seccion.nombre}</td>
                                        <td className="px-4 py-3 text-neutral-700">{seccion.curso_nombre ?? seccion.curso_id}</td>
                                        <td className="px-4 py-3 text-neutral-700">{seccion.docente_nombre ?? seccion.docente_id}</td>
                                        <td className="px-4 py-3 text-neutral-700">{seccion.periodo_semestre ?? seccion.periodo_academico_id}</td>
                                        <td className="px-4 py-3 text-neutral-700">{seccion.cupos_ocupados}/{seccion.aforo}</td>
                                        <td className="px-4 py-3">
                                            {seccion.silabo_url ? (
                                                <a href={seccion.silabo_url} target="_blank" rel="noreferrer" className="text-blue-700 hover:underline">
                                                    Ver sílabo
                                                </a>
                                            ) : (
                                                <span className="text-xs text-neutral-500">Sin sílabo</span>
                                            )}
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className="flex flex-wrap gap-2">
                                                <button type="button" className="subtle inline-flex items-center gap-1" onClick={() => openEdit(seccion)} title="Editar">
                                                    <Pencil className="h-4 w-4" />
                                                </button>
                                                <button type="button" className="subtle inline-flex items-center gap-1" onClick={() => openSilabo(seccion)} title="Subir sílabo">
                                                    <Upload className="h-4 w-4" />
                                                </button>
                                                <button type="button" className="subtle inline-flex items-center gap-1" onClick={() => openHorarios(seccion)} title="Horarios">
                                                    <CalendarClock className="h-4 w-4" />
                                                </button>
                                                <button type="button" className="subtle inline-flex items-center gap-1 text-red-700" onClick={() => handleDeleteSeccion(seccion.id)} title="Eliminar">
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

            <Dialog open={seccionDialogOpen} onOpenChange={setSeccionDialogOpen}>
                <Dialog.Surface>
                    <Dialog.Header>{editingSeccion ? 'Editar sección' : 'Nueva sección'}</Dialog.Header>
                    <Dialog.Content>
                        <form id="seccion-form" className="space-y-4" onSubmit={handleSubmitSeccion}>
                            {!editingSeccion && (
                                <>
                                    <label className="flex flex-col gap-2 text-sm">
                                        Curso
                                        <select value={form.curso_id} onChange={(event) => setForm((prev) => ({ ...prev, curso_id: event.target.value }))} required>
                                            {cursos.map((c) => (
                                                <option key={c.id} value={c.id}>{c.nombre}</option>
                                            ))}
                                        </select>
                                    </label>
                                    <label className="flex flex-col gap-2 text-sm">
                                        Periodo académico
                                        <select value={form.periodo_academico_id} onChange={(event) => setForm((prev) => ({ ...prev, periodo_academico_id: event.target.value }))} required>
                                            {periodos.map((p) => (
                                                <option key={p.id} value={p.id}>{p.semestre}</option>
                                            ))}
                                        </select>
                                    </label>
                                    <label className="flex flex-col gap-2 text-sm">
                                        Nombre de la sección
                                        <input type="text" placeholder="Ej: DAW-A" value={form.nombre} onChange={(event) => setForm((prev) => ({ ...prev, nombre: event.target.value }))} required />
                                    </label>
                                </>
                            )}
                            <label className="flex flex-col gap-2 text-sm">
                                Docente
                                <select value={form.docente_id} onChange={(event) => setForm((prev) => ({ ...prev, docente_id: event.target.value }))} required>
                                    {docentes.map((d) => (
                                        <option key={d.id} value={d.id}>{d.user_nombre ?? d.id}</option>
                                    ))}
                                </select>
                            </label>
                            <label className="flex flex-col gap-2 text-sm">
                                Aforo (cupos)
                                <input type="number" min="1" value={form.aforo} onChange={(event) => setForm((prev) => ({ ...prev, aforo: event.target.value }))} required />
                            </label>
                        </form>
                    </Dialog.Content>
                    <Dialog.Footer>
                        <button type="submit" form="seccion-form" className="primary" disabled={isSubmitting}>
                            {isSubmitting ? 'Guardando...' : 'Guardar'}
                        </button>
                        <Dialog.Trigger className="subtle">Cancelar</Dialog.Trigger>
                    </Dialog.Footer>
                </Dialog.Surface>
            </Dialog>

            <Dialog open={silaboDialogOpen} onOpenChange={setSilaboDialogOpen}>
                <Dialog.Surface>
                    <Dialog.Header>Subir sílabo — {silaboSeccion?.nombre}</Dialog.Header>
                    <Dialog.Content>
                        <form id="silabo-form" onSubmit={handleSubmitSilabo}>
                            <label className="flex flex-col gap-2 text-sm">
                                URL del sílabo
                                <input type="text" placeholder="https://..." value={silaboUrl} onChange={(event) => setSilaboUrl(event.target.value)} required />
                            </label>
                        </form>
                    </Dialog.Content>
                    <Dialog.Footer>
                        <button type="submit" form="silabo-form" className="primary" disabled={isSubmitting}>
                            {isSubmitting ? 'Guardando...' : 'Guardar'}
                        </button>
                        <Dialog.Trigger className="subtle">Cancelar</Dialog.Trigger>
                    </Dialog.Footer>
                </Dialog.Surface>
            </Dialog>

            <Dialog open={horarioDialogOpen} onOpenChange={setHorarioDialogOpen}>
                <Dialog.Surface className="w-lg">
                    <Dialog.Header>Horarios — {horarioSeccion?.nombre}</Dialog.Header>
                    <Dialog.Content>
                        <div className="space-y-4">
                            {horarioError && (
                                <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
                                    {horarioError}
                                </p>
                            )}

                            {horarios.length === 0 ? (
                                <p className="text-sm text-neutral-500">Sin horarios registrados.</p>
                            ) : (
                                <ul className="space-y-2">
                                    {horarios.map((h) => (
                                        <li key={h.id} className="flex items-center justify-between rounded-md border border-neutral-200 px-3 py-2 text-sm">
                                            <span>{DIAS[h.dia_semana]} · {h.hora_inicio.slice(0, 5)}–{h.hora_final.slice(0, 5)} · {h.aula}</span>
                                            <button type="button" className="text-red-700" onClick={() => handleDeleteHorario(h.id)}>
                                                <Trash2 className="h-4 w-4" />
                                            </button>
                                        </li>
                                    ))}
                                </ul>
                            )}

                            <form className="grid grid-cols-2 gap-3 border-t border-neutral-200 pt-4" onSubmit={handleAddHorario}>
                                <label className="col-span-2 flex flex-col gap-1 text-xs">
                                    Día
                                    <select value={horarioForm.dia_semana} onChange={(event) => setHorarioForm((prev) => ({ ...prev, dia_semana: event.target.value }))}>
                                        {DIAS.map((dia, index) => (
                                            <option key={dia} value={index}>{dia}</option>
                                        ))}
                                    </select>
                                </label>
                                <label className="flex flex-col gap-1 text-xs">
                                    Inicio
                                    <input type="time" value={horarioForm.hora_inicio} onChange={(event) => setHorarioForm((prev) => ({ ...prev, hora_inicio: event.target.value }))} required />
                                </label>
                                <label className="flex flex-col gap-1 text-xs">
                                    Fin
                                    <input type="time" value={horarioForm.hora_final} onChange={(event) => setHorarioForm((prev) => ({ ...prev, hora_final: event.target.value }))} required />
                                </label>
                                <label className="col-span-2 flex flex-col gap-1 text-xs">
                                    Aula
                                    <input type="text" placeholder="Ej: Lab-201" value={horarioForm.aula} onChange={(event) => setHorarioForm((prev) => ({ ...prev, aula: event.target.value }))} required />
                                </label>
                                <button type="submit" className="primary col-span-2">Agregar horario</button>
                            </form>
                        </div>
                    </Dialog.Content>
                    <Dialog.Footer>
                        <Dialog.Trigger className="subtle">Cerrar</Dialog.Trigger>
                    </Dialog.Footer>
                </Dialog.Surface>
            </Dialog>
        </section>
    )
}