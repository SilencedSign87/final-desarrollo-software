import { BarChart3, FileText, LayoutDashboard, ClipboardList, GraduationCap, Table } from "lucide-react"
import { Outlet } from "react-router-dom"
import DashboardShell from "../../components/DashboardShell"
import LogoutButton from "../../components/LogoutButton"
import { useAuth } from "../../context/AuthContext"

const routes = [
    { path: '/direccion/dashboard', icon: LayoutDashboard, name: 'Dashboard' },
    { path: '/direccion/matricula', icon: ClipboardList, name: 'Matrícula' },
    {path: '/direccion/notas', icon: Table, name: 'Notas' },
    { path: '/direccion/carga-docente', icon: GraduationCap, name: 'Carga Docente' },
    { path: '/direccion/documentos', icon: FileText, name: 'Documentos' },
    { path: '/direccion/auditorias', icon: BarChart3, name: 'Auditorías' },
]

export default function DireccionShell() {
    const { user } = useAuth()

    return (
        <DashboardShell
            headerContent={
                <h1 className="text-xl font-bold tracking-tight text-slate-900">
                    Bienvenido, {user?.nombres}
                </h1>
            }
            routes={routes}
            trailingContent={
                <LogoutButton className="subtle flex gap-3 justify-start w-full" />
            }
        >
            <Outlet />
        </DashboardShell>
    )
}