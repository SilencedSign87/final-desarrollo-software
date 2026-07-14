const LIMA_TZ = 'America/Lima'

/**
 * Formatea una fecha a hora de Perú.
 * Si el backend ya envió texto legible (p. ej. "13/07/2026, 22:28:10"), se muestra tal cual.
 */
export const formatDateTime = (value) => {
    if (!value) return '—'
    if (typeof value === 'string' && /^\d{2}\/\d{2}\/\d{4}/.test(value)) {
        return value
    }

    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return '—'
    return date.toLocaleString('es-PE', { timeZone: LIMA_TZ })
}
