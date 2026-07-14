import { formatDateTime } from '../../utils/date'
import AuditActionBadge from './AuditActionBadge'
import { getActionStyle } from './auditStyles'

export default function AuditLogsTable({ logs, emptyMessage, highlightRoleChanges = false }) {
    if (!logs?.length) {
        return (
            <p className="rounded-lg border border-dashed border-neutral-300 px-4 py-8 text-center text-sm text-neutral-500">
                {emptyMessage}
            </p>
        )
    }

    return (
        <div className="overflow-x-auto rounded-lg border border-neutral-300">
            <table className="min-w-full divide-y divide-neutral-200 text-sm">
                <thead className="bg-neutral-50">
                    <tr>
                        <th className="px-4 py-3 text-left font-medium text-neutral-600">Fecha</th>
                        <th className="px-4 py-3 text-left font-medium text-neutral-600">Acción</th>
                        <th className="px-4 py-3 text-left font-medium text-neutral-600">Usuario</th>
                        <th className="px-4 py-3 text-left font-medium text-neutral-600">Recurso</th>
                        <th className="px-4 py-3 text-left font-medium text-neutral-600">Detalle</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-neutral-200">
                    {logs.map((log) => {
                        const style = getActionStyle(log.accion)
                        const rowClass = highlightRoleChanges && log.accion === 'cambio_rol'
                            ? 'bg-violet-50/70'
                            : style.row

                        return (
                            <tr key={log.id} className={rowClass}>
                                <td className="whitespace-nowrap px-4 py-3 text-neutral-600">
                                    {formatDateTime(log.fecha_creacion)}
                                </td>
                                <td className="px-4 py-3">
                                    <AuditActionBadge accion={log.accion} />
                                </td>
                                <td className="px-4 py-3 text-neutral-700">
                                    {log.usuario_email || (
                                        <span className="text-neutral-400 italic">Sistema</span>
                                    )}
                                </td>
                                <td className="px-4 py-3 font-mono text-xs text-neutral-600">
                                    {log.recurso || '—'}
                                </td>
                                <td className="max-w-md px-4 py-3 text-neutral-700">{log.detalle}</td>
                            </tr>
                        )
                    })}
                </tbody>
            </table>
        </div>
    )
}
