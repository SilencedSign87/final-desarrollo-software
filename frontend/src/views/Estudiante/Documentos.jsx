import { useCallback, useEffect, useState } from 'react'
import { FileText, Plus } from 'lucide-react'
import DocumentRequestsTable from '../../components/documents/DocumentRequestsTable'
import Dialog from '../../components/Dialog'
import Spinner from '../../components/spinner'
import { createDocumentRequest, getDocumentRequests } from '../../services/documentsService'

const DOCUMENT_TYPES = [
    'Constancia de estudios',
    'Certificado de notas',
    'Constancia de matrícula',
]

export default function EstudianteDocumentos() {
    const [requests, setRequests] = useState([])
    const [tipoDocumento, setTipoDocumento] = useState(DOCUMENT_TYPES[0])
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

    const handleSubmit = async (event) => {
        event.preventDefault()
        setIsSubmitting(true)
        setError(null)

        try {
            await createDocumentRequest({ tipo_documento: tipoDocumento })
            setDialogOpen(false)
            await loadRequests({ showLoading: true })
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudo crear la solicitud')
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <section className="space-y-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <h2 className="text-2xl font-semibold text-slate-900">Certificados y documentos</h2>
                    <p className="mt-1 text-sm text-neutral-600">
                        Solicita certificados y constancias en línea.
                    </p>
                </div>

                <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                    <Dialog.Trigger className="primary inline-flex items-center gap-2">
                        <Plus className="h-4 w-4" />
                        Nueva solicitud
                    </Dialog.Trigger>
                    <Dialog.Surface>
                        <Dialog.Header>Solicitar documento</Dialog.Header>
                        <Dialog.Content>
                            <form id="document-request-form" className="space-y-4" onSubmit={handleSubmit}>
                                <label className="flex flex-col gap-2 text-sm">
                                    Tipo de documento
                                    <select
                                        value={tipoDocumento}
                                        onChange={(event) => setTipoDocumento(event.target.value)}
                                    >
                                        {DOCUMENT_TYPES.map((type) => (
                                            <option key={type} value={type}>
                                                {type}
                                            </option>
                                        ))}
                                    </select>
                                </label>
                            </form>
                        </Dialog.Content>
                        <Dialog.Footer>
                            <button
                                type="submit"
                                form="document-request-form"
                                className="primary"
                                disabled={isSubmitting}
                            >
                                {isSubmitting ? 'Enviando...' : 'Enviar solicitud'}
                            </button>
                            <Dialog.Trigger className="subtle">Cancelar</Dialog.Trigger>
                        </Dialog.Footer>
                    </Dialog.Surface>
                </Dialog>
            </div>

            {error && (
                <p className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                </p>
            )}

            <div className="rounded-lg border border-neutral-300 bg-neutral-50 p-4">
                <div className="mb-4 flex items-center gap-2 text-sm text-neutral-600">
                    <FileText className="h-4 w-4" />
                    <span>Mis solicitudes</span>
                </div>

                {isLoading ? (
                    <div className="flex justify-center py-10">
                        <Spinner />
                    </div>
                ) : (
                    <DocumentRequestsTable
                        requests={requests}
                        emptyMessage="Aún no has solicitado documentos."
                        showDownload
                    />
                )}
            </div>
        </section>
    )
}
