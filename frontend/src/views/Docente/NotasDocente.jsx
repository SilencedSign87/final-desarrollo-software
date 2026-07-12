import { useParams } from "react-router-dom"
import { useQuery } from "../../hooks/useQuery"
import { twMerge } from "tailwind-merge"
import { useEffect, useState } from "react"
import { PeriodoAcademicoService } from "../../services/periodoAcademicoService"
import { DocenteService } from "../../services/docenteService"
import { EvaluacionService } from "../../services/evaluacionService"
import Skeleton from "../../components/Skeleton"
import { Delete, Edit, Info, Plus, Trash } from "lucide-react"
import EditableText from "../../components/EditableText"
import Dialog from "../../components/Dialog"
import Table from "../../components/Table"

export default function NotasDocente() {
    const query = useQuery('docente_notas')
    const periodoAcademico = query.params.periodoAcademico || ''
    const seccion = query.params.seccion || ''

    const [periodosAcademicos, setPeriodosAcademicos] = useState()
    const [seccionesAsignadas, setSeccionesAsignadas] = useState()
    const [docenteId, setDocenteId] = useState()
    const [notasSeccion, setNotaSeccion] = useState()

    const handleChange = (key) => (event) => {
        const value = event.target.value

        const record = { [key]: value }

        if (key === 'periodoAcademico') {
            record.seccion = ''
            setSeccionesAsignadas(undefined)
            setNotaSeccion(undefined)
        } else if (key === 'seccion') {
            setNotaSeccion(undefined)
        }

        query.set(record)
    }

    const renderSkeleton = () => {
        return (<Skeleton className="w-20 h-9" />)
    }

    const handleLoadPeriodoAcademico = async () => {
        setPeriodosAcademicos(undefined)
        const response = await PeriodoAcademicoService.search()
        setPeriodosAcademicos(response.data)
    }

    const handleLoadSeccionesAsignadas = async () => {
        if (!periodoAcademico) return
        setSeccionesAsignadas(undefined)

        let id = docenteId
        if (!id) {
            const meResponse = await DocenteService.Me()
            id = meResponse.data.id
            setDocenteId(id)
        }

        const response = await DocenteService.Secciones(id, { periodo_academico_id: periodoAcademico })
        setSeccionesAsignadas(response.data)
    }

    const handleFetchEstudiantes = async () => {
        if (!seccion) return
        setNotaSeccion(undefined)
        const response = await EvaluacionService.searchNotasPorSeccion({ seccion_id: seccion })
        setNotaSeccion(response.data)
    }

    const handleVerifyNota = (raw) => {
        const parsed = parseFloat(raw)
        if (isNaN(parsed)) return raw
        return Math.min(20, Math.max(0, parsed)).toString()
    }

    const handleNotaChange = async (detalle_matricula_id, notaInfo, newValue) => {
        const nota = parseFloat(newValue)
        if (isNaN(nota)) return

        try {
            if (notaInfo.evaluacion_id) {
                await EvaluacionService.actualizarEvaluacion({
                    id: notaInfo.evaluacion_id,
                    nota
                })
            } else {
                await EvaluacionService.crearEvaluacion({
                    detalle_matricula_id,
                    tipo_evaluacion_id: notaInfo.tipo_evaluacion_id,
                    nota,
                })
            }

            await handleFetchEstudiantes()

        } catch (error) {
            console.error('Error al actualizar la nota:', error)
        }
    }

    useEffect(() => {
        handleLoadPeriodoAcademico()
    }, [])

    useEffect(() => {
        if (!periodoAcademico) {
            setSeccionesAsignadas(undefined)
            setNotaSeccion(undefined)
            return
        }
        handleLoadSeccionesAsignadas()
    }, [periodoAcademico])

    useEffect(() => {
        if (!seccion) {
            setNotaSeccion(undefined)
            return
        }
        handleFetchEstudiantes()
    }, [seccion])

    const { tipos_evaluacion = [], estudiantes = [] } = notasSeccion ?? {}

    return (
        <>
            <div className="grid grid-rows-[1fr_auto] gap-4">
                <form className="space-y-2">
                    <fieldset className="flex flex-wrap items-center justify-start pb-2 gap-6">

                        <label className="flex flex-col items-start justify-center gap-1">
                            Periodo académico
                            {
                                periodosAcademicos === undefined
                                    ? renderSkeleton()
                                    : (
                                        <select value={periodoAcademico} onChange={handleChange('periodoAcademico')} className="w-full">
                                            <option value=""> -- </option>
                                            {
                                                periodosAcademicos.map((periodo) => (
                                                    <option key={periodo.id} value={periodo.id}>{periodo.semestre}</option>
                                                ))
                                            }
                                        </select>
                                    )
                            }
                        </label>

                        <label className={`flex flex-col items-start justify-center gap-1 ${!periodoAcademico ? 'hidden' : ''}`} >
                            Curso - Sección
                            {
                                seccionesAsignadas === undefined
                                    ? renderSkeleton()
                                    : (
                                        <select
                                            disabled={!periodoAcademico}
                                            className="w-full"
                                            value={seccion}
                                            onChange={handleChange('seccion')}>
                                            <option value=""> -- </option>
                                            {
                                                seccionesAsignadas.map((sec) => (
                                                    <option key={sec.id} value={sec.id}>{sec.curso_nombre} - {sec.nombre}</option>
                                                ))
                                            }
                                        </select>
                                    )
                            }
                        </label>

                    </fieldset>
                </form>

                <div className="overflow-hidden">
                    {
                        notasSeccion && (
                            <div className="flex justify-end pb-4">
                                <EditNotasSchema
                                    tipos_evaluacion={tipos_evaluacion}
                                    seccion_id={seccion}
                                    onSave={handleFetchEstudiantes}
                                />
                            </div>
                        )
                    }

                    <div className="overflow-x-auto rounded-lg border border-neutral-300 w-full">
                        {
                            seccion
                                ? notasSeccion === undefined
                                    ? <Skeleton className="w-full h-48" />
                                    : (
                                        <>
                                            <Table>
                                                <Table.Header>
                                                    <Table.Row>
                                                        <Table.Cell sortable>Estudiante</Table.Cell>
                                                        {
                                                            tipos_evaluacion.map((tipo) => (
                                                                <Table.Cell key={tipo.id} sortable>
                                                                    <div className="flex flex-col items-center justify-start gap-1">
                                                                        {tipo.nombre}
                                                                        <span className="block text-xs text-neutral-400 font-normal">
                                                                            {tipo.peso}
                                                                        </span>
                                                                    </div>
                                                                </Table.Cell>
                                                            ))
                                                        }
                                                        <Table.Cell sortable>Promedio</Table.Cell>
                                                    </Table.Row>
                                                </Table.Header>
                                                <Table.Content>
                                                    {
                                                        estudiantes.map((est) => (
                                                            <Table.Row key={est.detalle_matricula_id}>
                                                                <Table.Cell value={est.estudiante_nombre} >{est.estudiante_nombre}</Table.Cell>
                                                                {est.notas.map((n) => (
                                                                    <Table.Cell key={n.tipo_evaluacion_id} className="text-center">
                                                                        {n.nota === null && n.evaluacion_id === null ? (
                                                                            <EditableText
                                                                                className="inline-flex justify-center"
                                                                                value="--"
                                                                                onVerification={handleVerifyNota}
                                                                                onChange={(newValue) =>
                                                                                    handleNotaChange(est.detalle_matricula_id, n, newValue)
                                                                                }
                                                                            />
                                                                        ) : (
                                                                            <EditableText
                                                                                className="inline-flex justify-center"
                                                                                value={n.nota}
                                                                                onVerification={handleVerifyNota}
                                                                                onChange={(newValue) =>
                                                                                    handleNotaChange(est.detalle_matricula_id, n, newValue)
                                                                                }
                                                                            />
                                                                        )}
                                                                    </Table.Cell>
                                                                ))}
                                                                <Table.Cell className="text-center font-medium">
                                                                    {est.promedio_final ?? '--'}
                                                                </Table.Cell>
                                                            </Table.Row>
                                                        ))
                                                    }
                                                    {
                                                        estudiantes.length === 0 && (
                                                            <Table.Row>
                                                                <Table.Cell colSpan={tipos_evaluacion.length + 2} className="text-center text-neutral-500">
                                                                    No hay estudiantes matriculados en esta sección.
                                                                </Table.Cell>
                                                            </Table.Row>
                                                        )
                                                    }
                                                </Table.Content>
                                            </Table>
                                        </>
                                    )
                                : (
                                    <div className="w-full px-8 py-6 bg-neutral-100 flex items-center justify-start gap-2 text-neutral-900">
                                        <Info size={20} />
                                        <p>
                                            Seleccione todas las opciones de filtro para ver la lista de estudiantes y sus notas.
                                        </p>
                                    </div>
                                )
                        }
                    </div>

                </div>
            </div>
        </>
    )
}

