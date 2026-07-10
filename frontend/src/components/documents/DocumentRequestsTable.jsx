import DocumentStatusBadge from './DocumentStatusBadge'
import { getDocumentComprobanteUrl, getDocumentDownloadUrl } from '../../services/documentsService'

export default function DocumentRequestsTable({
    requests,
    emptyMessage,
    actions,
    showDownload = false,
    showComprobante = false,
}) {
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
                        {showComprobante && (
                            <th className="px-4 py-3 text-left font-medium text-neutral-600">Comprobante</th>
                        )}
                        {showDownload && (
                            <th className="px-4 py-3 text-left font-medium text-neutral-600">PDF / QR</th>
                        )}
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
                            <td className="px-4 py-3 text-neutral-900">
                                {request.tipo_documento}
                                {request.requiere_pago ? (
                                    <span className="ml-2 text-xs text-amber-700">Pago</span>
                                ) : null}
                            </td>
                            <td className="px-4 py-3">
                                <DocumentStatusBadge status={request.estado} />
                            </td>
                            <td className="px-4 py-3 text-neutral-600">
                                {new Date(request.fecha_creacion).toLocaleString()}
                            </td>
                            {showComprobante && (
                                <td className="px-4 py-3">
                                    {request.comprobante_url ? (
                                        <a
                                            href={request.comprobante_url.startsWith('/api/')
                                                ? request.comprobante_url
                                                : getDocumentComprobanteUrl(request.id)}
                                            className="text-blue-700 hover:underline"
                                            target="_blank"
                                            rel="noreferrer"
                                        >
                                            Ver comprobante
                                        </a>
                                    ) : (
                                        <span className="text-xs text-neutral-500">No aplica</span>
                                    )}
                                </td>
                            )}
                            {showDownload && (
                                <td className="px-4 py-3">
                                    {request.estado === 'emitido' ? (
                                        <div className="space-y-1">
                                            <a
                                                href={getDocumentDownloadUrl(request.id)}
                                                className="block text-blue-700 hover:underline"
                                                target="_blank"
                                                rel="noreferrer"
                                            >
                                                Descargar PDF
                                            </a>
                                            {request.qr_hash && (
                                                <span className="block text-xs text-neutral-500">
                                                    QR: {request.qr_hash.slice(0, 12)}...
                                                </span>
                                            )}
                                        </div>
                                    ) : (
                                        <span className="text-xs text-neutral-500">No disponible</span>
                                    )}
                                </td>
                            )}
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
