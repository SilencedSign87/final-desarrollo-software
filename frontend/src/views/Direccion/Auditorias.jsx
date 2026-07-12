import { useCallback, useEffect, useState } from 'react'
import AuditLogsTable from '../../components/security/AuditLogsTable'
import AuditSummaryCards from '../../components/security/AuditSummaryCards'
import Spinner from '../../components/spinner'
import {
    getAuditLogs,
    getAuditSummary,
    getRoleChangeHistory,
} from '../../services/securityService'

const ACTION_FILTERS = [
    { value: '', label: 'Todas' },
    { value: 'login', label: 'Login' },
    { value: 'login_fallido', label: 'Login fallido' },
    { value: 'cambio_rol', label: 'Cambio de rol' },
    { value: 'autorizar_documento', label: 'Autorizar' },
    { value: 'rechazar_documento', label: 'Rechazar' },
    { value: 'emitir_documento', label: 'Emitir' },
]

export default function DireccionAuditorias() {
    const [summary, setSummary] = useState(null)
    const [logs, setLogs] = useState([])
    const [logsMeta, setLogsMeta] = useState(null)
    const [roleChanges, setRoleChanges] = useState([])
    const [page, setPage] = useState(1)
    const [accion, setAccion] = useState('')
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState(null)

    const loadData = useCallback(async () => {
        setIsLoading(true)
        setError(null)
        try {
            const [summaryRes, logsRes, rolesRes] = await Promise.all([
                getAuditSummary(),
                getAuditLogs({ page, per_page: 15, accion: accion || undefined }),
                getRoleChangeHistory({ page: 1, per_page: 8 }),
            ])
            setSummary(summaryRes.data)
            setLogs(logsRes.data.data ?? [])
            setLogsMeta(logsRes.data.meta ?? null)
            setRoleChanges(rolesRes.data.data ?? [])
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudo cargar la auditoría')
        } finally {
            setIsLoading(false)
        }
    }, [page, accion])

    useEffect(() => {
        loadData()
    }, [loadData])

    return (
        <section className="space-y-8">
            <div>
                <h2 className="text-2xl font-semibold text-slate-900">Auditorías y reportes</h2>
                <p className="mt-1 text-sm text-neutral-600">
                    Indicadores estratégicos, bitácora de acciones críticas e historial de roles.
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
                <>
                    {summary && <AuditSummaryCards summary={summary} />}

                    <div className="space-y-4">
                        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                            <h3 className="text-lg font-semibold text-slate-900">Bitácora del sistema</h3>
                            <label className="flex items-center gap-2 text-sm text-neutral-600">
                                Filtrar
                                <select
                                    value={accion}
                                    onChange={(event) => {
                                        setPage(1)
                                        setAccion(event.target.value)
                                    }}
                                >
                                    {ACTION_FILTERS.map((option) => (
                                        <option key={option.value || 'all'} value={option.value}>
                                            {option.label}
                                        </option>
                                    ))}
                                </select>
                            </label>
                        </div>

                        <AuditLogsTable
                            logs={logs}
                            emptyMessage="Aún no hay eventos registrados en la bitácora."
                        />

                        {logsMeta && logsMeta.pages > 1 && (
                            <div className="flex items-center justify-between text-sm text-neutral-600">
                                <p>
                                    Página {logsMeta.page} de {logsMeta.pages}
                                </p>
                                <div className="flex gap-2">
                                    <button
                                        type="button"
                                        className="secondary"
                                        disabled={page <= 1}
                                        onClick={() => setPage((current) => current - 1)}
                                    >
                                        Anterior
                                    </button>
                                    <button
                                        type="button"
                                        className="secondary"
                                        disabled={page >= logsMeta.pages}
                                        onClick={() => setPage((current) => current + 1)}
                                    >
                                        Siguiente
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-slate-900">Historial de cambios de rol</h3>
                        <AuditLogsTable
                            logs={roleChanges}
                            emptyMessage="No se han registrado cambios de rol."
                        />
                    </div>
                </>
            )}
        </section>
    )
}