const EditNotasSchema = ({ tipos_evaluacion = [], seccion_id, onSave }) => {
    const [items, setItems] = useState(tipos_evaluacion)
    const [open, setOpen] = useState(false)

    useEffect(() => {
        if (open) setItems(tipos_evaluacion)
    }, [open, tipos_evaluacion])

    const handleAdd = () => {
        setItems([...items, { id: null, nombre: '', peso: 0, _new: true }])
    }

    const handleRemove = (index) => {
        setItems((prevItems) => {
            const updatedItems = [...prevItems]
            if (updatedItems[index]._new) {
                updatedItems.splice(index, 1)
            } else {
                updatedItems[index]._deleted = true
            }
            return updatedItems
        })
    }

    const handleRestore = (index) => {
        items[index]._deleted = false
        setItems([...items])
    }

    const handleChange = (index, field, value) => {
        const updated = [...items]
        updated[index] = { ...updated[index], [field]: value }
        setItems(updated)
    }

    const handleSave = async () => {
        try {
            for (const item of items) {
                if (item._new) {
                    if (!item.nombre || !item.peso) {
                        continue
                    }
                    await EvaluacionService.crearTipoEvaluacion({
                        seccion_id,
                        nombre: item.nombre,
                        peso: parseFloat(item.peso),
                    })
                } else if (item._deleted) {
                    await EvaluacionService.eliminarTipoEvaluacion({ id: item.id })
                } else {
                    await EvaluacionService.actualizarTipoEvaluacion({
                        id: item.id,
                        nombre: item.nombre,
                        peso: parseFloat(item.peso),
                    })
                }
            }
            setOpen(false)
            onSave?.()
        } catch (error) {
            console.error('Error al guardar estructura de notas:', error)
        }
    }


    return (
        <>
            <Dialog open={open} onOpenChange={setOpen}>
                <Dialog.Trigger className="primary flex items-center gap-2">
                    <Edit size={16} />
                    Editar estructura de notas
                </Dialog.Trigger>
                <Dialog.Surface>
                    <Dialog.Header>
                        <h2>Editar estructura de notas</h2>
                    </Dialog.Header>
                    <Dialog.Content>
                        <div className="w-full">
                            <Table>
                                <Table.Header>
                                    <Table.Row>
                                        <Table.Cell>Nombre</Table.Cell>
                                        <Table.Cell>Peso</Table.Cell>
                                        <Table.Cell></Table.Cell>
                                    </Table.Row>
                                </Table.Header>
                                <Table.Content>
                                    {items.map((item, i) => (
                                        <Table.Row key={i}>
                                            <Table.Cell>
                                                <input
                                                    className="w-full border border-neutral-300 rounded px-2 py-1 text-sm"
                                                    value={item.nombre}
                                                    onChange={(e) => handleChange(i, 'nombre', e.target.value)}
                                                />
                                            </Table.Cell>
                                            <Table.Cell>
                                                <input
                                                    className="w-full border border-neutral-300 rounded px-2 py-1 text-sm text-right"
                                                    type="number"
                                                    min="0"
                                                    max="100"
                                                    value={item.peso}
                                                    onChange={(e) => handleChange(i, 'peso', e.target.value)}
                                                />
                                            </Table.Cell>
                                            <Table.Cell className="text-center">
                                                {
                                                    item._deleted
                                                        ? (
                                                            <button
                                                                className="text-green-500 hover:text-green-700 text-sm"
                                                                onClick={() => handleRestore(i)}
                                                            >
                                                                Restaurar
                                                            </button>
                                                        ) :
                                                        (

                                                            <button
                                                                className="text-red-500 hover:text-red-700 text-sm"
                                                                onClick={() => handleRemove(i)}
                                                            >
                                                                Eliminar
                                                            </button>
                                                        )
                                                }
                                            </Table.Cell>
                                        </Table.Row>
                                    ))}
                                </Table.Content>
                            </Table>
                            <button
                                className="secondary mt-2 px-1.5 py-1 text-sm font-light flex items-center justify-start gap-2"
                                onClick={handleAdd}
                            >
                                <Plus size={16} />
                                Agregar evaluación
                            </button>
                        </div>
                    </Dialog.Content>
                    <Dialog.Footer>
                        <Dialog.Trigger className="subtle">
                            Cancelar
                        </Dialog.Trigger>
                        <button className="primary" onClick={handleSave}>
                            Guardar cambios
                        </button>
                    </Dialog.Footer>
                </Dialog.Surface>
            </Dialog>
        </>
    )
}