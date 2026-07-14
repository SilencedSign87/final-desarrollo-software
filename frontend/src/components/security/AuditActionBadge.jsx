import { ACTION_LABELS, getActionStyle } from './auditStyles'

export default function AuditActionBadge({ accion }) {
    const style = getActionStyle(accion)

    return (
        <span
            className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset ${style.badge}`}
        >
            <span className={`h-1.5 w-1.5 rounded-full ${style.dot}`} />
            {ACTION_LABELS[accion] ?? accion}
        </span>
    )
}
