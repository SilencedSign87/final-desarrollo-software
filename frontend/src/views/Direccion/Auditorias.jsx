import { useEffect, useState } from 'react'
import AuditSummaryCards from '../../components/security/AuditSummaryCards'
import Spinner from '../../components/spinner'
import { getAuditSummary } from '../../services/securityService'

export default function DireccionAuditorias() {
    const [summary, setSummary] = useState(null)
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        let active = true

        getAuditSummary()
            .then((response) => {
                if (active) {
                    setSummary(response.data)
                }
            })
            .catch((requestError) => {
                if (active) {
                    setError(requestError.response?.data?.error ?? 'No se pudo cargar el resumen de auditoría')
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
                <h2 className="text-2xl font-semibold text-slate-900">Auditorías y reportes</h2>
                <p className="mt-1 text-sm text-neutral-600">
                    Supervisa indicadores estratégicos del sistema académico.
                </p>
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
                summary && <AuditSummaryCards summary={summary} />
            )}
        </section>
    )
}
