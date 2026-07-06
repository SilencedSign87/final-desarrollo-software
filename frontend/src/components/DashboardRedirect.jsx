import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Spinner from "./spinner";
import LoadingView from "../views/LoadingView";

export default function DashboardRedirect() {
    const { user, isLoading, isAuthenticated } = useAuth()

    if (isLoading) return <LoadingView/>
    if (!isAuthenticated) return <Navigate to="/" replace />
    return <Navigate to={`/${user.rol}/dashboard`} replace />

}