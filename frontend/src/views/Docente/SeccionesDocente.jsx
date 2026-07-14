import { useEffect, useState } from 'react'
import { CalendarClock, Layers, Upload } from 'lucide-react'
import Dialog from '../../components/Dialog'
import Spinner from '../../components/Spinner'
import { DocenteService } from '../../services/docenteService'
import { SeccionService } from '../../services/seccionService'
import { HorarioService } from '../../services/horarioService'
import { PeriodoAcademicoService } from '../../services/periodoAcademicoService'

const DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

export default function SeccionesDocente() {
    const [secciones, setSecciones] = useState([])
    const [periodos, setPeriodos] = useState([])
    const [periodoId, setPeriodoId] = useState('')
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState(null)

    const [silaboDialogOpen, setSilaboDialogOpen] = useState(false)
    const [silaboSeccion, setSilaboSeccion] = useState(null)
    const [silaboFile, setSilaboFile] = useState(null)
    const [isSubmitting, setIsSubmitting] = useState(false)

    const [horarioDialogOpen, setHorarioDialogOpen] = useState(false)
    const [horarioSeccion, setHorarioSeccion] = useState(null)
    const [horarios, setHorarios] = useState([])

    const reload = async () => {
        setIsLoading(true)
        try {
            const me = await DocenteService.Me()
            const response = await DocenteService.Secciones(me.data.id)
            setSecciones(response.data ?? [])
            setError(null)
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudieron cargar tus secciones')
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        let active = true

        Promise.all([
            DocenteService.Me().then((response) => DocenteService.Secciones(response.data.id)),
            PeriodoAcademicoService.search(),
        ])
            .then(([seccionesRes, periodosRes]) => {
                if (!active) return
                setSecciones(seccionesRes.data ?? [])
                setPeriodos(periodosRes.data ?? [])
            })
            .catch((requestError) => {
                if (active) setError(requestError.response?.data?.error ?? 'No se pudieron cargar tus secciones')
            })
            .finally(() => {
                if (active) setIsLoading(false)
            })

        return () => {
            active = false
        }
    }, [])

    const seccionesFiltradas = periodoId
        ? secciones.filter((s) => String(s.periodo_academico_id) === String(periodoId))
        : secciones

    const openSilabo = (seccion) => {
        setSilaboSeccion(seccion)
        setSilaboFile(null)
        setError(null)
        setSilaboDialogOpen(true)
    }

    const handleSubmitSilabo = async (event) => {
        event.preventDefault()
        if (!silaboFile) {
            setError('Debes seleccionar un archivo PDF')
            return
        }
        setIsSubmitting(true)
        setError(null)
        try {
            await SeccionService.UploadSilabo(silaboSeccion.id, silaboFile)
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
        try {
            const response = await HorarioService.Search({ seccion_id: seccion.id })
            setHorarios(response.data ?? [])
        } catch {
            setHorarios([])
        }
    }

    return (
        <section className="space-y-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
                <div>
                    <h2 className="text-2xl font-semibold text-slate-900">Mis secciones</h2>
                    <p className="mt-1 text-sm text-neutral-600">
                        Sube el sílabo de tus cursos y consulta tus horarios asignados.
                    </p>
                </div>
                <label className="flex flex-col gap-1 text-sm">
                    Periodo académico
                    <select value={periodoId} onChange={(e) => setPeriodoId(e.target.value)}>
                        <option value="">Todos</option>
                        {periodos.map((p) => (
                            <option key={p.id} value={p.id}>{p.semestre}</option>
                        ))}
                    </select>
                </label>
            </div>

            {error && (
                <p className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                </p>
            )}

            <div className="rounded-lg border border-neutral-300 bg-neutral-50 p-4">
                <div className="mb-4 flex items-center gap-2 text-sm text-neutral-600">
                    <Layers className="h-4 w-4" />
                    <span>Secciones asignadas</span>
                </div>

                {isLoading ? (
                    <div className="flex justify-center py-10">
                        <Spinner />
                    </div>
                ) : !seccionesFiltradas.length ? (
                    <p className="rounded-lg border border-dashed border-neutral-300 px-4 py-8 text-center text-sm text-neutral-500">
                        No tienes secciones asignadas {periodoId ? 'en este periodo' : ''}.
                    </p>
                ) : (
                    <div className="overflow-x-auto rounded-lg border border-neutral-300">
                        <table className="min-w-full divide-y divide-neutral-200 text-sm">
                            <thead className="bg-neutral-50">
                                <tr>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Curso</th>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Sección</th>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Periodo</th>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Sílabo</th>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Acciones</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-neutral-200 bg-white">
                                {seccionesFiltradas.map((seccion) => (
                                    <tr key={seccion.id}>
                                        <td className="px-4 py-3 text-neutral-900">{seccion.curso_nombre}</td>
                                        <td className="px-4 py-3 text-neutral-700">{seccion.nombre}</td>
                                        <td className="px-4 py-3 text-neutral-700">{seccion.periodo_semestre}</td>
                                        <td className="px-4 py-3">
                                            {seccion.silabo_url ? (
                                                <button
                                                    type="button"
                                                    onClick={() => SeccionService.VerSilabo(seccion.id)}
                                                    className="text-blue-700 hover:underline"
                                                >
                                                    Ver sílabo
                                                </button>
                                            ) : (
                                                <span className="text-xs text-neutral-500">Sin sílabo</span>
                                            )}
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className="flex gap-2">
                                                <button type="button" className="subtle inline-flex items-center gap-1" onClick={() => openSilabo(seccion)}>
                                                    <Upload className="h-4 w-4" />
                                                    Sílabo
                                                </button>
                                                <button type="button" className="subtle inline-flex items-center gap-1" onClick={() => openHorarios(seccion)}>
                                                    <CalendarClock className="h-4 w-4" />
                                                    Horario
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

            <Dialog open={silaboDialogOpen} onOpenChange={setSilaboDialogOpen}>
                <Dialog.Surface>
                    <Dialog.Header>Subir sílabo — {silaboSeccion?.nombre}</Dialog.Header>
                    <Dialog.Content>
                        {error && (
                            <p className="mb-2 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
                                {error}
                            </p>
                        )}
                        <form id="silabo-docente-form" onSubmit={handleSubmitSilabo}>
                            <label className="flex flex-col gap-2 text-sm">
                                Archivo PDF del sílabo
                                <input
                                    type="file"
                                    accept="application/pdf"
                                    onChange={(event) => setSilaboFile(event.target.files?.[0] ?? null)}
                                    required
                                />
                            </label>
                            {silaboSeccion?.silabo_url && (
                                <p className="mt-2 text-xs text-neutral-500">
                                    Ya existe un sílabo subido —{' '}
                                    <button
                                        type="button"
                                        onClick={() => SeccionService.VerSilabo(silaboSeccion.id)}
                                        className="text-blue-700 hover:underline"
                                    >
                                        verlo aquí
                                    </button>. Subir un nuevo archivo lo reemplaza.
                                </p>
                            )}
                        </form>
                    </Dialog.Content>
                    <Dialog.Footer>
                        <button type="submit" form="silabo-docente-form" className="primary" disabled={isSubmitting}>
                            {isSubmitting ? 'Guardando...' : 'Guardar'}
                        </button>
                        <Dialog.Trigger className="subtle">Cancelar</Dialog.Trigger>
                    </Dialog.Footer>
                </Dialog.Surface>
            </Dialog>

            <Dialog open={horarioDialogOpen} onOpenChange={setHorarioDialogOpen}>
                <Dialog.Surface>
                    <Dialog.Header>Horario — {horarioSeccion?.nombre}</Dialog.Header>
                    <Dialog.Content>
                        {horarios.length === 0 ? (
                            <p className="text-sm text-neutral-500">Sin horarios registrados aún.</p>
                        ) : (
                            <ul className="space-y-2">
                                {horarios.map((h) => (
                                    <li key={h.id} className="rounded-md border border-neutral-200 px-3 py-2 text-sm">
                                        {DIAS[h.dia_semana]} · {h.hora_inicio.slice(0, 5)}–{h.hora_final.slice(0, 5)} · {h.aula}
                                    </li>
                                ))}
                            </ul>
                        )}
                    </Dialog.Content>
                    <Dialog.Footer>
                        <Dialog.Trigger className="subtle">Cerrar</Dialog.Trigger>
                    </Dialog.Footer>
                </Dialog.Surface>
            </Dialog>
        </section>
    )
}