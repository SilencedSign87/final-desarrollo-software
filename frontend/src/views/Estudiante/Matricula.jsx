import { useCallback, useEffect, useMemo, useState } from 'react'
import { ClipboardList, Plus } from 'lucide-react'
import MatriculasTable from '../../components/matricula/MatriculasTable'
import Dialog from '../../components/Dialog'
import Spinner from '../../components/spinner'
import { createMatricula, getMisMatriculas } from '../../services/matriculaService'
import { GetCursosDisponibles } from '../../services/cursos'
import { PeriodoAcademicoService } from '../../services/periodoAcademicoService'
import { SeccionService } from '../../services/seccionService'

export default function EstudianteMatricula() {
    const [matriculas, setMatriculas] = useState([])
    const [periodos, setPeriodos] = useState([])
    const [secciones, setSecciones] = useState([])
    const [cursosDisponibles, setCursosDisponibles] = useState([])
    const [semestreActual, setSemestreActual] = useState(null)
    const [periodoId, setPeriodoId] = useState('')
    const [comprobante, setComprobante] = useState(null)
    const [seccionesSeleccionadas, setSeccionesSeleccionadas] = useState([])
    const [isLoading, setIsLoading] = useState(true)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [error, setError] = useState(null)
    const [dialogOpen, setDialogOpen] = useState(false)
    const [confirmando, setConfirmando] = useState(false)

    const periodoSeleccionado = useMemo(
        () => periodos.find((periodo) => String(periodo.id) === String(periodoId)),
        [periodos, periodoId]
    )
    const requierePago = Boolean(periodoSeleccionado?.requiere_pago)

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
        setConfirmando(false)
        setSeccionesSeleccionadas([])
        setComprobante(null)
        setError(null)

        try {
            const response = await GetCursosDisponibles()
            setCursosDisponibles(response.data?.cursos ?? [])
            setSemestreActual(response.data?.semestre_actual ?? null)
        } catch (requestError) {
            setCursosDisponibles([])
            setError(requestError.response?.data?.error ?? 'No se pudieron cargar tus cursos disponibles')
        }

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

    // Solo se muestran secciones de cursos que le corresponden al estudiante
    // (semestre actual o repitencia con prerequisitos cumplidos).
    const cursosDisponiblesIds = new Set(cursosDisponibles.map((c) => c.id))
    const seccionesFiltradas = secciones.filter((s) => cursosDisponiblesIds.has(s.curso_id))

    const periodoActivo = periodos[0]
    const matriculaBloqueante = periodoActivo
        ? matriculas.find(
              (m) =>
                  m.periodo_academico_id === periodoActivo.id &&
                  ['pendiente', 'validada'].includes(m.estado)
          )
        : null

    const seccionesSeleccionadasInfo = seccionesFiltradas.filter((s) =>
        seccionesSeleccionadas.includes(s.id)
    )

    const handlePeriodoChange = async (event) => {
        const nuevoPeriodo = event.target.value
        setPeriodoId(nuevoPeriodo)
        setSeccionesSeleccionadas([])
        setComprobante(null)
        await cargarSecciones(nuevoPeriodo)
    }

    const toggleSeccion = (seccionId) => {
        setSeccionesSeleccionadas((prev) =>
            prev.includes(seccionId)
                ? prev.filter((id) => id !== seccionId)
                : [...prev, seccionId]
        )
    }

    const handleRevisar = (event) => {
        event.preventDefault()
        setError(null)

        if (requierePago && !comprobante) {
            setError('Debes adjuntar el comprobante de pago para este periodo')
            return
        }

        setConfirmando(true)
    }

    const handleConfirmar = async () => {
        setIsSubmitting(true)
        setError(null)

        if (requierePago && !comprobante) {
            setError('Debes adjuntar el comprobante de pago para este periodo')
            setIsSubmitting(false)
            return
        }

        try {
            await createMatricula({
                periodo_academico_id: Number(periodoId),
                secciones_ids: seccionesSeleccionadas,
                comprobante,
            })
            setDialogOpen(false)
            setConfirmando(false)
            await loadMatriculas({ showLoading: true })
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudo crear la matrícula')
            setConfirmando(false)
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

                {matriculaBloqueante ? (
                    <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-2 text-sm text-amber-800">
                        Ya tienes una matrícula <strong>{matriculaBloqueante.estado}</strong> para{' '}
                        {periodoActivo?.semestre}. {matriculaBloqueante.estado === 'pendiente'
                            ? 'Espera a que sea validada.'
                            : 'No puedes solicitar otra en este periodo.'}
                    </div>
                ) : (
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
                        <Dialog.Header>
                            {confirmando ? 'Revisa tu solicitud' : 'Solicitar matrícula'}
                        </Dialog.Header>
                        <Dialog.Content>
                            {confirmando ? (
                                <div className="space-y-3 text-sm">
                                    <p className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-amber-800">
                                        Verifica que los cursos y secciones sean correctos. Una vez
                                        enviada, no podrás modificar ni volver a solicitar tu
                                        matrícula mientras esté pendiente o validada.
                                    </p>
                                    <p><strong>Periodo:</strong> {periodoSeleccionado?.semestre ?? periodoActivo?.semestre}</p>
                                    <div>
                                        <strong>Cursos a matricular:</strong>
                                        <ul className="mt-1 list-disc space-y-1 pl-5">
                                            {seccionesSeleccionadasInfo.map((s) => (
                                                <li key={s.id}>
                                                    {s.curso_nombre ?? cursosDisponibles.find((c) => c.id === s.curso_id)?.nombre} — Sección {s.nombre}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                    <p>
                                        <strong>Comprobante:</strong>{' '}
                                        {requierePago
                                            ? (comprobante?.name ?? 'No adjunto')
                                            : 'No requerido'}
                                    </p>
                                </div>
                            ) : (
                            <form id="matricula-form" className="space-y-4" onSubmit={handleRevisar}>
                                <label className="flex flex-col gap-2 text-sm">
                                    Periodo académico
                                    <select value={periodoId} onChange={handlePeriodoChange} required>
                                        <option value="" disabled>Selecciona un periodo</option>
                                        {periodos.map((periodo) => (
                                            <option key={periodo.id} value={periodo.id}>
                                                {periodo.semestre}
                                                {periodo.requiere_pago ? ' (requiere pago)' : ''}
                                            </option>
                                        ))}
                                    </select>
                                </label>

                                <div className="flex flex-col gap-2 text-sm">
                                    <div className="flex items-center justify-between">
                                        <span>Cursos y secciones disponibles</span>
                                        {semestreActual && (
                                            <span className="text-xs text-neutral-500">
                                                Semestre actual: {semestreActual}
                                            </span>
                                        )}
                                    </div>
                                    {seccionesFiltradas.length ? (
                                        <div className="space-y-3 rounded-md border border-neutral-300 p-3">
                                            {cursosDisponibles.map((curso) => {
                                                const seccionesDelCurso = seccionesFiltradas.filter(
                                                    (s) => s.curso_id === curso.id
                                                )
                                                if (!seccionesDelCurso.length) return null
                                                return (
                                                    <div key={curso.id} className="space-y-1">
                                                        <p className="text-xs font-semibold text-slate-700">
                                                            {curso.nombre}{' '}
                                                            <span className="font-normal text-neutral-500">
                                                                (Semestre {curso.semestre_num})
                                                            </span>
                                                        </p>
                                                        {seccionesDelCurso.map((seccion) => (
                                                            <label key={seccion.id} className="flex items-center gap-2 pl-2">
                                                                <input
                                                                    type="checkbox"
                                                                    checked={seccionesSeleccionadas.includes(seccion.id)}
                                                                    onChange={() => toggleSeccion(seccion.id)}
                                                                />
                                                                {seccion.nombre} — {seccion.cupos_ocupados}/{seccion.aforo} cupos ocupados
                                                            </label>
                                                        ))}
                                                    </div>
                                                )
                                            })}
                                        </div>
                                    ) : (
                                        <p className="text-xs text-neutral-500">
                                            No hay secciones abiertas para los cursos que te corresponden en este periodo.
                                        </p>
                                    )}
                                </div>

                                {requierePago && (
                                    <label className="flex flex-col gap-2 text-sm">
                                        Comprobante de pago (PDF o imagen)
                                        <input
                                            type="file"
                                            accept=".pdf,.png,.jpg,.jpeg,.webp,application/pdf,image/*"
                                            onChange={(event) => setComprobante(event.target.files?.[0] ?? null)}
                                            required
                                        />
                                        <span className="text-xs text-neutral-500">Máximo 5 MB</span>
                                    </label>
                                )}
                            </form>
                            )}
                        </Dialog.Content>
                        <Dialog.Footer>
                            {confirmando ? (
                                <>
                                    <button
                                        type="button"
                                        className="primary"
                                        disabled={isSubmitting}
                                        onClick={handleConfirmar}
                                    >
                                        {isSubmitting ? 'Enviando...' : 'Confirmar y enviar'}
                                    </button>
                                    <button
                                        type="button"
                                        className="subtle"
                                        disabled={isSubmitting}
                                        onClick={() => setConfirmando(false)}
                                    >
                                        Volver a revisar
                                    </button>
                                </>
                            ) : (
                                <>
                                    <button
                                        type="submit"
                                        form="matricula-form"
                                        className="primary"
                                        disabled={seccionesSeleccionadas.length === 0}
                                    >
                                        Continuar
                                    </button>
                                    <Dialog.Trigger className="subtle">Cancelar</Dialog.Trigger>
                                </>
                            )}
                        </Dialog.Footer>
                    </Dialog.Surface>
                </Dialog>
                )}
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
