import { useEffect, useState } from 'react'
import { BookOpen } from 'lucide-react'
import Spinner from '../../components/spinner'
import { DocenteService } from '../../services/docenteService'

export default function CursosDocente() {
    const [secciones, setSecciones] = useState([])
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        let active = true

        DocenteService.Me()
            .then((response) => DocenteService.Secciones(response.data.id))
            .then((response) => {
                if (active) {
                    setSecciones(response.data ?? [])
                }
            })
            .catch((requestError) => {
                if (active) {
                    setError(requestError.response?.data?.error ?? 'No se pudieron cargar tus cursos')
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
                <h2 className="text-2xl font-semibold text-slate-900">Mis cursos</h2>
                <p className="mt-1 text-sm text-neutral-600">
                    Cursos y secciones que tienes asignados este periodo.
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
            ) : !secciones.length ? (
                <p className="rounded-lg border border-dashed border-neutral-300 px-4 py-8 text-center text-sm text-neutral-500">
                    No tienes cursos asignados este periodo.
                </p>
            ) : (
                <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                    {secciones.map((seccion) => (
                        <article key={seccion.id} className="rounded-lg border border-neutral-300 bg-neutral-50 p-5">
                            <div className="mb-2 flex items-center gap-2 text-neutral-500">
                                <BookOpen className="h-4 w-4" />
                                <span className="text-xs">{seccion.periodo_semestre}</span>
                            </div>
                            <p className="text-lg font-semibold text-slate-900">{seccion.curso_nombre}</p>
                            <p className="text-sm text-neutral-600">Sección {seccion.nombre}</p>
                        </article>
                    ))}
                </div>
            )}
        </section>
    )
}