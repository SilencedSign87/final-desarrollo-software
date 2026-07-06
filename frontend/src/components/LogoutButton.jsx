import { LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Logout } from "../services/authService";
import { useAuth } from "../context/AuthContext";

export default function LogoutButton() {
    const navigate = useNavigate()
    const { logout } = useAuth()

    const handleLogout = () => {
        logout()
    }

    return (
        <button className="subtle flex items-center justify-center gap-4 w-full" onClick={handleLogout}>
            <LogOut /> <span> Cerrar sesión</span>
        </button>
    )
}