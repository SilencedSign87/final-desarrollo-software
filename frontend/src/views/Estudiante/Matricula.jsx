import { useCallback, useEffect, useState } from 'react'
import { ClipboardList, Plus } from 'lucide-react'
import MatriculasTable from '../../components/matricula/MatriculasTable'
import Dialog from '../../components/Dialog'
import Spinner from '../../components/spinner'
import { createMatricula, getMisMatriculas } from '../../services/matriculaService'
import { PeriodoAcademicoService } from '../../services/periodoAcademicoService'
import { SeccionService } from '../../services/seccionService'

export default function EstudianteMatricula() {
    const [matriculas, setMatriculas] = useState([])
    const [periodos, setPeriodos] = useState([])
    const [secciones, setSecciones] = useState([])
    const [periodoId, setPeriodoId] = useState('')
    const [comprobanteUrl, setComprobanteUrl] = useState('')
    const [seccionesSeleccionadas, setSeccionesSeleccionadas] = useState([])
    const [isLoading, setIsLoading] = useState(true)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [error, setError] = useState(null)
    const [dialogOpen, setDialogOpen] = useState(false)

    const loadMatriculas = useCallback(async ({ showLoading = false } = {}) => {
        if (showLoading) {
            setIsLoading(true)
        }
        setError(null)
        try {
            const response = await getMisMatriculas()
            setMatriculas(response.data ?? [])
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudieron cargar tus matrículas')
        } finally {
            if (showLoading) {
                setIsLoading(false)
            }
        }
    }, [])

    useEffect(() => {
        let active = true

        getMisMatriculas()
            .then((response) => {
                if (active) {
                    setMatriculas(response.data ?? [])
                }
            })
            .catch((requestError) => {
                if (active) {
                    setError(requestError.response?.data?.error ?? 'No se pudieron cargar tus matrículas')
                }
            })
            .finally(() => {
                if (active) {
                    setIsLoading(false)
                }
            })

        PeriodoAcademicoService.search({ estado: 'activo' })
            .then((response) => {
                if (active) {
                    setPeriodos(response.data ?? [])
                }
            })
            .catch(() => {
                if (active) {
                    setPeriodos([])
                }
            })

        return () => {
            active = false
        }
    }, [])

    const handleOpenDialog = async () => {
        setDialogOpen(true)
        setSeccionesSeleccionadas([])
        setComprobanteUrl('')

        if (periodos[0]) {
            const primerPeriodo = periodos[0].id
            setPeriodoId(primerPeriodo)
            await cargarSecciones(primerPeriodo)
        }
    }

    const cargarSecciones = async (periodo) => {
        try {
            const response = await SeccionService.Search({ periodo_academico_id: periodo })
            setSecciones(response.data ?? [])
        } catch {
            setSecciones([])
        }
    }

    const handlePeriodoChange = async (event) => {
        const nuevoPeriodo = event.target.value
        setPeriodoId(nuevoPeriodo)
        setSeccionesSeleccionadas([])
        await cargarSecciones(nuevoPeriodo)
    }

    const toggleSeccion = (seccionId) => {
        setSeccionesSeleccionadas((prev) =>
            prev.includes(seccionId)
                ? prev.filter((id) => id !== seccionId)
                : [...prev, seccionId]
        )
    }

    const handleSubmit = async (event) => {
        event.preventDefault()
        setIsSubmitting(true)
        setError(null)

        try {
            await createMatricula({
                periodo_academico_id: Number(periodoId),
                comprobante_url: comprobanteUrl,
                secciones_ids: seccionesSeleccionadas,
            })
            setDialogOpen(false)
            await loadMatriculas({ showLoading: true })
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudo crear la matrícula')
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <section className="space-y-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <h2 className="text-2xl font-semibold text-slate-900">Matrícula</h2>
                    <p className="mt-1 text-sm text-neutral-600">
                        Solicita tu matrícula y descarga tu ficha una vez validada.
                    </p>
                </div>

                <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                    <button
                        type="button"
                        className="primary inline-flex items-center gap-2"
                        onClick={handleOpenDialog}
                    >
                        <Plus className="h-4 w-4" />
                        Solicitar matrícula
                    </button>
                    <Dialog.Surface>
                        <Dialog.Header>Solicitar matrícula</Dialog.Header>
                        <Dialog.Content>
                            <form id="matricula-form" className="space-y-4" onSubmit={handleSubmit}>
                                <label className="flex flex-col gap-2 text-sm">
                                    Periodo académico
                                    <select value={periodoId} onChange={handlePeriodoChange} required>
                                        <option value="" disabled>Selecciona un periodo</option>
                                        {periodos.map((periodo) => (
                                            <option key={periodo.id} value={periodo.id}>
                                                {periodo.semestre}
                                            </option>
                                        ))}
                                    </select>
                                </label>

                                <div className="flex flex-col gap-2 text-sm">
                                    Secciones disponibles
                                    {secciones.length ? (
                                        <div className="space-y-1 rounded-md border border-neutral-300 p-3">
                                            {secciones.map((seccion) => (
                                                <label key={seccion.id} className="flex items-center gap-2">
                                                    <input
                                                        type="checkbox"
                                                        checked={seccionesSeleccionadas.includes(seccion.id)}
                                                        onChange={() => toggleSeccion(seccion.id)}
                                                    />
                                                    {seccion.nombre} — {seccion.cupos_ocupados}/{seccion.aforo} cupos ocupados
                                                </label>
                                            ))}
                                        </div>
                                    ) : (
                                        <p className="text-xs text-neutral-500">No hay secciones disponibles para este periodo.</p>
                                    )}
                                </div>

                                <label className="flex flex-col gap-2 text-sm">
                                    URL del comprobante de pago
                                    <input
                                        type="text"
                                        value={comprobanteUrl}
                                        onChange={(event) => setComprobanteUrl(event.target.value)}
                                        placeholder="https://..."
                                        required
                                    />
                                </label>
                            </form>
                        </Dialog.Content>
                        <Dialog.Footer>
                            <button
                                type="submit"
                                form="matricula-form"
                                className="primary"
                                disabled={isSubmitting || seccionesSeleccionadas.length === 0}
                            >
                                {isSubmitting ? 'Enviando...' : 'Enviar solicitud'}
                            </button>
                            <Dialog.Trigger className="subtle">Cancelar</Dialog.Trigger>
                        </Dialog.Footer>
                    </Dialog.Surface>
                </Dialog>
            </div>

            {error && (
                <p className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                </p>
            )}

            <div className="rounded-lg border border-neutral-300 bg-neutral-50 p-4">
                <div className="mb-4 flex items-center gap-2 text-sm text-neutral-600">
                    <ClipboardList className="h-4 w-4" />
                    <span>Mis matrículas</span>
                </div>

                {isLoading ? (
                    <div className="flex justify-center py-10">
                        <Spinner />
                    </div>
                ) : (
                    <MatriculasTable
                        matriculas={matriculas}
                        emptyMessage="Aún no has solicitado matrícula."
                        showFicha
                    />
                )}
            </div>
        </section>
    )
}