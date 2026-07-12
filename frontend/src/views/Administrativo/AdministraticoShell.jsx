import { FileText, LayoutDashboard, Shield, ClipboardList, BookOpen, GraduationCap, Layers, Table } from "lucide-react";
import { Outlet } from "react-router-dom";
import DashboardShell from "../../components/DashboardShell";
import LogoutButton from "../../components/LogoutButton";
import { useAuth } from "../../context/AuthContext";

const routes = [
    { path: '/administrador/dashboard', icon: LayoutDashboard, name: 'Dashboard' },
    { path: '/administrador/matricula', icon: ClipboardList, name: 'Matrícula' },
    { path: '/administrador/cursos', icon: BookOpen, name: 'Cursos' },
    { path: '/administrador/notas', icon: Table, name: 'Notas' },
    { path: '/administrador/docentes', icon: GraduationCap, name: 'Docentes' },
    { path: '/administrador/secciones', icon: Layers, name: 'Secciones' },
    { path: '/administrador/documentos', icon: FileText, name: 'Documentos' },
    { path: '/administrador/seguridad', icon: Shield, name: 'Seguridad' },
]

export default function AdministrativoShell() {
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