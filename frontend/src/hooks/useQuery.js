import { useCallback, useMemo } from "react"
import { useSearchParams } from "react-router-dom"

const NAMESPACESEPARATOR = '_'

function addNamespace(namespace, query) {
    return `${namespace}${NAMESPACESEPARATOR}${query}`
}

function stripNamespace(namespace, query) {
    return query.replace(`${namespace}${NAMESPACESEPARATOR}`, '')
}

export function useQuery(namespace) {
    const [searchParams, setSearchParams] = useSearchParams()

    const params = useMemo(() => {
        const result = {}
        for (const [key, value] of searchParams.entries()) {
            const shortkey = stripNamespace(namespace, key)
            if (shortkey === null) continue

            if (Object.hasOwn(result, shortkey)) {
                const existing = result[shortkey]
                result[shortkey] = Array.isArray(existing) ? [...existing, value] : [existing, value]
            } else {
                result[shortkey] = value
            }
        }
        return result
    }, [searchParams, namespace])

    const get = useCallback(
        (key) => searchParams.get(addNamespace(namespace, key))
        , [searchParams, namespace]
    )

    const set = useCallback(
        (keyOrRecord, value) => {
            setSearchParams(
                (prev) => {
                    const next = new URLSearchParams(prev)

                    if (typeof keyOrRecord === 'object' && keyOrRecord !== null) {
                        for (const [k, v] of Object.entries(keyOrRecord)) {
                            applyValue(next, addNamespace(namespace, k), v)
                        }
                    } else {
                        applyValue(next, addNamespace(namespace, keyOrRecord), value)
                    }

                    return next
                },
                { replace: true },
            )
        },
        [namespace, setSearchParams],
    )

    const remove = useCallback(
        (key) => {
            setSearchParams(
                (prev) => {
                    const next = new URLSearchParams(prev)
                    next.delete(addNamespace(namespace, key))
                    return next
                },
                { replace: true },
            )
        },
        [namespace, setSearchParams],
    )

    const clear = useCallback(() => {
        setSearchParams(
            (prev) => {
                const next = new URLSearchParams(prev)
                if (namespace) {
                    const prefix = `${namespace}${NAMESPACESEPARATOR}`
                    for (const key of next.keys()) {
                        if (key.startsWith(prefix)) next.delete(key)
                    }
                } else {
                    for (const key of next.keys()) next.delete(key)
                }
                return next
            },
            { replace: true }
        )
    }, [namespace, setSearchParams])

    return { params, get, set, remove, clear }
}

function applyValue(params, key, value) {
    params.delete(key)
    if (value == null || value === '') return
    if (Array.isArray(value)) {
        for (const v of value) {
            if (v != null && v !== '') params.append(key, String(v))
        }
    } else {
        params.set(key, String(value))
    }
}
