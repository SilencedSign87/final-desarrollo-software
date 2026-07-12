import { createContext, useContext, useMemo, useState, Children, useRef, isValidElement } from "react"
import { twMerge } from "tailwind-merge"
import { ChevronDown } from "lucide-react"

const TableContext = createContext(null)

function useTableContext() {
    const ctx = useContext(TableContext)
    if (!ctx) throw new Error("Table subcomponent must be used within Table")
    return ctx
}

const Table = ({ className, children, ...props }) => {
    const [sortConfig, setSortConfig] = useState({ columnIndex: null, direction: null })

    return (
        <TableContext.Provider value={{ sortConfig, setSortConfig, isHeader: false }}>
            <div className="w-full overflow-x-auto">
                <table className={twMerge("min-w-fit w-full divide-y divide-neutral-200 text-sm", className)} {...props}>
                    {children}
                </table>
            </div>
        </TableContext.Provider>
    )
}

Table.Header = function Header({ className, children, ...props }) {
    const { sortConfig, setSortConfig } = useTableContext()
    return (
        <thead className={twMerge("bg-neutral-50", className)} {...props}>
            <TableContext.Provider value={{ sortConfig, setSortConfig, isHeader: true }}>
                {children}
            </TableContext.Provider>
        </thead>
    )
}

Table.Content = function Content({ className, children, ...props }) {
    const { sortConfig } = useTableContext()
    const rows = Children.toArray(children).filter(Boolean)

    const sortedRows = useMemo(() => {
        if (sortConfig.columnIndex === null || sortConfig.direction === null) return rows

        return [...rows].sort((a, b) => {
            const getValue = (el) => {
                if (!isValidElement(el)) return ""
                const cells = Children.toArray(el.props.children)
                const cell = cells[sortConfig.columnIndex]
                if (!isValidElement(cell)) return ""
                const raw = cell.props.value ?? cell.props.children ?? ""
                return raw
            }

            const aRaw = getValue(a)
            const bRaw = getValue(b)
            const aVal = typeof aRaw === "number" ? aRaw : String(aRaw)
            const bVal = typeof bRaw === "number" ? bRaw : String(bRaw)

            if (typeof aVal === "number" && typeof bVal === "number") {
                return sortConfig.direction === "asc" ? aVal - bVal : bVal - aVal
            }
            return sortConfig.direction === "asc"
                ? String(aVal).localeCompare(String(bVal))
                : String(bVal).localeCompare(String(aVal))
        })
    }, [rows, sortConfig])

    return (
        <tbody className={twMerge("divide-y divide-neutral-200 bg-white", className)} {...props}>
            {sortedRows}
        </tbody>
    )
}

Table.Row = function Row({ className, children, ...props }) {
    return (
        <tr className={className} {...props}>
            {children}
        </tr>
    )
}

Table.Cell = function Cell({  className, sortable = false, value, children, ...props }) {
    const { isHeader, sortConfig, setSortConfig } = useTableContext()
    const colIndex = useRef(null)

    const handleClick = () => {
        if (!sortable) return
        setSortConfig((prev) => {
            if (prev.columnIndex !== colIndex.current) {
                return { columnIndex: colIndex.current, direction: "desc" }
            }
            if (prev.direction === "desc") {
                return { columnIndex: colIndex.current, direction: "asc" }
            }
            return { columnIndex: null, direction: null }
        })
    }

    const Tag = isHeader ? "th" : "td"

    return (
        <Tag
            ref={(el) => {
                if (el && colIndex.current === null) {
                    colIndex.current = Array.from(el.parentElement?.children || []).indexOf(el)
                }
            }}
            className={twMerge(
                isHeader
                    ? "px-4 py-3 font-medium text-neutral-600"
                    : "px-4 py-3 text-neutral-900",
                sortable && "cursor-pointer select-none hover:bg-neutral-100",
                className,
            )}
            onClick={isHeader && sortable ? handleClick : undefined}
            {...props}
        >
            <span className="inline-flex items-center gap-1">
                {children}
                {isHeader && sortable && (
                    <ChevronDown
                        size={14}
                        className={twMerge(
                            "text-neutral-800 transition-transform",
                            colIndex.current === sortConfig.columnIndex
                                ? sortConfig.direction === "asc" ? "rotate-180" : ""
                                : "opacity-30",
                        )}
                    />
                )}
            </span>
        </Tag>
    )
}

export default Table
