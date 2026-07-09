const LABELS = {
    pendiente: 'Pendientes',
    validada: 'Validadas',
    rechazada: 'Rechazadas',
}

export default function MatriculaSummaryCards({ summary }) {
    const estados = ['pendiente', 'validada', 'rechazada']
    const total = Object.values(summary).reduce((acc, val) => acc + val, 0)

    const items = [
        { label: 'Total de matrículas', value: total },
        ...estados.map((estado) => ({
            label: LABELS[estado],
            value: summary[estado] ?? 0,
        })),
    ]

    return (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {items.map((item) => (
                <article
                    key={item.label}
                    className="rounded-lg border border-neutral-300 bg-neutral-50 p-5"
                >
                    <p className="text-sm text-neutral-600">{item.label}</p>
                    <p className="mt-2 text-3xl font-semibold text-slate-900">{item.value}</p>
                </article>
            ))}
        </div>
    )
}