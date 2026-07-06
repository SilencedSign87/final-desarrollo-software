import { Outlet } from "react-router-dom";
import DashboardShell from "../../components/DashboardShell";

export default function AdministrativoShell() {
    return (
        <>
            <DashboardShell
            >
                <Outlet />
            </DashboardShell>
        </>
    )
}