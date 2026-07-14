import { useEffect, useState } from 'react'
import { ClipboardCheck } from 'lucide-react'
import Spinner from '../../components/Spinner'
import { getPlanesEstudio, getCumplimientoPlan } from '../../services/cursos'
import { PeriodoAcademicoService } from '../../services/periodoAcademicoService'

const ESTADO_LABEL = {
    cumple: { text: 'Cumple', className: 'bg-green-100 text-green-800' },
    sin_docente: { text: 'Sin docente asignado', className: 'bg-amber-100 text-amber-800' },
    sin_seccion: { text: 'Sin sección abierta', className: 'bg-red-100 text-red-800' },
}

export default function CumplimientoPlan() {
    const [planes, setPlanes] = useState([])
    const [periodos, setPeriodos] = useState([])
    const [planId, setPlanId] = useState('')
    const [periodoId, setPeriodoId] = useState('')
    const [reporte, setReporte] = useState(null)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState(null)

    useEffect(() => {
        Promise.all([getPlanesEstudio(), PeriodoAcademicoService.search()]).then(([planesRes, periodosRes]) => {
            const listaPlanes = planesRes.data ?? []
            const listaPeriodos = periodosRes.data ?? []
            setPlanes(listaPlanes)
            setPeriodos(listaPeriodos)
            if (listaPlanes[0]) setPlanId(String(listaPlanes[0].id))
            const activo = listaPeriodos.find((p) => p.estado === 'activo')
            setPeriodoId(activo ? String(activo.id) : '')
        })
    }, [])

    useEffect(() => {
        if (!planId) return
        let active = true
        setIsLoading(true)
        setError(null)

        getCumplimientoPlan(Number(planId), periodoId ? Number(periodoId) : undefined)
            .then((response) => {
                if (active) setReporte(response.data)
            })
            .catch((requestError) => {
                if (active) {
                    setError(requestError.response?.data?.error ?? 'No se pudo cargar el cumplimiento del plan')
                    setReporte(null)
                }
            })
            .finally(() => {
                if (active) setIsLoading(false)
            })

        return () => {
            active = false
        }
    }, [planId, periodoId])

    return (
        <section className="space-y-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
                <div>
                    <h2 className="text-2xl font-semibold text-slate-900">Cumplimiento del plan de estudios</h2>
                    <p className="mt-1 text-sm text-neutral-600">
                        Qué cursos del plan no tienen sección abierta o docente asignado en el periodo.
                    </p>
                </div>
                <div className="flex gap-3">
                    <label className="flex flex-col gap-1 text-sm">
                        Plan de estudios
                        <select value={planId} onChange={(e) => setPlanId(e.target.value)}>
                            {planes.map((p) => (
                                <option key={p.id} value={p.id}>
                                    {p.especialidad_nombre} — v{p.version} ({p.anio})
                                </option>
                            ))}
                        </select>
                    </label>
                    <label className="flex flex-col gap-1 text-sm">
                        Periodo académico
                        <select value={periodoId} onChange={(e) => setPeriodoId(e.target.value)}>
                            {periodos.map((p) => (
                                <option key={p.id} value={p.id}>
                                    {p.semestre} {p.estado === 'activo' ? '(activo)' : ''}
                                </option>
                            ))}
                        </select>
                    </label>
                </div>
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
            ) : reporte ? (
                <>
                    <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                        <div className="rounded-lg border border-neutral-300 bg-white p-4">
                            <p className="text-xs text-neutral-500">Total cursos</p>
                            <p className="text-2xl font-semibold text-slate-900">{reporte.resumen.total_cursos}</p>
                        </div>
                        <div className="rounded-lg border border-green-200 bg-green-50 p-4">
                            <p className="text-xs text-green-700">Cumple</p>
                            <p className="text-2xl font-semibold text-green-800">{reporte.resumen.cumple}</p>
                        </div>
                        <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
                            <p className="text-xs text-amber-700">Sin docente</p>
                            <p className="text-2xl font-semibold text-amber-800">{reporte.resumen.sin_docente}</p>
                        </div>
                        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
                            <p className="text-xs text-red-700">Sin sección</p>
                            <p className="text-2xl font-semibold text-red-800">{reporte.resumen.sin_seccion}</p>
                        </div>
                    </div>

                    <div className="overflow-x-auto rounded-lg border border-neutral-300">
                        <table className="min-w-full divide-y divide-neutral-200 text-sm">
                            <thead className="bg-neutral-50">
                                <tr>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Semestre</th>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Curso</th>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Secciones</th>
                                    <th className="px-4 py-3 text-left font-medium text-neutral-600">Estado</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-neutral-200 bg-white">
                                {reporte.cursos.map((c) => (
                                    <tr key={c.curso_id}>
                                        <td className="px-4 py-3 text-neutral-700">{c.semestre_num}</td>
                                        <td className="px-4 py-3 text-neutral-900">
                                            <div className="flex items-center gap-2">
                                                <ClipboardCheck className="h-4 w-4 text-neutral-400" />
                                                {c.curso_nombre}
                                            </div>
                                        </td>
                                        <td className="px-4 py-3 text-neutral-700">{c.total_secciones}</td>
                                        <td className="px-4 py-3">
                                            <span className={`rounded-full px-2 py-1 text-xs font-medium ${ESTADO_LABEL[c.estado].className}`}>
                                                {ESTADO_LABEL[c.estado].text}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </>
            ) : (
                <p className="rounded-lg border border-dashed border-neutral-300 px-4 py-8 text-center text-sm text-neutral-500">
                    Selecciona un plan de estudios.
                </p>
            )}
        </section>
    )
}