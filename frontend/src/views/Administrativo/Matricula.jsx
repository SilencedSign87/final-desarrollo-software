import { useCallback, useEffect, useState } from 'react'
import { Check, X } from 'lucide-react'
import MatriculasTable from '../../components/matricula/MatriculasTable'
import PeriodoPagoConfig from '../../components/matricula/PeriodoPagoConfig'
import Dialog from '../../components/Dialog'
import Spinner from '../../components/spinner'
import { getMatriculas, validarMatricula } from '../../services/matriculaService'

const FILTROS = [
    { value: '', label: 'Todas' },
    { value: 'pendiente', label: 'Pendientes' },
    { value: 'validada', label: 'Validadas' },
    { value: 'rechazada', label: 'Rechazadas' },
]

export default function AdministrativoMatricula() {
    const [matriculas, setMatriculas] = useState([])
    const [filtroEstado, setFiltroEstado] = useState('pendiente')
    const [selectedMatricula, setSelectedMatricula] = useState(null)
    const [accionSeleccionada, setAccionSeleccionada] = useState(null)
    const [observacion, setObservacion] = useState('')
    const [isLoading, setIsLoading] = useState(true)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [error, setError] = useState(null)
    const [dialogOpen, setDialogOpen] = useState(false)

    const loadMatriculas = useCallback(async (estado) => {
        try {
            const response = await getMatriculas(estado || undefined)
            setMatriculas(response.data ?? [])
            setError(null)
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudieron cargar las matrículas')
        } finally {
            setIsLoading(false)
        }
    }, [])

    useEffect(() => {
        let active = true

        getMatriculas(filtroEstado || undefined)
            .then((response) => {
                if (active) {
                    setMatriculas(response.data ?? [])
                    setError(null)
                }
            })
            .catch((requestError) => {
                if (active) {
                    setError(requestError.response?.data?.error ?? 'No se pudieron cargar las matrículas')
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
    }, [filtroEstado])

    const handleFiltroChange = (value) => {
        setIsLoading(true)
        setFiltroEstado(value)
    }

    const openDialog = (matricula, accion) => {
        setSelectedMatricula(matricula)
        setAccionSeleccionada(accion)
        setObservacion('')
        setDialogOpen(true)
    }

    const handleConfirm = async () => {
        if (!selectedMatricula || !accionSeleccionada) return

        setIsSubmitting(true)
        setError(null)

        try {
            await validarMatricula(selectedMatricula.id, {
                estado: accionSeleccionada,
                observacion: observacion || undefined,
            })
            setDialogOpen(false)
            setSelectedMatricula(null)
            setIsLoading(true)
            await loadMatriculas(filtroEstado)
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudo actualizar la matrícula')
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <section className="space-y-6">
            <div>
                <h2 className="text-2xl font-semibold text-slate-900">Validación de matrículas</h2>
                <p className="mt-1 text-sm text-neutral-600">
                    Revisa el comprobante de pago y valida o rechaza cada solicitud.
                </p>
            </div>

            <PeriodoPagoConfig />

            <div className="flex gap-2">
                {FILTROS.map((filtro) => (
                    <button
                        key={filtro.value}
                        type="button"
                        className={filtroEstado === filtro.value ? 'primary' : 'subtle'}
                        onClick={() => handleFiltroChange(filtro.value)}
                    >
                        {filtro.label}
                    </button>
                ))}
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
                <MatriculasTable
                    matriculas={matriculas}
                    emptyMessage="No hay matrículas con este filtro."
                    actions={(matricula) =>
                        matricula.estado === 'pendiente' ? (
                            <div className="flex gap-2">
                                <button
                                    type="button"
                                    className="primary inline-flex items-center gap-1"
                                    onClick={() => openDialog(matricula, 'validada')}
                                >
                                    <Check className="h-4 w-4" />
                                    Validar
                                </button>
                                <button
                                    type="button"
                                    className="subtle inline-flex items-center gap-1 text-red-700"
                                    onClick={() => openDialog(matricula, 'rechazada')}
                                >
                                    <X className="h-4 w-4" />
                                    Rechazar
                                </button>
                            </div>
                        ) : (
                            <span className="text-xs text-neutral-500">Ya procesada</span>
                        )
                    }
                />
            )}

            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <Dialog.Surface>
                    <Dialog.Header>
                        {accionSeleccionada === 'validada' ? 'Validar matrícula' : 'Rechazar matrícula'}
                    </Dialog.Header>
                    <Dialog.Content>
                        {selectedMatricula && (
                            <div className="space-y-3 text-sm text-neutral-600">
                                <p>
                                    Matrícula #{selectedMatricula.id} · {selectedMatricula.estudiante_nombre}
                                </p>
                                <label className="flex flex-col gap-2">
                                    Observación {accionSeleccionada === 'rechazada' ? '(motivo del rechazo)' : '(opcional)'}
                                    <textarea
                                        className="min-h-20 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        value={observacion}
                                        onChange={(event) => setObservacion(event.target.value)}
                                    />
                                </label>
                            </div>
                        )}
                    </Dialog.Content>
                    <Dialog.Footer>
                        <button
                            type="button"
                            className="primary"
                            disabled={isSubmitting}
                            onClick={handleConfirm}
                        >
                            {isSubmitting ? 'Guardando...' : 'Confirmar'}
                        </button>
                        <Dialog.Trigger className="subtle">Cancelar</Dialog.Trigger>
                    </Dialog.Footer>
                </Dialog.Surface>
            </Dialog>
        </section>
    )
}