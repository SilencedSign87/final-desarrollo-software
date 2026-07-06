import { LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Logout } from "../services/authService";
import { useAuth } from "../context/AuthContext";
import { twMerge } from "tailwind-merge";
import Dialog from "./Dialog";

export default function LogoutButton({ className = '', iconClassName = '' }) {
    const navigate = useNavigate()
    const { logout } = useAuth()

    const handleLogout = () => {
        logout()
    }

    return (
        <Dialog>
            <Dialog.Trigger className={'subtle flex items-center justify-start gap-3 w-full'}>
                <LogOut className={twMerge('w-5 h-5', iconClassName)} /> <span> Cerrar sesión</span>    
            </Dialog.Trigger>
            <Dialog.Surface>
                <Dialog.Header>
                    <h2 className="text-lg font-semibold">Cerrar sesión</h2>
                </Dialog.Header>
                <Dialog.Content>
                    <p>Está seguro que desea cerrar sesión?</p>
                </Dialog.Content>
                <Dialog.Footer>
                    <button onClick={handleLogout} className="primary">
                        Cerrar sesión
                    </button>
                    <Dialog.Trigger className="subtle">
                        Cancelar
                    </Dialog.Trigger>
                </Dialog.Footer>
            </Dialog.Surface>
        </Dialog>
    )
}