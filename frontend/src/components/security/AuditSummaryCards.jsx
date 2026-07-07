export default function AuditSummaryCards({ summary }) {
    const items = [
        { label: 'Usuarios registrados', value: summary.total_usuarios },
        { label: 'Solicitudes de documentos', value: summary.total_solicitudes_documento },
        { label: 'Documentos pendientes', value: summary.documentos_pendientes },
        { label: 'Documentos emitidos', value: summary.documentos_emitidos },
    ]

    return (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {items.map((item) => (
                <article
                    key={item.label}
                    className="rounded-lg border border-neutral-300 bg-neutral-50 p-5"
                >
                    <p className="text-sm text-neutral-600">{item.label}</p>
                    <p className="mt-2 text-3xl font-semibold text-slate-900">{item.value}</p>
                </article>
            ))}
        </div>
    )
}
