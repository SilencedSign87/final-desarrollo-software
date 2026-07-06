import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function DashboardRedirect() {
    const {user} = useAuth()

    return <Navigate to={`/${user.rol}/dashboard`} replace />

}