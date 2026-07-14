import { useCallback, useEffect, useMemo, useState } from 'react'
import { FileText, Plus } from 'lucide-react'
import DocumentPagination from '../../components/documents/DocumentPagination'
import DocumentRequestsTable from '../../components/documents/DocumentRequestsTable'
import Dialog from '../../components/Dialog'
import Spinner from '../../components/Spinner'
import { createDocumentRequest, getDocumentRequests } from '../../services/documentsService'
import { getTiposDocumento } from '../../services/tipoDocumentoService'

const PER_PAGE = 10

export default function EstudianteDocumentos() {
    const [requests, setRequests] = useState([])
    const [meta, setMeta] = useState(null)
    const [page, setPage] = useState(1)
    const [tipos, setTipos] = useState([])
    const [tipoDocumentoId, setTipoDocumentoId] = useState('')
    const [comprobante, setComprobante] = useState(null)
    const [isLoading, setIsLoading] = useState(true)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [error, setError] = useState(null)
    const [dialogOpen, setDialogOpen] = useState(false)

    const tipoSeleccionado = useMemo(
        () => tipos.find((tipo) => String(tipo.id) === String(tipoDocumentoId)),
        [tipos, tipoDocumentoId]
    )
    const requierePago = Boolean(tipoSeleccionado?.requiere_pago)

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

    useEffect(() => {
        let active = true

        getTiposDocumento()
            .then((response) => {
                if (active) {
                    const data = response.data ?? []
                    setTipos(data)
                    if (data[0]) {
                        setTipoDocumentoId(String(data[0].id))
                    }
                }
            })
            .catch(() => {
                if (active) {
                    setTipos([])
                }
            })

        return () => {
            active = false
        }
    }, [])

    const handleOpenDialog = () => {
        setDialogOpen(true)
        setComprobante(null)
        if (tipos[0]) {
            setTipoDocumentoId(String(tipos[0].id))
        }
    }

    const handleSubmit = async (event) => {
        event.preventDefault()
        setIsSubmitting(true)
        setError(null)

        if (requierePago && !comprobante) {
            setError('Debes adjuntar el comprobante de pago para este documento')
            setIsSubmitting(false)
            return
        }

        try {
            await createDocumentRequest({
                tipo_documento_id: Number(tipoDocumentoId),
                comprobante,
            })
            setDialogOpen(false)
            setPage(1)
            await loadRequests({ showLoading: true, pageToLoad: 1 })
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
                    <button
                        type="button"
                        className="primary inline-flex items-center gap-2"
                        onClick={handleOpenDialog}
                    >
                        <Plus className="h-4 w-4" />
                        Nueva solicitud
                    </button>
                    <Dialog.Surface>
                        <Dialog.Header>Solicitar documento</Dialog.Header>
                        <Dialog.Content>
                            <form id="document-request-form" className="space-y-4" onSubmit={handleSubmit}>
                                <label className="flex flex-col gap-2 text-sm">
                                    Tipo de documento
                                    <select
                                        value={tipoDocumentoId}
                                        onChange={(event) => {
                                            setTipoDocumentoId(event.target.value)
                                            setComprobante(null)
                                        }}
                                        required
                                    >
                                        <option value="" disabled>Selecciona un tipo</option>
                                        {tipos.map((tipo) => (
                                            <option key={tipo.id} value={tipo.id}>
                                                {tipo.nombre}
                                                {tipo.requiere_pago ? ' (requiere pago)' : ''}
                                            </option>
                                        ))}
                                    </select>
                                </label>

                                {requierePago && (
                                    <label className="flex flex-col gap-2 text-sm">
                                        Comprobante de pago (PDF o imagen)
                                        <input
                                            type="file"
                                            accept=".pdf,.png,.jpg,.jpeg,.webp,application/pdf,image/*"
                                            onChange={(event) => setComprobante(event.target.files?.[0] ?? null)}
                                            required
                                        />
                                        <span className="text-xs text-neutral-500">Máximo 5 MB</span>
                                    </label>
                                )}
                            </form>
                        </Dialog.Content>
                        <Dialog.Footer>
                            <button
                                type="submit"
                                form="document-request-form"
                                className="primary"
                                disabled={isSubmitting || !tipoDocumentoId}
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
                    <div className="space-y-4">
                        <DocumentRequestsTable
                            requests={requests}
                            emptyMessage="Aún no has solicitado documentos."
                            showDownload
                            showComprobante
                            showObservacion
                        />
                        <DocumentPagination
                            meta={meta}
                            page={page}
                            onPageChange={setPage}
                        />
                    </div>
                )}
            </div>
        </section>
    )
}
