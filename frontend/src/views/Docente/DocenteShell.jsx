import DashboardShell from "../../components/DashboardShell"
import LogoutButton from "../../components/LogoutButton"
import { Outlet } from "react-router-dom"

export default function DocenteShell() {
    return(
        <>
            <DashboardShell
                headerContent={
                    <h1 className="text-xl font-bold tracking-tight text-slate-900">
                        Bienvenido, Docente
                    </h1>
                }
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