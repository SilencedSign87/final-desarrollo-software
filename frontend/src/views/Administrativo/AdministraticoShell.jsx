import { Outlet } from "react-router-dom";
import DashboardShell from "../../components/DashboardShell";

export default function AdministrativoShell() {
    return (
        <>
            <DashboardShell
                headerContent={
                    <h1 className="text-xl font-bold tracking-tight text-slate-900">
                        Bienvenido, Administrativo
                    </h1>
                }
            >
                <Outlet />
            </DashboardShell>
        </>
    )
}