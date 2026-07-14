import { useCallback, useEffect, useState } from 'react'
import { Check, X } from 'lucide-react'
import DocumentPagination from '../../components/documents/DocumentPagination'
import DocumentRequestsTable from '../../components/documents/DocumentRequestsTable'
import TipoDocumentoPagoConfig from '../../components/documents/TipoDocumentoPagoConfig'
import Dialog from '../../components/Dialog'
import Spinner from '../../components/Spinner'
import { authorizeDocumentRequest, getDocumentRequests } from '../../services/documentsService'

const PER_PAGE = 10

export default function DireccionDocumentos() {
    const [requests, setRequests] = useState([])
    const [meta, setMeta] = useState(null)
    const [page, setPage] = useState(1)
    const [isLoading, setIsLoading] = useState(true)
    const [processingId, setProcessingId] = useState(null)
    const [error, setError] = useState(null)
    const [rejectDialogOpen, setRejectDialogOpen] = useState(false)
    const [selectedRequest, setSelectedRequest] = useState(null)
    const [observacion, setObservacion] = useState('')

    const loadRequests = useCallback(async ({ showLoading = false, pageToLoad = page } = {}) => {
        if (showLoading) {
            setIsLoading(true)
        }
        setError(null)
        try {
            const response = await getDocumentRequests({ page: pageToLoad, per_page: PER_PAGE })
            setRequests(response.data.data ?? [])
            setMeta(response.data.meta ?? null)
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudieron cargar las solicitudes')
        } finally {
            if (showLoading) {
                setIsLoading(false)
            }
        }
    }, [page])

    useEffect(() => {
        let active = true

        setIsLoading(true)
        getDocumentRequests({ page, per_page: PER_PAGE })
            .then((response) => {
                if (active) {
                    setRequests(response.data.data ?? [])
                    setMeta(response.data.meta ?? null)
                }
            })
            .catch((requestError) => {
                if (active) {
                    setError(requestError.response?.data?.error ?? 'No se pudieron cargar las solicitudes')
                }
            })
            .finally(() => {
                if (active) {
                    setIsLoading(false)
                }
            })

        return () => {
            active = false
        }
    }, [page])

    const handleAuthorize = async (requestId) => {
        setProcessingId(requestId)
        setError(null)

        try {
            await authorizeDocumentRequest(requestId, { aprobado: true })
            await loadRequests({ showLoading: true })
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudo autorizar la solicitud')
        } finally {
            setProcessingId(null)
        }
    }

    const openRejectDialog = (request) => {
        setSelectedRequest(request)
        setObservacion('')
        setRejectDialogOpen(true)
    }

    const handleReject = async () => {
        if (!selectedRequest) return
        if (!observacion.trim()) {
            setError('Debes indicar una observación al rechazar')
            return
        }

        setProcessingId(selectedRequest.id)
        setError(null)

        try {
            await authorizeDocumentRequest(selectedRequest.id, {
                aprobado: false,
                observacion: observacion.trim(),
            })
            setRejectDialogOpen(false)
            setSelectedRequest(null)
            setObservacion('')
            await loadRequests({ showLoading: true })
        } catch (requestError) {
            const detail = requestError.response?.data
            setError(
                detail?.error
                ?? detail?.message
                ?? (Array.isArray(detail?.validation_error)
                    ? detail.validation_error.map((item) => item.msg).join('. ')
                    : null)
                ?? 'No se pudo rechazar la solicitud'
            )
        } finally {
            setProcessingId(null)
        }
    }

    return (
        <section className="space-y-6">
            <div>
                <h2 className="text-2xl font-semibold text-slate-900">Autorización de documentos</h2>
                <p className="mt-1 text-sm text-neutral-600">
                    Autoriza o rechaza la emisión de documentos oficiales.
                </p>
            </div>

            <TipoDocumentoPagoConfig />

            {error && (
                <p className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                </p>
            )}

            {isLoading ? (
                <div className="flex justify-center py-10">
                    <Spinner />
                </div>
            ) : (
                <div className="space-y-4">
                    <DocumentRequestsTable
                        requests={requests}
                        emptyMessage="No hay solicitudes pendientes de revisión."
                        showComprobante
                        showObservacion
                        actions={(request) =>
                            request.estado === 'pendiente_autorizacion' ? (
                                <div className="flex flex-wrap gap-2">
                                    <button
                                        type="button"
                                        className="primary inline-flex items-center gap-2"
                                        disabled={processingId === request.id}
                                        onClick={() => handleAuthorize(request.id)}
                                    >
                                        <Check className="h-4 w-4" />
                                        Autorizar
                                    </button>
                                    <button
                                        type="button"
                                        className="secondary inline-flex items-center gap-2"
                                        disabled={processingId === request.id}
                                        onClick={() => openRejectDialog(request)}
                                    >
                                        <X className="h-4 w-4" />
                                        Rechazar
                                    </button>
                                </div>
                            ) : (
                                <span className="text-xs text-neutral-500">Revisión completada</span>
                            )
                        }
                    />
                    <DocumentPagination
                        meta={meta}
                        page={page}
                        onPageChange={setPage}
                        disabled={Boolean(processingId)}
                    />
                </div>
            )}

            <Dialog open={rejectDialogOpen} onOpenChange={setRejectDialogOpen}>
                <Dialog.Surface>
                    <Dialog.Header>Rechazar solicitud</Dialog.Header>
                    <Dialog.Content>
                        {selectedRequest && (
                            <div className="space-y-4 text-sm">
                                <p className="text-neutral-600">
                                    Ticket {selectedRequest.codigo_ticket || `#${selectedRequest.id}`} ·{' '}
                                    {selectedRequest.tipo_documento}
                                </p>
                                <label className="flex flex-col gap-2">
                                    Observación (obligatoria)
                                    <textarea
                                        className="min-h-24 rounded-md border border-neutral-300 px-3 py-2"
                                        value={observacion}
                                        onChange={(event) => setObservacion(event.target.value)}
                                        maxLength={255}
                                        placeholder="Indica el motivo del rechazo"
                                        required
                                    />
                                </label>
                            </div>
                        )}
                    </Dialog.Content>
                    <Dialog.Footer>
                        <button
                            type="button"
                            className="primary"
                            disabled={processingId === selectedRequest?.id || !observacion.trim()}
                            onClick={handleReject}
                        >
                            Confirmar rechazo
                        </button>
                        <Dialog.Trigger className="subtle">Cancelar</Dialog.Trigger>
                    </Dialog.Footer>
                </Dialog.Surface>
            </Dialog>
        </section>
    )
}
