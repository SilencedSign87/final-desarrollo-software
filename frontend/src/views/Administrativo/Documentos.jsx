import { useCallback, useEffect, useState } from 'react'
import { FileCheck } from 'lucide-react'
import DocumentRequestsTable from '../../components/documents/DocumentRequestsTable'
import Dialog from '../../components/Dialog'
import Spinner from '../../components/spinner'
import { getDocumentRequests, issueDocument } from '../../services/documentsService'

export default function AdministrativoDocumentos() {
    const [requests, setRequests] = useState([])
    const [selectedRequest, setSelectedRequest] = useState(null)
    const [isLoading, setIsLoading] = useState(true)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [error, setError] = useState(null)
    const [dialogOpen, setDialogOpen] = useState(false)

    const loadRequests = useCallback(async ({ showLoading = false } = {}) => {
        if (showLoading) {
            setIsLoading(true)
        }
        setError(null)
        try {
            const response = await getDocumentRequests()
            setRequests(response.data.data ?? [])
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudieron cargar las solicitudes')
        } finally {
            if (showLoading) {
                setIsLoading(false)
            }
        }
    }, [])

    useEffect(() => {
        let active = true

        getDocumentRequests()
            .then((response) => {
                if (active) {
                    setRequests(response.data.data ?? [])
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
    }, [])

    const openIssueDialog = (request) => {
        setSelectedRequest(request)
        setDialogOpen(true)
    }

    const handleIssue = async () => {
        if (!selectedRequest) return

        setIsSubmitting(true)
        setError(null)

        try {
            await issueDocument(selectedRequest.id)
            setDialogOpen(false)
            setSelectedRequest(null)
            await loadRequests({ showLoading: true })
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudo emitir el documento')
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <section className="space-y-6">
            <div>
                <h2 className="text-2xl font-semibold text-slate-900">Emisión de documentos</h2>
                <p className="mt-1 text-sm text-neutral-600">
                    Emite certificados autorizados. El sistema generará el PDF y el código QR automáticamente.
                </p>
            </div>

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
                <DocumentRequestsTable
                    requests={requests}
                    emptyMessage="No hay solicitudes registradas."
                    showDownload
                    actions={(request) =>
                        request.estado === 'autorizado' ? (
                            <button
                                type="button"
                                className="primary inline-flex items-center gap-2"
                                onClick={() => openIssueDialog(request)}
                            >
                                <FileCheck className="h-4 w-4" />
                                Emitir
                            </button>
                        ) : request.estado === 'emitido' ? (
                            <span className="text-xs text-neutral-500">Documento emitido</span>
                        ) : (
                            <span className="text-xs text-neutral-500">Pendiente de autorización</span>
                        )
                    }
                />
            )}

            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <Dialog.Surface>
                    <Dialog.Header>Emitir documento</Dialog.Header>
                    <Dialog.Content>
                        {selectedRequest && (
                            <div className="space-y-3 text-sm text-neutral-600">
                                <p>
                                    Solicitud #{selectedRequest.id} · {selectedRequest.tipo_documento}
                                </p>
                                <p>
                                    Al confirmar, el sistema generará un PDF oficial con código QR de verificación.
                                </p>
                            </div>
                        )}
                    </Dialog.Content>
                    <Dialog.Footer>
                        <button
                            type="button"
                            className="primary"
                            disabled={isSubmitting}
                            onClick={handleIssue}
                        >
                            {isSubmitting ? 'Generando PDF...' : 'Confirmar emisión'}
                        </button>
                        <Dialog.Trigger className="subtle">Cancelar</Dialog.Trigger>
                    </Dialog.Footer>
                </Dialog.Surface>
            </Dialog>
        </section>
    )
}
