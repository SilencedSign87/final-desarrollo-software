const STATUS_STYLES = {
    pendiente: 'bg-amber-100 text-amber-800',
    validada: 'bg-emerald-100 text-emerald-800',
    rechazada: 'bg-red-100 text-red-800',
}

const STATUS_LABELS = {
    pendiente: 'Pendiente',
    validada: 'Validada',
    rechazada: 'Rechazada',
}

export default function MatriculaStatusBadge({ status }) {
    return (
        <span
            className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${STATUS_STYLES[status] ?? 'bg-neutral-100 text-neutral-700'}`}
        >
            {STATUS_LABELS[status] ?? status}
        </span>
    )
}