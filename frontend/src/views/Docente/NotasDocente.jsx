export default function NotasDocente() {
    return (
        <>
            <div className="grid grid-rows-[1fr_auto] gap-4">
                <form className="flex flex-wrap items-center justify-start p-4 gap-4">
                    <select>
                        <option value="">Seleccione una sección</option>
                    </select>
                    <select>
                        <option value="">Seleccione un curso</option>
                    </select>
                    <select>
                        <option value="">Seleccione un estudiante</option>
                    </select>
                </form>
                <div className="overflow-x-auto rounded-lg border border-neutral-300">
                    <table className="min-w-full divide-y divide-neutral-200 text-sm">
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