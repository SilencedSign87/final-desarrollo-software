export default function DocumentPagination({ meta, page, onPageChange, disabled = false }) {
    if (!meta || meta.pages <= 1) {
        return null
    }

    return (
        <div className="flex flex-wrap items-center justify-between gap-3 text-sm text-neutral-600">
            <p>
                Página {meta.page} de {meta.pages} · {meta.total} solicitudes
            </p>
            <div className="flex gap-2">
                <button
                    type="button"
                    className="secondary"
                    disabled={disabled || page <= 1}
                    onClick={() => onPageChange(page - 1)}
                >
                    Anterior
                </button>
                <button
                    type="button"
                    className="secondary"
                    disabled={disabled || page >= meta.pages}
                    onClick={() => onPageChange(page + 1)}
                >
                    Siguiente
                </button>
            </div>
        </div>
    )
}
