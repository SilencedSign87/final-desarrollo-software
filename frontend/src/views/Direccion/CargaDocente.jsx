import { useEffect, useState } from 'react'
import { GraduationCap } from 'lucide-react'
import Spinner from '../../components/spinner'
import { DocenteService } from '../../services/docenteService'

export default function DireccionCargaDocente() {
    const [carga, setCarga] = useState([])
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        let active = true

        DocenteService.CargaDocente()
            .then((response) => {
                if (active) {
                    setCarga(response.data ?? [])
                }
            })
            .catch((requestError) => {
                if (active) {
                    setError(requestError.response?.data?.error ?? 'No se pudo cargar la información de carga docente')
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

    return (
        <section className="space-y-6">
            <div>
                <h2 className="text-2xl font-semibold text-slate-900">Carga docente</h2>
                <p className="mt-1 text-sm text-neutral-600">
                    Número de secciones asignadas por cada docente en el periodo actual.
                </p>
            </div>

            {error && (
                <p className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                </p>
            )}

            <div className="rounded-lg border border-neutral-300 bg-neutral-50 p-4">
                <div className="mb-4 flex items-center gap-2 text-sm text-neutral-600">
                    <GraduationCap className="h-4 w-4" />
                    <span>Carga por docente</span>
                </div>

                {isLoading ? (
                    <div className="flex justify-center py-10">
                        <Spinner />
                    </div>
                ) : !carga.length ? (
                    <p className="rounded-lg border border-dashed border-neutral-300 px-4 py-8 text-center text-sm text-neutral-500">
                        No hay docentes registrados.
                    </p>
                ) : (
                    <div className="overflow-x-auto rounded-lg border border-neutral-300">
                        <table className="min-w-full divide-y divide-neutral-200 text-sm">
                            <thead className="bg-neutral-50">
                                <tr>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Docente</th>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Categoría</th>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Secciones asignadas</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-neutral-200 bg-white">
                                {carga.map((item) => (
                                    <tr key={item.docente_id}>
                                        <td className="px-4 py-3 text-neutral-900">{item.nombre_completo}</td>
                                        <td className="px-4 py-3 text-neutral-700 capitalize">{item.categoria}</td>
                                        <td className="px-4 py-3 text-neutral-700">{item.total_secciones}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </section>
    )
}