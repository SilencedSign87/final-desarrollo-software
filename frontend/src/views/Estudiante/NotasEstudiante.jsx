import { useEffect, useState } from "react"
import { useQuery } from "../../hooks/useQuery"
import { PeriodoAcademicoService } from "../../services/periodoAcademicoService"
import { EvaluacionService } from "../../services/evaluacionService"
import Spinner from "../../components/Spinner"
import Table from "../../components/Table"
import { BadgeCheck, Clock } from "lucide-react"

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
        const data = response.data
        setPeriodos(data)

        if (!periodo) {
            const activo = data.find((p) => p.estado === "activo")
            if (activo) query.set({ periodo: activo.id })
        }
    }
    const handleFetchNotas = async () => {
        if (!periodo) return
        setIsLoading(true)
        const response = await EvaluacionService.getMisNotas({ periodo_academico_id: periodo })
        setNotas(response.data)


        setIsLoading(false)
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
                                    <article key={nota.curso + nota.seccion} className="flex flex-col gap-2 mb-4 border border-neutral-300 rounded-lg max-w-3xl mx-auto">
                                        <header className="flex items-center justify-between p-4 border-b border-neutral-300">
                                            <h2 className="text-xl font-semibold">{nota.curso}</h2>
                                            <small>{nota.seccion}</small>
                                        </header>
                                        <legend className="text-sm font-medium text-neutral-600 px-4">Notas</legend>
                                        <div className="overflow-x-auto px-4">
                                            <Table>
                                                <Table.Header>
                                                    <Table.Row>
                                                        <Table.Cell>Nombre</Table.Cell>
                                                        <Table.Cell>Peso</Table.Cell>
                                                        <Table.Cell sortable>Nota</Table.Cell>
                                                    </Table.Row>
                                                </Table.Header>
                                                <Table.Content>
                                                    {
                                                        nota.evaluaciones.map((evaluacion) => (
                                                            <Table.Row key={evaluacion.nombre + evaluacion.peso}>
                                                                <Table.Cell>{evaluacion.nombre}</Table.Cell>
                                                                <Table.Cell>{evaluacion.peso}</Table.Cell>
                                                                <Table.Cell value={evaluacion.nota}>{evaluacion.nota}</Table.Cell>
                                                            </Table.Row>
                                                        ))
                                                    }
                                                </Table.Content>
                                            </Table>
                                        </div>
                                        <footer className="p-4 pt-1 pb-2 border-t text-sm border-neutral-300 flex items-center justify-between">
                                            <div className="px-4 py-3 text-neutral-800 font-semibold flex flex-col gap-1">
                                                Promedio
                                                {nota.is_validated ? (
                                                    <span className="inline-flex items-center gap-1 text-xs text-green-700">
                                                        <BadgeCheck size={14} />
                                                        Nota oficial
                                                    </span>
                                                ) : (
                                                    <span className="inline-flex items-center gap-1 text-xs text-amber-600">
                                                        <Clock size={14} />
                                                        Promedio calculado (no oficial)
                                                    </span>
                                                )}
                                            </div>
                                            <div className="px-4 py-3 text-neutral-800 font-semibold">
                                                {nota.promedio ?? nota.promedio_calculado ?? "--"}
                                            </div>
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
