import { BookOpen, DoorClosed, LayoutDashboard, Table } from "lucide-react"
import DashboardShell from "../../components/DashboardShell"
import LogoutButton from "../../components/LogoutButton"
import { Outlet } from "react-router-dom"

const routes = [
    {path: '/docente/secciones', icon: DoorClosed, name: 'Secciones' },
    { path: '/docente/cursos', icon: BookOpen, name: 'Cursos' },
    { path: '/docente/notas', icon: Table, name: 'Notas' },
]

export default function DocenteShell() {
    return(
        <>
            <DashboardShell
                headerContent={
                    <h1 className="text-xl font-bold tracking-tight text-slate-900">
                        Bienvenido, Docente
                    </h1>
                }
                routes={routes}
                trailingContent={
                    <>
                        <LogoutButton className="subtle flex gap-3 justify-start w-full" />
                    </>
                }
            >
                <Outlet />
            </DashboardShell>
        </>
    )
}