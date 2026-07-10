import { useCallback, useEffect, useState } from 'react'
import { Check, X } from 'lucide-react'
import DocumentRequestsTable from '../../components/documents/DocumentRequestsTable'
import TipoDocumentoPagoConfig from '../../components/documents/TipoDocumentoPagoConfig'
import Spinner from '../../components/spinner'
import { authorizeDocumentRequest, getDocumentRequests } from '../../services/documentsService'

export default function DireccionDocumentos() {
    const [requests, setRequests] = useState([])
    const [isLoading, setIsLoading] = useState(true)
    const [processingId, setProcessingId] = useState(null)
    const [error, setError] = useState(null)

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

    const handleAuthorization = async (requestId, aprobado) => {
        setProcessingId(requestId)
        setError(null)

        try {
            await authorizeDocumentRequest(requestId, { aprobado })
            await loadRequests({ showLoading: true })
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudo procesar la autorización')
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
                <DocumentRequestsTable
                    requests={requests}
                    emptyMessage="No hay solicitudes pendientes de revisión."
                    showComprobante
                    actions={(request) =>
                        request.estado === 'pendiente_autorizacion' ? (
                            <div className="flex flex-wrap gap-2">
                                <button
                                    type="button"
                                    className="primary inline-flex items-center gap-2"
                                    disabled={processingId === request.id}
                                    onClick={() => handleAuthorization(request.id, true)}
                                >
                                    <Check className="h-4 w-4" />
                                    Autorizar
                                </button>
                                <button
                                    type="button"
                                    className="secondary inline-flex items-center gap-2"
                                    disabled={processingId === request.id}
                                    onClick={() => handleAuthorization(request.id, false)}
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
            )}
        </section>
    )
}
