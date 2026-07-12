import { useEffect, useMemo, useState } from "react"
import { useQuery } from "../../hooks/useQuery"
import { PeriodoAcademicoService } from "../../services/periodoAcademicoService"
import { SeccionService } from "../../services/seccionService"
import { EvaluacionService } from "../../services/evaluacionService"
import { getCursos } from "../../services/cursos"
import Skeleton from "../../components/Skeleton"
import Table from "../../components/Table"
import { twMerge } from "tailwind-merge"

export default function DireccionNotas() {
    const query = useQuery("direccion_notas")
    const periodoAcademico = query.params.periodoAcademico || ""
    const curso = query.params.curso || ""
    const seccion = query.params.seccion || ""

    const [periodos, setPeriodos] = useState()
    const [cursos, setCursos] = useState()
    const [secciones, setSecciones] = useState()
    const [stats, setStats] = useState()

    const handleChange = (key) => (event) => {
        const value = event.target.value
        const record = { [key]: value }

        if (key === "periodoAcademico") {
            record.curso = ""
            record.seccion = ""
            setCursos(undefined)
            setSecciones(undefined)
            setStats(undefined)
        } else if (key === "curso") {
            record.seccion = ""
            setSecciones(undefined)
            setStats(undefined)
        } else if (key === "seccion") {
            setStats(undefined)
        }

        query.set(record)
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

    const handleLoadCursos = async () => {
        if (!periodoAcademico) return
        setCursos(undefined)
        const response = await PeriodoAcademicoService.getCursosByPeriodoAcademico(periodoAcademico)
        setCursos(response.data)
    }

    const handleLoadSecciones = async () => {
        if (!curso) return
        setSecciones(undefined)
        const response = await SeccionService.Search({ curso_id: curso })
        setSecciones(response.data)
    }

    const handleFetchStats = async () => {
        if (!periodoAcademico) return
        setStats(undefined)
        const response = await EvaluacionService.getEstadisticasDireccion({
            periodo_academico_id: periodoAcademico,
            curso_id: curso || undefined,
            seccion_id: seccion || undefined,
        })
        setStats(response.data)
    }

    useEffect(() => { handleLoadPeriodos() }, [])
    useEffect(() => { handleLoadCursos() }, [periodoAcademico])
    useEffect(() => { handleLoadSecciones() }, [curso])
    useEffect(() => { handleFetchStats() }, [periodoAcademico, curso, seccion])

    const { resumen = {}, detalle = [] } = stats ?? {}

    return (
        <>
            <div className="space-y-6">
                <h1 className="text-2xl font-bold">Estadísticas de Notas</h1>

                <div className="flex flex-wrap items-end gap-4">
                    <label className="flex flex-col items-start gap-1">
                        Periodo académico
                        {periodos === undefined ? (
                            <Skeleton className="w-40 h-9" />
                        ) : (
                            <select
                                value={periodoAcademico}
                                onChange={handleChange("periodoAcademico")}
                                className="w-full"
                            >
                                <option value="">--</option>
                                {periodos.map((p) => (
                                    <option key={p.id} value={p.id}>
                                        {p.semestre}
                                    </option>
                                ))}
                            </select>
                        )}
                    </label>

                    <label
                        className={`flex flex-col items-start gap-1 ${!periodoAcademico ? "hidden" : ""}`}
                    >
                        Curso
                        {cursos === undefined ? (
                            <Skeleton className="w-48 h-9" />
                        ) : (
                            <select
                                disabled={!periodoAcademico}
                                className="w-full"
                                value={curso}
                                onChange={handleChange("curso")}
                            >
                                <option value="">Todos</option>
                                {cursos.map((c) => (
                                    <option key={c.id} value={c.id}>
                                        {c.nombre}
                                    </option>
                                ))}
                            </select>
                        )}
                    </label>

                    <label
                        className={`flex flex-col items-start gap-1 ${!curso ? "hidden" : ""}`}
                    >
                        Sección
                        {secciones === undefined ? (
                            <Skeleton className="w-24 h-9" />
                        ) : (
                            <select
                                disabled={!curso}
                                className="w-full"
                                value={seccion}
                                onChange={handleChange("seccion")}
                            >
                                <option value="">Todas</option>
                                {secciones.map((s) => (
                                    <option key={s.id} value={s.id}>
                                        {s.nombre}
                                    </option>
                                ))}
                            </select>
                        )}
                    </label>
                </div>

                {stats === undefined ? (
                    periodoAcademico && <Skeleton className="w-full h-48" />
                ) : stats ? (
                    <>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <StatCard
                                label="Total estudiantes"
                                value={resumen.total_estudiantes}
                            />
                            <StatCard
                                label="Promedio general"
                                value={resumen.promedio_general ?? "—"}
                                className={
                                    resumen.promedio_general >= 10.5
                                        ? "text-green-600"
                                        : "text-red-600"
                                }
                            />
                            <StatCard
                                label="Aprobados"
                                value={`${resumen.aprobados} (${resumen.aprobados_porcentaje ?? "—"}%)`}
                                className="text-green-600"
                            />
                            <StatCard
                                label="Desaprobados"
                                value={`${resumen.desaprobados} (${resumen.desaprobados_porcentaje ?? "—"}%)`}
                                className="text-red-600"
                            />
                        </div>

                        <div className="space-y-2">
                            <h2 className="text-lg font-semibold">Distribución de notas</h2>
                            <div className="flex gap-1 h-8">
                                {Object.entries(resumen.distribucion ?? {}).map(
                                    ([rango, count]) => {
                                        const max =
                                            Math.max(
                                                ...Object.values(resumen.distribucion ?? {}),
                                                1,
                                            )
                                        return (
                                            <div
                                                key={rango}
                                                className="flex-1 flex flex-col items-center gap-1"
                                            >
                                                <div className="w-full bg-neutral-100 rounded-t relative h-full">
                                                    <div
                                                        className={twMerge(
                                                            "absolute bottom-0 w-full rounded-t transition-all",
                                                            rango === "00-05"
                                                                ? "bg-red-400"
                                                                : rango === "05-10"
                                                                  ? "bg-orange-400"
                                                                  : rango === "10-15"
                                                                    ? "bg-yellow-400"
                                                                    : "bg-green-400",
                                                        )}
                                                        style={{
                                                            height: `${(count / max) * 100}%`,
                                                        }}
                                                    />
                                                </div>
                                                <span className="text-xs text-neutral-500">
                                                    {rango}
                                                </span>
                                                <span className="text-xs font-medium">{count}</span>
                                            </div>
                                        )
                                    },
                                )}
                            </div>
                        </div>

                        {detalle.length > 0 && (
                            <div className="overflow-x-auto rounded-lg border border-neutral-300">
                                <Table>
                                    <Table.Header>
                                        <Table.Row>
                                            {seccion ? (
                                                <>
                                                    <Table.Cell sortable>Estudiante</Table.Cell>
                                                    <Table.Cell sortable>Promedio</Table.Cell>
                                                    <Table.Cell sortable>Estado</Table.Cell>
                                                </>
                                            ) : curso ? (
                                                <>
                                                    <Table.Cell sortable>Sección</Table.Cell>
                                                    <Table.Cell>Curso</Table.Cell>
                                                    <Table.Cell>Docente</Table.Cell>
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
                                                </>
                                            ) : (
                                                <>
                                                    <Table.Cell sortable>Curso</Table.Cell>
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
                                                </>
                                            )}
                                        </Table.Row>
                                    </Table.Header>
                                    <Table.Content>
                                        {detalle.map((row, i) => (
                                            <Table.Row key={i}>
                                                {"estudiante" in row ? (
                                                    <>
                                                        <Table.Cell value={row.estudiante}>
                                                            {row.estudiante}
                                                        </Table.Cell>
                                                        <Table.Cell
                                                            className="text-center"
                                                            value={row.promedio}
                                                        >
                                                            {row.promedio ?? "—"}
                                                        </Table.Cell>
                                                        <Table.Cell className="text-center">
                                                            <span
                                                                className={twMerge(
                                                                    "px-2 py-0.5 rounded text-xs font-medium",
                                                                    row.estado === "aprobado"
                                                                        ? "bg-green-100 text-green-700"
                                                                        : row.estado ===
                                                                            "desaprobado"
                                                                          ? "bg-red-100 text-red-700"
                                                                          : "bg-neutral-100 text-neutral-600",
                                                                )}
                                                            >
                                                                {row.estado}
                                                            </span>
                                                        </Table.Cell>
                                                    </>
                                                ) : "seccion" in row ? (
                                                    <>
                                                        <Table.Cell value={row.seccion}>
                                                            {row.seccion}
                                                        </Table.Cell>
                                                        <Table.Cell>{row.curso}</Table.Cell>
                                                        <Table.Cell>{row.docente}</Table.Cell>
                                                        <Table.Cell
                                                            className="text-center"
                                                            value={row.total_estudiantes}
                                                        >
                                                            {row.total_estudiantes}
                                                        </Table.Cell>
                                                        <Table.Cell
                                                            className="text-center font-medium"
                                                            value={row.promedio}
                                                        >
                                                            {row.promedio ?? "—"}
                                                        </Table.Cell>
                                                        <Table.Cell
                                                            className="text-center text-green-600"
                                                            value={row.aprobados}
                                                        >
                                                            {row.aprobados}
                                                        </Table.Cell>
                                                        <Table.Cell
                                                            className="text-center text-red-600"
                                                            value={row.desaprobados}
                                                        >
                                                            {row.desaprobados}
                                                        </Table.Cell>
                                                    </>
                                                ) : (
                                                    <>
                                                        <Table.Cell
                                                            className="font-medium"
                                                            value={row.curso}
                                                        >
                                                            {row.curso}
                                                        </Table.Cell>
                                                        <Table.Cell
                                                            className="text-center"
                                                            value={row.total_estudiantes}
                                                        >
                                                            {row.total_estudiantes}
                                                        </Table.Cell>
                                                        <Table.Cell
                                                            className="text-center font-medium"
                                                            value={row.promedio}
                                                        >
                                                            {row.promedio ?? "—"}
                                                        </Table.Cell>
                                                        <Table.Cell
                                                            className="text-center text-green-600"
                                                            value={row.aprobados}
                                                        >
                                                            {row.aprobados}
                                                        </Table.Cell>
                                                        <Table.Cell
                                                            className="text-center text-red-600"
                                                            value={row.desaprobados}
                                                        >
                                                            {row.desaprobados}
                                                        </Table.Cell>
                                                    </>
                                                )}
                                            </Table.Row>
                                        ))}
                                    </Table.Content>
                                </Table>
                            </div>
                        )}
                    </>
                ) : null}
            </div>
        </>
    )
}

function StatCard({ label, value, className }) {
    return (
        <div className="rounded-lg border border-neutral-300 bg-neutral-50 p-4">
            <p className="text-xs text-neutral-500 uppercase tracking-wider">{label}</p>
            <p className={twMerge("text-2xl font-bold mt-1", className)}>{value}</p>
        </div>
    )
}
