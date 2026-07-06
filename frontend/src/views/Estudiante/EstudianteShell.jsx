import { BookOpen, GraduationCap, LayoutDashboard, User } from "lucide-react";
import DashboardShell from "../../components/DashboardShell";
import LogoutButton from "../../components/LogoutButton";
import { useAuth } from "../../context/AuthContext";
import { Outlet } from "react-router-dom";

const routes = [
    { path: '/estudiante/dashboard', icon: LayoutDashboard, name: 'Dashboard' },
    { path: '/estudiante/cursos', icon: BookOpen, name: 'Mis Cursos' },
    { path: '/estudiante/notas', icon: GraduationCap, name: 'Notas' },
    { path: '/estudiante/perfil', icon: User, name: 'Perfil' },
]

export default function EstudianteShell() {
    const { user } = useAuth()


    return (
        <>
            <DashboardShell
                headerContent={
                    <h1 className="text-xl font-bold tracking-tight text-slate-900">
                        Bienvenido, {user?.nombres}
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