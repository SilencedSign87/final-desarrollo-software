import { useEffect, useState } from "react"
import { useQuery } from "../../hooks/useQuery"
import { PeriodoAcademicoService } from "../../services/periodoAcademicoService"
import { EvaluacionService } from "../../services/evaluacionService"
import Skeleton from "../../components/Skeleton"
import Table from "../../components/Table"
import { twMerge } from "tailwind-merge"

export default function DireccionRecordAcademico() {
    const query = useQuery("direccion_record_academico")
    const periodoAcademico = query.params.periodoAcademico || ""

    const [periodos, setPeriodos] = useState()
    const [data, setData] = useState()

    const handleChange = (key) => (event) => {
        query.set({ [key]: event.target.value })
    }

    const handleLoadPeriodos = async () => {
        setPeriodos(undefined)
        const response = await PeriodoAcademicoService.search()
        const data = response.data
        setPeriodos(data)

        if (!periodoAcademico) {
            const activo = data.find((p) => p.estado === "activo")
            if (activo) query.set({ periodoAcademico: activo.id })
        }
    }

    const handleFetchStats = async () => {
        if (!periodoAcademico) return
        setData(undefined)
        const response = await EvaluacionService.getRecordAcademicoDireccion({
            periodo_academico_id: periodoAcademico,
        })
        setData(response.data)
    }

    useEffect(() => { handleLoadPeriodos() }, [])
    useEffect(() => { handleFetchStats() }, [periodoAcademico])

    return (
        <>
            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <h1 className="text-2xl font-bold">Análisis de Record Académico</h1>

                    {periodos === undefined ? (
                        <Skeleton className="w-40 h-9" />
                    ) : (
                        <select
                            value={periodoAcademico}
                            onChange={handleChange("periodoAcademico")}
                            className="w-48"
                        >
                            <option value="">--</option>
                            {periodos.map((p) => (
                                <option key={p.id} value={p.id}>
                                    {p.semestre}
                                </option>
                            ))}
                        </select>
                    )}
                </div>

                {data === undefined ? (
                    periodoAcademico && <Skeleton className="w-full h-48" />
                ) : (
                    <div className="space-y-8">
                        {data.cursos.map((curso) => (
                            <CursoSection key={curso.curso_id} curso={curso} />
                        ))}
                        {data.cursos.length === 0 && (
                            <div className="w-full px-8 py-6 bg-neutral-100 rounded-lg text-neutral-500 text-center">
                                No hay cursos registrados en este periodo académico.
                            </div>
                        )}
                    </div>
                )}
            </div>
        </>
    )
}

function CursoSection({ curso }) {
    return (
        <div className="rounded-lg border border-neutral-300 overflow-hidden">
            <div className="bg-neutral-50 px-5 py-3 border-b border-neutral-300 flex items-center justify-between">
                <div>
                    <span className="text-lg font-bold">{curso.curso}</span>
                    <span className="ml-2 text-sm text-neutral-500">
                        Semestre {curso.semestre_num}
                    </span>
                </div>
                <div className="flex items-center gap-6 text-sm">
                    <span className="text-neutral-500">
                        Total: <strong>{curso.total_estudiantes}</strong>
                    </span>
                    <span
                        className={twMerge(
                            "font-semibold",
                            curso.promedio >= 10.5 ? "text-green-600" : "text-red-600",
                        )}
                    >
                        Prom: {curso.promedio ?? "—"}
                    </span>
                </div>
            </div>
            <div className="overflow-x-auto">
                <Table>
                    <Table.Header>
                        <Table.Row>
                            <Table.Cell sortable>Sección</Table.Cell>
                            <Table.Cell sortable>Docente</Table.Cell>
                            <Table.Cell sortable className="text-center">
                                Estudiantes
                            </Table.Cell>
                            <Table.Cell sortable className="text-center">
                                Promedio
                            </Table.Cell>
                            <Table.Cell sortable className="text-center">
                                Aprobados
                            </Table.Cell>
                            <Table.Cell sortable className="text-center">
                                Desaprobados
                            </Table.Cell>
                            <Table.Cell sortable className="text-center">
                                En curso
                            </Table.Cell>
                        </Table.Row>
                    </Table.Header>
                    <Table.Content>
                        {curso.secciones.map((sec) => (
                            <Table.Row key={sec.seccion_id}>
                                <Table.Cell className="font-medium" value={sec.seccion}>
                                    {sec.seccion}
                                </Table.Cell>
                                <Table.Cell value={sec.docente}>{sec.docente}</Table.Cell>
                                <Table.Cell className="text-center" value={sec.total_estudiantes}>
                                    {sec.total_estudiantes}
                                </Table.Cell>
                                <Table.Cell
                                    className={twMerge(
                                        "text-center font-medium",
                                        sec.promedio >= 10.5
                                            ? "text-green-600"
                                            : sec.promedio !== null
                                              ? "text-red-600"
                                              : "",
                                    )}
                                    value={sec.promedio}
                                >
                                    {sec.promedio ?? "—"}
                                </Table.Cell>
                                <Table.Cell
                                    className="text-center text-green-600"
                                    value={sec.aprobados}
                                >
                                    {sec.aprobados}
                                </Table.Cell>
                                <Table.Cell
                                    className="text-center text-red-600"
                                    value={sec.desaprobados}
                                >
                                    {sec.desaprobados}
                                </Table.Cell>
                                <Table.Cell
                                    className="text-center text-amber-600"
                                    value={sec.en_curso}
                                >
                                    {sec.en_curso}
                                </Table.Cell>
                            </Table.Row>
                        ))}
                    </Table.Content>
                </Table>
            </div>
        </div>
    )
}
