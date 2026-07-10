import { useEffect, useState } from 'react'
import MatriculaSummaryCards from '../../components/matricula/MatriculaSummaryCards'
import PeriodoPagoConfig from '../../components/matricula/PeriodoPagoConfig'
import Spinner from '../../components/spinner'
import { getMatriculaEstadisticas } from '../../services/matriculaService'

export default function DireccionMatricula() {
    const [summary, setSummary] = useState(null)
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        let active = true

        getMatriculaEstadisticas()
            .then((response) => {
                if (active) {
                    setSummary(response.data)
                }
            })
            .catch((requestError) => {
                if (active) {
                    setError(requestError.response?.data?.error ?? 'No se pudo cargar el resumen de matrícula')
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

    return (
        <section className="space-y-6">
            <div>
                <h2 className="text-2xl font-semibold text-slate-900">Estadísticas de matrícula</h2>
                <p className="mt-1 text-sm text-neutral-600">
                    Supervisa el estado de las solicitudes de matrícula por facultad.
                </p>
            </div>

            <PeriodoPagoConfig />

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
                summary && <MatriculaSummaryCards summary={summary} />
            )}
        </section>
    )
}