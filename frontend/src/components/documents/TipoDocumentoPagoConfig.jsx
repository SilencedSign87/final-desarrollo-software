import { useEffect, useState } from 'react'
import {
    createTipoDocumento,
    getTiposDocumento,
    updateTipoDocumento,
} from '../../services/tipoDocumentoService'

/**
 * Panel para que admin/dirección configure si cada tipo de documento requiere pago.
 */
export default function TipoDocumentoPagoConfig() {
    const [tipos, setTipos] = useState([])
    const [nuevoNombre, setNuevoNombre] = useState('')
    const [nuevoRequierePago, setNuevoRequierePago] = useState(false)
    const [isLoading, setIsLoading] = useState(true)
    const [isCreating, setIsCreating] = useState(false)
    const [updatingId, setUpdatingId] = useState(null)
    const [error, setError] = useState(null)

    const load = async () => {
        setIsLoading(true)
        setError(null)
        try {
            const response = await getTiposDocumento()
            setTipos(response.data ?? [])
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudieron cargar los tipos')
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        load()
    }, [])

    const togglePago = async (tipo) => {
        setUpdatingId(tipo.id)
        setError(null)
        try {
            await updateTipoDocumento(tipo.id, { requiere_pago: !tipo.requiere_pago })
            await load()
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudo actualizar el tipo')
        } finally {
            setUpdatingId(null)
        }
    }

    const handleCreate = async (event) => {
        event.preventDefault()
        if (!nuevoNombre.trim()) return

        setIsCreating(true)
        setError(null)
        try {
            await createTipoDocumento({
                nombre: nuevoNombre.trim(),
                requiere_pago: nuevoRequierePago,
                activo: true,
            })
            setNuevoNombre('')
            setNuevoRequierePago(false)
            await load()
        } catch (requestError) {
            setError(requestError.response?.data?.error ?? 'No se pudo crear el tipo')
        } finally {
            setIsCreating(false)
        }
    }

    return (
        <div className="rounded-lg border border-neutral-300 bg-white p-4">
            <h3 className="text-sm font-semibold text-slate-900">Pago por tipo de documento</h3>
            <p className="mt-1 text-xs text-neutral-500">
                Si está activo, el estudiante debe adjuntar comprobante al solicitar ese documento.
            </p>

            {error && (
                <p className="mt-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
                    {error}
                </p>
            )}

            {isLoading ? (
                <p className="mt-3 text-xs text-neutral-500">Cargando tipos...</p>
            ) : (
                <ul className="mt-3 divide-y divide-neutral-200">
                    {tipos.map((tipo) => (
                        <li key={tipo.id} className="flex items-center justify-between gap-3 py-2 text-sm">
                            <span className="font-medium text-slate-800">{tipo.nombre}</span>
                            <label className="inline-flex items-center gap-2 text-xs text-neutral-700">
                                <input
                                    type="checkbox"
                                    checked={Boolean(tipo.requiere_pago)}
                                    disabled={updatingId === tipo.id}
                                    onChange={() => togglePago(tipo)}
                                />
                                Requiere pago
                            </label>
                        </li>
                    ))}
                </ul>
            )}

            <form className="mt-4 flex flex-col gap-2 border-t border-neutral-200 pt-3 sm:flex-row sm:items-end" onSubmit={handleCreate}>
                <label className="flex flex-1 flex-col gap-1 text-xs text-neutral-700">
                    Nuevo tipo
                    <input
                        type="text"
                        value={nuevoNombre}
                        onChange={(event) => setNuevoNombre(event.target.value)}
                        placeholder="Ej. Constancia de egreso"
                        className="rounded-md border border-neutral-300 px-3 py-2 text-sm"
                        required
                    />
                </label>
                <label className="inline-flex items-center gap-2 pb-2 text-xs text-neutral-700">
                    <input
                        type="checkbox"
                        checked={nuevoRequierePago}
                        onChange={(event) => setNuevoRequierePago(event.target.checked)}
                    />
                    Requiere pago
                </label>
                <button type="submit" className="primary" disabled={isCreating}>
                    {isCreating ? 'Creando...' : 'Agregar'}
                </button>
            </form>
        </div>
    )
}
