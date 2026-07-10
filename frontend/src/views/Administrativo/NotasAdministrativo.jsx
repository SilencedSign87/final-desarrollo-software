import { useQuery } from "../../hooks/useQuery"
import { twMerge } from "tailwind-merge"
import { useEffect, useState } from "react"
import { PeriodoAcademicoService } from "../../services/periodoAcademicoService"
import { SeccionService } from "../../services/seccionService"
import { EvaluacionService } from "../../services/evaluacionService"
import Skeleton from "../../components/Skeleton"
import { Check, Info } from "lucide-react"
import EditableText from "../../components/EditableText"

export default function NotasAdministrativo() {
    const query = useQuery('administrativo_notas')
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

    const handleValidarPromedio = async (detalle_matricula_id) => {
        try {
            await EvaluacionService.validarPromedio({ seccion_id: seccion, detalle_matricula_id })
            await handleFetchEstudiantes()
        } catch (error) {
            console.error('Error al validar promedio:', error)
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
                                                        <th className="px-4 py-3 text-center font-medium text-neutral-600">Acción</th>
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
                                                                <td className="px-4 py-3 text-center">
                                                                    <button
                                                                        className="primary inline-flex items-center gap-1.5 text-xs"
                                                                        onClick={() => handleValidarPromedio(est.detalle_matricula_id)}
                                                                    >
                                                                        <Check size={18} />
                                                                        {
                                                                            (est.promedio_final !== null && est.promedio_final!== '') ? 'Revalidar' : 'Validar'
                                                                        }
                                                                    </button>
                                                                </td>
                                                            </tr>
                                                        ))}
                                                    {estudiantes.length === 0 && (
                                                        <tr>
                                                            <td colSpan={tipos_evaluacion.length + 3} className="px-4 py-6 text-center text-neutral-500">
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
