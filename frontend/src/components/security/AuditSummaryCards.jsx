const CARD_STYLES = [
    {
        label: 'Usuarios registrados',
        key: 'total_usuarios',
        card: 'border-sky-200 bg-sky-50',
        labelColor: 'text-sky-700',
        valueColor: 'text-sky-900',
    },
    {
        label: 'Solicitudes de documentos',
        key: 'total_solicitudes_documento',
        card: 'border-slate-200 bg-slate-50',
        labelColor: 'text-slate-600',
        valueColor: 'text-slate-900',
    },
    {
        label: 'Documentos pendientes',
        key: 'documentos_pendientes',
        card: 'border-amber-200 bg-amber-50',
        labelColor: 'text-amber-700',
        valueColor: 'text-amber-900',
    },
    {
        label: 'Documentos emitidos',
        key: 'documentos_emitidos',
        card: 'border-emerald-200 bg-emerald-50',
        labelColor: 'text-emerald-700',
        valueColor: 'text-emerald-900',
    },
    {
        label: 'Eventos de bitácora',
        key: 'total_eventos_auditoria',
        card: 'border-indigo-200 bg-indigo-50',
        labelColor: 'text-indigo-700',
        valueColor: 'text-indigo-900',
    },
    {
        label: 'Cambios de rol',
        key: 'cambios_rol',
        card: 'border-violet-200 bg-violet-50',
        labelColor: 'text-violet-700',
        valueColor: 'text-violet-900',
    },
]

export default function AuditSummaryCards({ summary }) {
    return (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {CARD_STYLES.map((item) => (
                <article
                    key={item.key}
                    className={`rounded-lg border p-5 ${item.card}`}
                >
                    <p className={`text-sm font-medium ${item.labelColor}`}>{item.label}</p>
                    <p className={`mt-2 text-3xl font-semibold ${item.valueColor}`}>
                        {summary[item.key] ?? 0}
                    </p>
                </article>
            ))}
        </div>
    )
}
