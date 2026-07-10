import { useParams } from "react-router-dom"
import { useQuery } from "../../hooks/useQuery"
import { twMerge } from "tailwind-merge"
import { useEffect, useState } from "react"
import { PeriodoAcademicoService } from "../../services/periodoAcademicoService"
import { SeccionService } from "../../services/seccionService"
import { EvaluacionService } from "../../services/evaluacionService"
import Skeleton from "../../components/Skeleton"
import { Delete, Edit, Info, Plus, Trash } from "lucide-react"
import EditableText from "../../components/EditableText"
import Dialog from "../../components/Dialog"

export default function NotasDocente() {
    const query = useQuery('docente_notas')
    const periodoAcademico = query.params.periodoAcademico || ''
    const curso = query.params.curso || ''
    const seccion = query.params.seccion || ''

    const [periodosAcademicos, setPeriodosAcademicos] = useState()
    const [cursos, setCursos] = useState()
    const [secciones, setSecciones] = useState()
    const [notasSeccion, setNotaSeccion] = useState()

    const handleChange = (key) => (event) => {
        const value = event.target.value

        const record = { [key]: value }

        if (key === 'periodoAcademico') {
            record.curso = ''
            record.seccion = ''
            setCursos(undefined)
            setSecciones(undefined)
            setNotaSeccion(undefined)
        } else if (key === 'curso') {
            record.seccion = ''
            setSecciones(undefined)
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

    const handleFetchEstudiantes = async () => {
        if (!seccion) return
        setNotaSeccion(undefined)
        const response = await EvaluacionService.searchNotasPorSeccion({ seccion_id: seccion })
        setNotaSeccion(response.data)
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
            setCursos(undefined)
            setSecciones(undefined)
            setNotaSeccion(undefined)
            return
        }
        handleLoadCursos()
    }, [periodoAcademico])

    useEffect(() => {
        if (!curso) {
            setSecciones(undefined)
            setNotaSeccion(undefined)
            return
        }
        handleLoadSecciones()
    }, [curso])

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
                            Curso
                            {
                                cursos === undefined
                                    ? renderSkeleton()
                                    : (

                                        <select
                                            disabled={!periodoAcademico}
                                            className="w-full"
                                            value={curso}
                                            onChange={handleChange('curso')}>
                                            <option value=""> -- </option>
                                            {
                                                cursos.map((curso) => (
                                                    <option key={curso.id} value={curso.id}>{curso.nombre}</option>
                                                ))
                                            }
                                        </select>
                                    )
                            }
                        </label>
                        <label className={`flex flex-col items-start justify-center gap-1 ${!curso ? 'hidden' : ''}`} >
                            Sección
                            {
                                secciones === undefined
                                    ? renderSkeleton()
                                    : (
                                        <select
                                            disabled={!curso}
                                            className="w-full"
                                            value={seccion}
                                            onChange={handleChange('seccion')}>
                                            <option value=""> -- </option>
                                            {
                                                secciones.map((seccion) => (
                                                    <option key={seccion.id} value={seccion.id}>{seccion.nombre}</option>
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
                                            <table
                                                className={twMerge(
                                                    "min-w-fit w-full divide-y divide-neutral-200 text-sm",
                                                    !seccion && "hidden"
                                                )}
                                            >
                                                <thead className="bg-neutral-50">
                                                    <tr>
                                                        <th className="px-4 py-3 text-left font-medium text-neutral-600">Estudiante</th>
                                                        {
                                                            tipos_evaluacion.map((tipo) => (
                                                                <th key={tipo.id} className="px-4 py-3 text-left font-medium text-neutral-600">
                                                                    {tipo.nombre}
                                                                    <span className="block text-xs text-neutral-400 font-normal">
                                                                        {tipo.peso}
                                                                    </span>
                                                                </th>
                                                            ))
                                                        }
                                                        <th className="px-4 py-3 text-center font-medium text-neutral-600">Promedio</th>
                                                    </tr>
                                                </thead>
                                                <tbody className="divide-y divide-neutral-200 bg-white">
                                                    {
                                                        estudiantes.map((est) => (
                                                            <tr key={est.detalle_matricula_id}>
                                                                <td className="px-4 py-3 text-neutral-900 whitespace-nowrap">
                                                                    {est.estudiante_nombre}
                                                                </td>
                                                                {est.notas.map((n) => (
                                                                    <td key={n.tipo_evaluacion_id} className="px-4 py-3 text-center">
                                                                        {n.nota === null && n.evaluacion_id === null ? (
                                                                            <EditableText
                                                                                className="inline-flex justify-center"
                                                                                value="--"
                                                                                onChange={(newValue) =>
                                                                                    handleNotaChange(est.detalle_matricula_id, n, newValue)
                                                                                }
                                                                            />
                                                                        ) : (
                                                                            <EditableText
                                                                                className="inline-flex justify-center"
                                                                                value={n.nota}
                                                                                onChange={(newValue) =>
                                                                                    handleNotaChange(est.detalle_matricula_id, n, newValue)
                                                                                }
                                                                            />
                                                                        )}
                                                                    </td>
                                                                ))}
                                                                <td className="px-4 py-3 text-center font-medium text-neutral-900">
                                                                    {est.promedio_final ?? '--'}
                                                                </td>
                                                            </tr>
                                                        ))}
                                                    {estudiantes.length === 0 && (
                                                        <tr>
                                                            <td colSpan={tipos_evaluacion.length + 2} className="px-4 py-6 text-center text-neutral-500">
                                                                No hay estudiantes matriculados en esta sección.
                                                            </td>
                                                        </tr>
                                                    )}
                                                </tbody>
                                            </table>
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
            // Crear o actualizar cada item
            for (const item of items) {
                if (item._new) {
                    if (!item.nombre || !item.peso) {
                        continue // Skip if name or weight is empty
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
                            <div className="overflow-x-auto rounded-lg border border-neutral-300">
                                <table className="min-w-75 w-100 divide-y divide-neutral-200 text-sm">
                                    <thead>
                                        <tr>
                                            <th className="px-4 py-3 text-left font-medium text-neutral-600">Nombre</th>
                                            <th className="w-30 px-4 py-3 text-left font-medium text-neutral-600">Peso</th>
                                            <th className="w-12 px-4 py-3"></th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-neutral-200 bg-white">
                                        {items.map((item, i) => (
                                            <tr key={i}>
                                                <td className="px-4 py-2">
                                                    <input
                                                        className="w-full border border-neutral-300 rounded px-2 py-1 text-sm"
                                                        value={item.nombre}
                                                        onChange={(e) => handleChange(i, 'nombre', e.target.value)}
                                                    />
                                                </td>
                                                <td className="px-4 py-2">
                                                    <input
                                                        className="w-full border border-neutral-300 rounded px-2 py-1 text-sm text-right"
                                                        type="number"
                                                        min="0"
                                                        max="100"
                                                        value={item.peso}
                                                        onChange={(e) => handleChange(i, 'peso', e.target.value)}
                                                    />
                                                </td>
                                                <td className="px-4 py-2 text-center">
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
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
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