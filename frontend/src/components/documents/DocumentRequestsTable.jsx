import DocumentStatusBadge from './DocumentStatusBadge'

export default function DocumentRequestsTable({ requests, emptyMessage, actions }) {
    if (!requests?.length) {
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
                        <th className="px-4 py-3 text-left font-medium text-neutral-600">ID</th>
                        <th className="px-4 py-3 text-left font-medium text-neutral-600">Estudiante</th>
                        <th className="px-4 py-3 text-left font-medium text-neutral-600">Documento</th>
                        <th className="px-4 py-3 text-left font-medium text-neutral-600">Estado</th>
                        <th className="px-4 py-3 text-left font-medium text-neutral-600">Fecha</th>
                        {actions && (
                            <th className="px-4 py-3 text-left font-medium text-neutral-600">Acciones</th>
                        )}
                    </tr>
                </thead>
                <tbody className="divide-y divide-neutral-200 bg-white">
                    {requests.map((request) => (
                        <tr key={request.id}>
                            <td className="px-4 py-3 text-neutral-900">{request.id}</td>
                            <td className="px-4 py-3 text-neutral-700">{request.estudiante_id}</td>
                            <td className="px-4 py-3 text-neutral-900">{request.tipo_documento}</td>
                            <td className="px-4 py-3">
                                <DocumentStatusBadge status={request.estado} />
                            </td>
                            <td className="px-4 py-3 text-neutral-600">
                                {new Date(request.fecha_creacion).toLocaleString()}
                            </td>
                            {actions && (
                                <td className="px-4 py-3">{actions(request)}</td>
                            )}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}
