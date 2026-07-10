import { useEffect, useState } from "react"
import { useQuery } from "../../hooks/useQuery"
import { PeriodoAcademicoService } from "../../services/periodoAcademicoService"
import { EvaluacionService } from "../../services/evaluacionService"
import Spinner from "../../components/Spinner"

export default function NotasEstudiante() {
    const query = useQuery()

    const [periodos, setPeriodos] = useState([])
    const [isLoading, setIsLoading] = useState(false)
    const [notas, setNotas] = useState([])


    const periodo = query.get('periodo') || ''

    const handleChange = (key) => (event) => {
        const value = event.target.value

        const record = { [key]: value }

        if (value === '') {
            setNotas([])
        }

        query.set(record)
    }

    const handleFetchPeriodosMatriculados = async () => {
        const response = await PeriodoAcademicoService.getPeriodosMatriculados()
        setPeriodos(response.data)
    }
    const handleFetchNotas = async () => {
        if (!periodo) return
        setIsLoading(true)
        const response = await EvaluacionService.getMisNotas({ periodo_academico_id: periodo })
        setNotas(response.data)


        setIsLoading(false)
    }

    const CalcUnofficialPromedio = (nota) => {
        if (!nota.evaluaciones || nota.evaluaciones.length === 0) {
            return 0
        }
        let totalPeso = 0
        let totalNota = 0
        for (const evaluacion of nota.evaluaciones) {
            totalPeso += evaluacion.peso
            totalNota += evaluacion.nota * evaluacion.peso
        }
        return totalPeso > 0 ? (totalNota / totalPeso).toFixed(2) : 0
    }

    useEffect(() => {
        handleFetchPeriodosMatriculados()
    }, [])

    useEffect(() => {
        if (!periodo || periodo === '') return
        handleFetchNotas()
    }, [periodo])



    return (
        <>
            <div className="grid grid-cols-1 grid-rows-[auto_1fr]">
                <article >
                    <div className="flex flex-wrap items-center justify-start pb-2 gap-6">
                        <label className="flex flex-col items-start justify-center gap-1">
                            Periodo académico:
                            <select value={periodo} onChange={handleChange('periodo')}>
                                <option value="">--</option>
                                {periodos.map((p) => (
                                    <option key={p.id} value={p.id}>
                                        {p.semestre}
                                    </option>
                                ))}
                            </select>
                        </label>
                    </div>
                </article>
                <div className="overflow-hidden">
                    {
                        isLoading
                            ? <div className="flex flex-col items-center justify-center">
                                <Spinner />
                                <p className="text-neutral-500">Cargando notas...</p>
                            </div>
                            :

                            notas.length > 0
                                ? notas.map((nota) => (
                                    <article key={nota.curso + nota.seccion} className="flex flex-col gap-2 mb-4 border border-neutral-300 rounded-lg shadow-sm max-w-3xl mx-auto">
                                        <header className="flex items-center justify-between p-4 bg-neutral-100">
                                            <h2 className="text-xl font-semibold">{nota.curso}</h2>
                                            <small>{nota.seccion}</small>
                                        </header>
                                        <legend className="text-sm font-medium text-neutral-600 px-4">Notas</legend>
                                        <div className="overflow-x-auto px-4 pb-4">
                                            <table className="min-w-100 w-full divide-y divide-neutral-200 text-sm">
                                                <thead className="bg-neutral-50">
                                                    <tr>
                                                        <th className="px-4 py-3 text-left font-medium text-neutral-600">Nombre</th>
                                                        <th className="w-20 px-4 py-3 text-left font-medium text-neutral-600">Peso</th>
                                                        <th className="w-20 px-4 py-3 text-left font-medium text-neutral-600">Nota</th>
                                                    </tr>
                                                </thead>
                                                <tbody className="divide-y divide-neutral-200 bg-white">
                                                    {
                                                        nota.evaluaciones.map((evaluacion) => (
                                                            <tr key={evaluacion.nombre + evaluacion.peso}>
                                                                <td className="px-4 py-3">{evaluacion.nombre}</td>
                                                                <td className="px-4 py-3">{evaluacion.peso}</td>
                                                                <td className="px-4 py-3">{evaluacion.nota}</td>
                                                            </tr>
                                                        ))
                                                    }
                                                </tbody>
                                            </table>
                                        </div>
                                        <footer className="pl-4 pr-6 pt-2 pb-3 border-t text-sm border-neutral-300 flex items-center justify-between">
                                            <div className="px-4 py-3 text-neutral-800 font-semibold" colSpan={2}>
                                                Promedio
                                                {
                                                    !nota.promedio && <span className="text-neutral-400 ml-4" title="La nota no ha sido revisada aún">(no oficial)</span>
                                                }
                                            </div>
                                            <div className="px-4 py-3 text-neutral-800 font-semibold">{nota.promedio ?? CalcUnofficialPromedio(nota)}</div>
                                        </footer>
                                    </article>
                                ))
                                : <p className="text-center text-neutral-500">No hay notas disponibles</p>
                    }
                </div>
            </div>
        </>
    )
}