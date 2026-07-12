const ACTION_LABELS = {
    login: 'Login',
    login_fallido: 'Login fallido',
    logout: 'Logout',
    cambio_rol: 'Cambio de rol',
    autorizar_documento: 'Autorizar documento',
    rechazar_documento: 'Rechazar documento',
    emitir_documento: 'Emitir documento',
}

export default function AuditLogsTable({ logs, emptyMessage }) {
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
                <tbody className="divide-y divide-neutral-200 bg-white">
                    {logs.map((log) => (
                        <tr key={log.id}>
                            <td className="whitespace-nowrap px-4 py-3 text-neutral-600">
                                {log.fecha_creacion
                                    ? new Date(log.fecha_creacion).toLocaleString()
                                    : '—'}
                            </td>
                            <td className="px-4 py-3">
                                <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">
                                    {ACTION_LABELS[log.accion] ?? log.accion}
                                </span>
                            </td>
                            <td className="px-4 py-3 text-neutral-700">
                                {log.usuario_email || 'Sistema'}
                            </td>
                            <td className="px-4 py-3 text-neutral-600">{log.recurso || '—'}</td>
                            <td className="max-w-md px-4 py-3 text-neutral-700">{log.detalle}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}
