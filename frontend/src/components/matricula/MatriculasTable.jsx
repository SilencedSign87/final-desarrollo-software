import MatriculaStatusBadge from './MatriculaStatusBadge'
import { resolveApiUrl } from '../../services/api'
import { getFichaDownloadUrl } from '../../services/matriculaService'

export default function MatriculasTable({ matriculas, emptyMessage, actions, showFicha = false }) {
    if (!matriculas?.length) {
        return (
            <p className="rounded-lg border border-dashed border-neutral-300 px-4 py-8 text-center text-sm text-neutral-500">
                {emptyMessage}
            </p>
        )
    }

    return (
        <div className="overflow-x-auto rounded-lg border border-neutral-300">
            <table className="min-w-full divide-y divide-neutral-200 text-sm">
                <thead className="bg-neutral-50">
                    <tr>
                        <th className="px-4 py-3 text-left font-medium text-neutral-600">ID</th>
                        <th className="px-4 py-3 text-left font-medium text-neutral-600">Estudiante</th>
                        <th className="px-4 py-3 text-left font-medium text-neutral-600">Periodo</th>
                        <th className="px-4 py-3 text-left font-medium text-neutral-600">Cursos</th>
                        <th className="px-4 py-3 text-left font-medium text-neutral-600">Estado</th>
                        <th className="px-4 py-3 text-left font-medium text-neutral-600">Comprobante</th>
                        {showFicha && (
                            <th className="px-4 py-3 text-left font-medium text-neutral-600">Ficha</th>
                        )}
                        {actions && (
                            <th className="px-4 py-3 text-left font-medium text-neutral-600">Acciones</th>
                        )}
                    </tr>
                </thead>
                <tbody className="divide-y divide-neutral-200 bg-white">
                    {matriculas.map((matricula) => {
                        const comprobanteHref = matricula.comprobante_url
                            ? resolveApiUrl(matricula.comprobante_url)
                            : null

                        return (
                            <tr key={matricula.id}>
                                <td className="px-4 py-3 text-neutral-900">{matricula.id}</td>
                                <td className="px-4 py-3 text-neutral-700">{matricula.estudiante_nombre ?? matricula.estudiante_id}</td>
                                <td className="px-4 py-3 text-neutral-700">{matricula.periodo_semestre ?? matricula.periodo_academico_id}</td>
                                <td className="px-4 py-3 text-neutral-700">
                                    {matricula.detalles?.length ? (
                                        <ul className="space-y-0.5">
                                            {matricula.detalles.map((detalle) => (
                                                <li key={detalle.id}>
                                                    {detalle.curso_nombre ?? 'Curso'}{' '}
                                                    <span className="text-neutral-400">
                                                        ({detalle.seccion_nombre ?? detalle.seccion_id})
                                                    </span>
                                                </li>
                                            ))}
                                        </ul>
                                    ) : (
                                        <span className="text-xs text-neutral-500">Sin cursos</span>
                                    )}
                                </td>
                                <td className="px-4 py-3">
                                    <MatriculaStatusBadge status={matricula.estado} />
                                </td>
                                <td className="px-4 py-3">
                                    {comprobanteHref ? (
                                        <a
                                            href={comprobanteHref}
                                            className="text-blue-700 hover:underline"
                                            target="_blank"
                                            rel="noreferrer"
                                        >
                                            Ver comprobante
                                        </a>
                                    ) : (
                                        <span className="text-xs text-neutral-500">No disponible</span>
                                    )}
                                </td>
                                {showFicha && (
                                    <td className="px-4 py-3">
                                        {matricula.estado === 'validada' ? (
                                            <a
                                                href={getFichaDownloadUrl(matricula.id)}
                                                className="text-blue-700 hover:underline"
                                                target="_blank"
                                                rel="noreferrer"
                                            >
                                                Descargar PDF
                                            </a>
                                        ) : (
                                            <span className="text-xs text-neutral-500">No disponible</span>
                                        )}
                                    </td>
                                )}
                                {actions && (
                                    <td className="px-4 py-3">{actions(matricula)}</td>
                                )}
                            </tr>
                        )
                    })}
                </tbody>
            </table>
        </div>
    )
}
