import { useParams } from "react-router-dom"
import { useQuery } from "../../hooks/useQuery"
import { twMerge } from "tailwind-merge"
import { useEffect, useState } from "react"
import { PeriodoAcademicoService } from "../../services/periodoAcademicoService"
import { SeccionService } from "../../services/seccionService"
import { EvaluacionService } from "../../services/evaluacionService"

export default function NotasDocente() {
    const query = useQuery('docente_notas')
    const periodoAcademico = query.params.periodoAcademico || ''
    const curso = query.params.curso || ''
    const seccion = query.params.seccion || ''
    const tipoEvaluacion = query.params.tipoEvaluacion || ''

    const [periodosAcademicos, setPeriodosAcademicos] = useState([])
    const [cursos, setCursos] = useState([])
    const [secciones, setSecciones] = useState([])

    const handleChange = (key) => (event) => {
        query.set(key, event.target.value)
    }

    const handleLoadPeriodoAcademico = async() => {
        const response = await PeriodoAcademicoService.search()
        setPeriodosAcademicos(response.data)
    }

    const handleLoadCursos = async() => {
        if (!periodoAcademico) return

        const response = await PeriodoAcademicoService.getCursosByPeriodoAcademico(periodoAcademico)
        setCursos(response.data)
    }

    const handleLoadSecciones = async() => {
        const response = await SeccionService.Search({
            curso_id: curso,
        })
        setSecciones(response.data)
    }

    const handleTipoEvaluaciones = async() => {
        const response = await EvaluacionService.searchTipoEvaluaciones({
            
        })
    }

    useEffect(() => {
        handleLoadPeriodoAcademico()
    }, [])

    useEffect(() => {
        handleLoadCursos()
    }, [periodoAcademico])

    useEffect(() => {
        handleLoadSecciones()
    }, [curso])

    return (
        <>
            <div className="grid grid-rows-[1fr_auto] gap-4">
                <form className="space-y-2">
                    <fieldset className="flex flex-wrap items-center justify-start pb-2 gap-4">
                        <select value={periodoAcademico} onChange={handleChange('periodoAcademico')}>
                            <option value="">-- Seleccione un período académico -- </option>
                            {
                                periodosAcademicos.map((periodo) => (
                                    <option key={periodo.id} value={periodo.id}>{periodo.semestre}</option>
                                ))
                            }
                        </select>
                        <select
                            disabled={!periodoAcademico}
                            className="disabled:hidden"
                            value={curso}
                            onChange={handleChange('curso')}>
                            <option value="">-- Seleccione un curso --</option>
                            {
                                cursos.map((curso) => (
                                    <option key={curso.id} value={curso.id}>{curso.nombre}</option>
                                ))
                            }
                        </select>
                        <select
                            disabled={!curso}
                            className="disabled:hidden"
                            value={seccion}
                            onChange={handleChange('seccion')}>
                            <option value="">-- Seleccione una sección --</option>
                            {
                                secciones.map((seccion) => (
                                    <option key={seccion.id} value={seccion.id}>{seccion.nombre}</option>
                                ))
                            }
                        </select>
                        <select
                            disabled={!seccion}
                            className="disabled:hidden"
                            value={tipoEvaluacion}
                            onChange={handleChange('tipoEvaluacion')}>
                            <option value="">-- Seleccione un tipo de evaluación --</option>
                        </select>
                    </fieldset>
                </form>
                <div className="overflow-x-auto rounded-lg border border-neutral-300">
                    <table
                        className={twMerge(
                            "min-w-full divide-y divide-neutral-200 text-sm",
                            !tipoEvaluacion && "hidden"
                        )}
                    >
                        <thead className="bg-neutral-50">
                            <tr>
                                <th className="px-4 py-3 text-left font-medium text-neutral-600">Estudiante</th>
                                <th className="px-4 py-3 text-left font-medium text-neutral-600">Nota</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-neutral-200 bg-white">
                            <tr>
                                <td className="px-4 py-3 text-neutral-900">John Doe</td>
                                <td className="px-4 py-3 text-neutral-600">85</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

            </div>
        </>
    )
}