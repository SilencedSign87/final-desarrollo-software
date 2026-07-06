import DashboardShell from "../../components/DashboardShell";
import LogoutButton from "../../components/LogoutButton";
import { useAuth } from "../../context/AuthContext";

export default function EstudianteDashboard() {
    const { user } = useAuth()


    return (
        <>
            <DashboardShell
                headerContent={
                    <h1 className="text-xl font-bold tracking-tight text-slate-900">
                        Bienvenido, {user?.nombres}
                    </h1>
                }
                trailingContent={
                    <>
                        <LogoutButton />
                    </>
                }
            >
                <p>
                    vista para estudiantes
                </p>
            </DashboardShell>
        </>
    )
}