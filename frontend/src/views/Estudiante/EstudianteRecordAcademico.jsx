import { useEffect, useMemo, useState } from "react"
import { EvaluacionService } from "../../services/evaluacionService"
import Skeleton from "../../components/Skeleton"
import Table from "../../components/Table"

export default function EstudianteRecordAcademico() {
    const [record, setRecord] = useState()

    useEffect(() => {
        (async () => {
            setRecord(undefined)
            try {
                const response = await EvaluacionService.getRecordAcademico()
                setRecord(response.data)
            } catch (error) {
                console.error("Error al cargar record académico:", error)
                setRecord([])
            }
        })()
    }, [])

    const rows = useMemo(() => {
        if (!record) return []
        const flat = []
        for (const periodo of record) {
            for (const curso of periodo.cursos) {
                flat.push({ ...curso, periodo: periodo.periodo, periodo_id: periodo.periodo_id })
            }
        }
        return flat
    }, [record])

    const semestreGroups = useMemo(() => {
        const groups = []
        for (let i = 0; i < rows.length; i++) {
            if (i === 0 || rows[i].semestre_num !== rows[i - 1].semestre_num) {
                groups.push({ start: i, count: 1 })
            } else {
                groups[groups.length - 1].count++
            }
        }
        const map = {}
        for (const g of groups) {
            map[g.start] = g.count
        }
        return map
    }, [rows])

    return (
        <>
            <section className="space-y-6">
                <h1 className="text-2xl font-bold">Record Académico</h1>

                {
                    record === undefined ? (
                        <Skeleton className="w-full h-48" />
                    ) : rows.length === 0 ? (
                        <div className="w-full px-8 py-6 bg-neutral-100 rounded-lg text-neutral-500 text-center">
                            No hay registro de notas.
                        </div>
                    ) : (
                        <div className="overflow-x-auto rounded-lg border border-neutral-300">
                            <Table>
                                <Table.Header>
                                    <Table.Row>
                                        <Table.Cell className="text-center">Semestre</Table.Cell>
                                        <Table.Cell>Curso</Table.Cell>
                                        <Table.Cell>Prerrequisitos</Table.Cell>
                                        <Table.Cell className="text-center">Promedio</Table.Cell>
                                    </Table.Row>
                                </Table.Header>
                                <Table.Content>
                                    {rows.map((row, i) => (
                                        <Table.Row key={`${row.periodo_id}-${row.nombre}`}>
                                            {semestreGroups[i] ? (
                                                <Table.Cell
                                                    className="text-center align-middle text-lg font-bold"
                                                    rowSpan={semestreGroups[i]}
                                                >
                                                    {row.semestre_num}
                                                </Table.Cell>
                                            ) : null}
                                            <Table.Cell className="font-medium">{row.nombre}</Table.Cell>
                                            <Table.Cell className="text-neutral-500">
                                                {row.prerequisitos.length > 0 ? row.prerequisitos.join(", ") : "—"}
                                            </Table.Cell>
                                            <Table.Cell className="text-center">
                                                {row.promedio ?? "—"}
                                            </Table.Cell>
                                        </Table.Row>
                                    ))}
                                </Table.Content>
                            </Table>
                        </div>
                    )
                }
            </section>
        </>
    )
}