import { GraduationCap, FileText, ClipboardList, Star } from "lucide-react";
import DashboardShell from "../../components/DashboardShell";
import LogoutButton from "../../components/LogoutButton";
import { useAuth } from "../../context/AuthContext";
import { Outlet } from "react-router-dom";

const routes = [
    { path: '/estudiante/matricula', icon: ClipboardList, name: 'Matrícula' },
    { path: '/estudiante/notas', icon: GraduationCap, name: 'Notas' },
    { path: '/estudiante/record-academico', icon: Star, name: 'Record Académico' },
    { path: '/estudiante/documentos', icon: FileText, name: 'Documentos' },
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