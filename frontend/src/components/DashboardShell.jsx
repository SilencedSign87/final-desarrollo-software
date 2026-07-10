import { Menu } from "lucide-react";
import { useState } from "react";
import { NavLink } from "react-router-dom";

export default function DashboardShell({ children, leadingContent, trailingContent, routes, headerContent }) {
    const [sidebarOpen, setSidebarOpen] = useState(false)

    return (
        <div className="flex h-screen overflow-hidden bg-neutral-200">
            {/* Mobile overlay */}
            {sidebarOpen && (
                <div
                    className="fixed inset-0 z-40 bg-black/30 md:hidden"
                    onClick={() => setSidebarOpen(false)}
                    aria-hidden="true"
                />
            )}
            {/* Sidebar */}
            <aside
                className={`
                    fixed inset-y-0 left-0 z-50 flex flex-col w-64 bg-neutral-100 md:bg-neutral-200 border-r border-neutral-400 md:border-neutral-300 
                    transition-transform duration-300 ease-in-out
                    md:static md:translate-x-0
                    ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
                    `}
                aria-label="Barra de navegación"
            >
                {/* leadingContent */}
                {leadingContent && (
                    <div className="flex shrink-0 px-6 py-5 border-b border-gray-200">
                        {leadingContent}
                    </div>
                )}
                {/* Navigation */}
                <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto" aria-label="Navegacion principal">
                    {routes?.map((route) => {
                        const Icon = route.icon

                        return (
                            <NavLink
                                key={route.path}
                                to={route.path}
                                end={route.exact ?? true}
                                onClick={() => setSidebarOpen(false)}
                                className={({ isActive }) =>
                                    `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${isActive
                                        ? 'bg-white text-blue-700 shadow-sm'
                                        : 'text-neutral-600 hover:bg-white/60 hover:text-neutral-900'
                                    }`
                                }
                                aria-label={route.name}
                            >
                                {Icon && <Icon className="w-5 h-5 shrink-0" aria-hidden="true" />}
                                <span>{route.name}</span>
                            </NavLink>
                        )

                    })}
                </nav>
                {/* trailingContent */}
                {trailingContent && (
                    <div className="flex shrink-0 px-4 py-4 border-t border-gray-200">
                        {trailingContent}
                    </div>
                )}
            </aside>
            {/* Area principal */}
            <div className="flex flex-col flex-1 w-0">
                <header
                    className={`
                        flex items-center gap-3 px-4 py-3
                        bg-white
                        ${!headerContent ? 'md:hidden' : ''}
                    `}
                >
                    {/* Hamburguesa: solo en mobile */}
                    <button
                        onClick={() => setSidebarOpen(true)}
                        className="p-2 text-neutral-500 rounded-lg hover:bg-white/60 focus:outline-none focus:ring-2 focus:ring-blue-500 md:hidden"
                        aria-label="Abrir menú de navegación"
                    >
                        <Menu className="w-5 h-5" />
                    </button>

                    {/* headerContent — puede ser título de página, breadcrumbs, etc. */}
                    {headerContent && (
                        <div className="flex-1">
                            {headerContent}
                        </div>
                    )}
                </header>

                {/* children - el contenido específico de cada dashboard */}
                <main className="flex-1 overflow-y-auto overflow-x-hidden bg-white" id="main-content" tabIndex={-1}>
                    <div className="p-6 md:p-4">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    )
}