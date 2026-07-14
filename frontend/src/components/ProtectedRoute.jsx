import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Spinner from "./Spinner";
import LoadingView from "../views/LoadingView";

export default function ProtectedRoute({ children, allowedRoles }) {
    const { user, isLoading, isAuthenticated } = useAuth()

    if (isLoading) return <LoadingView />
    if (!isAuthenticated) return <Navigate to="/" replace />

    if (allowedRoles && !allowedRoles.includes(user.rol)) {
        return <Navigate to={`/${user.rol}/dashboard`} replace />
    }
    
    return children
}