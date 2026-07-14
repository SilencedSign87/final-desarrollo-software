import { ACTION_LABELS, getActionStyle } from './auditStyles'

export default function AuditLegend() {
    const items = Object.entries(ACTION_LABELS)

    return (
        <div className="flex flex-wrap gap-2">
            {items.map(([accion, label]) => {
                const style = getActionStyle(accion)
                return (
                    <span
                        key={accion}
                        className={`inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-[11px] font-medium ring-1 ring-inset ${style.badge}`}
                    >
                        <span className={`h-1.5 w-1.5 rounded-full ${style.dot}`} />
                        {label}
                    </span>
                )
            })}
        </div>
    )
}
