import { useEffect, useState } from 'react'
import { PeriodoAcademicoService } from '../../services/periodoAcademicoService'

/**
 * Panel para que admin/dirección active o desactive el pago de matrícula por periodo.
 */
export default function PeriodoPagoConfig() {
    const [periodos, setPeriodos] = useState([])
    const [isLoading, setIsLoading] = useState(true)
    const [updatingId, setUpdatingId] = useState(null)
    const [error, setError] = useState(null)
    const [message, setMessage] = useState(null)

    const load = async () => {
        setIsLoading(true)
        setError(null)
        try {
            const response = await PeriodoAcademicoService.search()
            setPeriodos(response.data ?? [])
        } catch (requestError) {
            setError(requestError.response?.data?.message ?? 'No se pudieron cargar los periodos')
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        load()
    }, [])

    const togglePago = async (periodo) => {
        setUpdatingId(periodo.id)
        setError(null)
        setMessage(null)
        try {
            await PeriodoAcademicoService.update(periodo.id, {
                requiere_pago: !periodo.requiere_pago,
            })
            setMessage(
                `Periodo ${periodo.semestre}: pago ${!periodo.requiere_pago ? 'requerido' : 'no requerido'}`
            )
            await load()
        } catch (requestError) {
            setError(requestError.response?.data?.message ?? 'No se pudo actualizar el periodo')
        } finally {
            setUpdatingId(null)
        }
    }

    return (
        <div className="rounded-lg border border-neutral-300 bg-white p-4">
            <h3 className="text-sm font-semibold text-slate-900">Pago de matrícula por periodo</h3>
            <p className="mt-1 text-xs text-neutral-500">
                Si está activo, el estudiante debe adjuntar comprobante al solicitar matrícula.
            </p>

            {error && (
                <p className="mt-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
                    {error}
                </p>
            )}
            {message && (
                <p className="mt-3 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-emerald-700">
                    {message}
                </p>
            )}

            {isLoading ? (
                <p className="mt-3 text-xs text-neutral-500">Cargando periodos...</p>
            ) : (
                <ul className="mt-3 divide-y divide-neutral-200">
                    {periodos.map((periodo) => (
                        <li key={periodo.id} className="flex items-center justify-between gap-3 py-2 text-sm">
                            <div>
                                <span className="font-medium text-slate-800">{periodo.semestre}</span>
                                <span className="ml-2 text-xs text-neutral-500">({periodo.estado})</span>
                            </div>
                            <label className="inline-flex items-center gap-2 text-xs text-neutral-700">
                                <input
                                    type="checkbox"
                                    checked={Boolean(periodo.requiere_pago)}
                                    disabled={updatingId === periodo.id}
                                    onChange={() => togglePago(periodo)}
                                />
                                Requiere pago
                            </label>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    )
}
