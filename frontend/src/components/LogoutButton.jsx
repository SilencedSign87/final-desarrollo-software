import { LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Logout } from "../services/authService";
import { useAuth } from "../context/AuthContext";
import { twMerge } from "tailwind-merge";

export default function LogoutButton({ className = '', iconClassName='' }) {
    const navigate = useNavigate()
    const { logout } = useAuth()

    const handleLogout = () => {
        logout()
    }

    return (
        <button className={twMerge('flex gap-3 items-center justify-center', className)} onClick={handleLogout}>
            <LogOut className={twMerge('w-5 h-5', iconClassName)} /> <span> Cerrar sesión</span>
        </button>
    )
}