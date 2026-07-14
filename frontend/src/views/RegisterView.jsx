import { useState } from "react"
import { Register } from "../services/authService"
import { useNavigate } from "react-router-dom"

export default function RegisterView() {
    const [error, setError] = useState(null)
    const navigate = useNavigate()

    const handleSubmit = async (event) => {
        event.preventDefault()
        if (!/^\d{8}$/.test(event.target.dni.value.trim())) {
            setError('El DNI debe tener exactamente 8 dígitos numéricos')
            return
        }
        
        if (event.target.password.value !== event.target.confirmPassword.value) {
            setError('Las contraseñas no coinciden')
            return
        }

        if (event.target.password.value.length < 6) {
            setError('La contraseña debe tener al menos 6 caracteres')
            return
        }

        const data = {
            nombres: event.target.name.value,
            apellidos: event.target.lastName.value,
            email: event.target.email.value,
            password: event.target.password.value,
            dni: event.target.dni.value,
            rol: 'estudiante'
        }

        const result = await Register(data)

        if (result?.data.id) {
            navigate('/login')
        }else {
            setError('Error al registrar el usuario')
        }
    }

    return (
        <div className='w-dvw h-dvh flex flex-col items-center justify-center'>
            <div className='mb-8'>
                <h1 className='text-3xl font-bold text-gray-800'>Registro de estudiante</h1>
            </div>
            <div className='max-w-7xl p-8 shadow-sm bg-white rounded-lg'>
                <form onSubmit={handleSubmit}>
                    <fieldset className="grid grid-cols-2 gap-x-8 gap-y-2">
                        <label className='flex flex-col gap-2'>
                            Nombres:
                            <input type="text" name="name" required />
                        </label>
                        <label className='flex flex-col gap-2'>
                            Apellidos:
                            <input type="text" name="lastName" required />
                        </label>
                        <label className=' col-span-2 flex flex-col gap-2'>
                            Email:
                            <input type="email" name="email" required />
                        </label>
                        <label className=' col-span-2 flex flex-col gap-2'>
                            DNI:
                            <input
                                type="text"
                                name="dni"
                                inputMode="numeric"
                                pattern="\d{8}"
                                maxLength={8}
                                title="Exactamente 8 dígitos"
                                required
                            />
                        </label>

                    </fieldset>
                    <hr className="border-neutral-300 my-3" />
                    <fieldset className="grid grid-cols-1 gap-2">
                        <label className='flex flex-col gap-2'>
                            Contraseña:
                            <input type="password" name="password" required />
                        </label>
                        <label className='flex flex-col gap-2'>
                            Confirmar Contraseña:
                            <input type="password" name="confirmPassword" required />
                        </label>
                    </fieldset>
                    <fieldset className='mt-4'>
                        <button type="submit" className='primary w-full'>
                            Registrarse
                        </button>
                        {
                            error && <p className='mt-2 text-sm text-red-500 text-center'>{error}</p>
                        }
                    </fieldset>
                </form>
                <div className='mt-6 flex flex-col items-center justify-center'>
                    <p className='mt-2 text-sm text-gray-500'>¿Ya tienes una cuenta? <a href="/login" className='text-blue-500 hover:underline'>Inicia sesión aquí</a></p>
                </div>
            </div>
        </div>
    )
}
