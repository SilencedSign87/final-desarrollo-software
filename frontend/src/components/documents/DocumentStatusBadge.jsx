const STATUS_STYLES = {
    pendiente_autorizacion: 'bg-amber-100 text-amber-800',
    autorizado: 'bg-blue-100 text-blue-800',
    emitido: 'bg-emerald-100 text-emerald-800',
    rechazado: 'bg-red-100 text-red-800',
}

const STATUS_LABELS = {
    pendiente_autorizacion: 'Pendiente de autorización',
    autorizado: 'Autorizado',
    emitido: 'Emitido',
    rechazado: 'Rechazado',
}

export default function DocumentStatusBadge({ status }) {
    return (
        <span
            className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${STATUS_STYLES[status] ?? 'bg-neutral-100 text-neutral-700'}`}
        >
            {STATUS_LABELS[status] ?? status}
        </span>
    )
}
