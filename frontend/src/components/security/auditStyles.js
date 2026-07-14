export const ACTION_LABELS = {
    login: 'Login',
    login_fallido: 'Login fallido',
    logout: 'Logout',
    cambio_rol: 'Cambio de rol',
    crear_usuario: 'Crear usuario',
    autorizar_documento: 'Autorizar documento',
    rechazar_documento: 'Rechazar documento',
    emitir_documento: 'Emitir documento',
}

export const ACTION_STYLES = {
    login: {
        badge: 'bg-sky-100 text-sky-800 ring-sky-200',
        row: 'bg-sky-50/40',
        dot: 'bg-sky-500',
    },
    login_fallido: {
        badge: 'bg-red-100 text-red-800 ring-red-200',
        row: 'bg-red-50/50',
        dot: 'bg-red-500',
    },
    logout: {
        badge: 'bg-slate-100 text-slate-700 ring-slate-200',
        row: 'bg-slate-50/60',
        dot: 'bg-slate-400',
    },
    cambio_rol: {
        badge: 'bg-violet-100 text-violet-800 ring-violet-200',
        row: 'bg-violet-50/40',
        dot: 'bg-violet-500',
    },
    crear_usuario: {
        badge: 'bg-teal-100 text-teal-800 ring-teal-200',
        row: 'bg-teal-50/40',
        dot: 'bg-teal-500',
    },
    autorizar_documento: {
        badge: 'bg-emerald-100 text-emerald-800 ring-emerald-200',
        row: 'bg-emerald-50/40',
        dot: 'bg-emerald-500',
    },
    rechazar_documento: {
        badge: 'bg-rose-100 text-rose-800 ring-rose-200',
        row: 'bg-rose-50/50',
        dot: 'bg-rose-500',
    },
    emitir_documento: {
        badge: 'bg-indigo-100 text-indigo-800 ring-indigo-200',
        row: 'bg-indigo-50/40',
        dot: 'bg-indigo-500',
    },
}

export const DEFAULT_ACTION_STYLE = {
    badge: 'bg-neutral-100 text-neutral-700 ring-neutral-200',
    row: '',
    dot: 'bg-neutral-400',
}

export function getActionStyle(accion) {
    return ACTION_STYLES[accion] ?? DEFAULT_ACTION_STYLE
}
