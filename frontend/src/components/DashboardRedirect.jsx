import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Spinner from "./Spinner";
import LoadingView from "../views/LoadingView";

const rolDefaultRoutes = {
    "estudiante": "/estudiante/matricula",
    "docente": "/docente/cursos",
    "administrador": "/administrador/matricula",
    "direccion": "/direccion/matricula"
}

export default function DashboardRedirect() {
    const { user, isLoading, isAuthenticated } = useAuth()

    if (isLoading) return <LoadingView/>
    if (!isAuthenticated) return <Navigate to="/" replace />
    return <Navigate to={rolDefaultRoutes[user.rol] || "/"} replace />

}