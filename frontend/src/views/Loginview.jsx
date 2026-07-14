import { useEffect, useState } from 'react'
import { healthCheck } from '../services/api'
import { useAuth } from '../context/AuthContext'
import Spinner from '../components/Spinner'
import { useNavigate } from 'react-router-dom'
import { AtSign, KeyRound } from 'lucide-react'

export default function LoginView() {
    const { user, isLoading, isAuthenticated, login } = useAuth()
    const [submitting, setSubmitting] = useState(false)
    const navigate = useNavigate()
    const [health, setHealth] = useState("")
    const [error, setError] = useState(null)

    const handleSubmit = async (event) => {
        event.preventDefault()
        setSubmitting(true)
        const credentials = {
            email: event.target.email.value,
            password: event.target.password.value
        }
        try {
            const response = await login(credentials)
            if (response?.data) {
                navigate('/dashboard')
            }
        } catch (error) {
            console.error('Error during login:', error)
            setError('Credenciales inválidas')
        } finally {
            setSubmitting(false)
        }
    }

    const checkHealth = async () => {
        try {
            const data = await healthCheck()
            setHealth(data.data.status === 'ok' ? 'API en línea' : 'API no está saludable')
        } catch (error) {
            setHealth('Error al verificar la salud de la API')
        }
    }

    useEffect(() => {
        checkHealth()
    }, [])

    useEffect(() => {
        if (!isLoading && isAuthenticated) {
            navigate('/dashboard')
        }
    }, [isLoading, isAuthenticated, navigate])

    return (
        <>
            <div className='w-dvw h-dvh flex flex-col items-center justify-center'>
                <div className='mb-8'>
                    <h1 className='text-3xl font-bold text-gray-800'>Sistema académico</h1>
                </div>
                <div className='max-w-7xl p-8 shadow-sm bg-white rounded-lg'>

                    {
                        isLoading
                            ? <Spinner />
                            : isAuthenticated
                                ? <>
                                    <a href="/dashboard" className='flex flex-col items-center justify-center text-sm font-light text-gray-700 gap-2'>
                                        <p className='font-normal'>
                                            Bienvenido, {user?.nombres} {user?.apellidos}
                                        </p>
                                        <Spinner />
                                        <small>Redirigiendo...</small>
                                    </a>
                                </>
                                : <>
                                    <form onSubmit={handleSubmit}>
                                        <fieldset>
                                            <label className='flex flex-col gap-2'>
                                                Correo:
                                                <div className='grid grid-cols-[auto_1fr] border border-neutral-300 rounded-lg px-2'>
                                                    <AtSign className=' text-gray-400 self-center' size={20} />
                                                    <input type="email" name="email" className="transparent" required />
                                                </div>
                                            </label>
                                            <label className='flex flex-col gap-2 mt-2'>
                                                Contraseña:
                                                <div className='grid grid-cols-[auto_1fr] border border-neutral-300 rounded-lg px-2'>
                                                    <KeyRound className=' text-gray-400 self-center' size={20} />
                                                    <input type="password" name="password" className="transparent" required />
                                                </div>
                                            </label>
                                        </fieldset>
                                        <fieldset className='mt-4'>
                                            <button type="submit" className='primary flex w-full items-center justify-center gap-2' disabled={submitting}>
                                                {
                                                    submitting && <Spinner color='#ffffff' strokeWidth={2} size={20} className='block' />
                                                }
                                                <span className='block'>
                                                    Acceder
                                                </span>
                                            </button>
                                        </fieldset>
                                        {
                                            error && <p className='mt-2 text-sm text-red-500 text-center'>{error}</p>
                                        }
                                    </form>
                                    <div className='mt-6 flex flex-col items-center justify-center'>
                                        <p className='mt-2 text-sm text-gray-500'>¿Olvidó su contraseña? <a href="/reset-password" className='text-blue-500 hover:underline'>Recupérela aquí</a></p>
                                    </div>
                                </>
                    }
                </div>
                {
                    health !== "" && <p className='absolute bottom-0 left-0 p-4 text-sm text-gray-500'>{health}</p>
                }
            </div>
        </>
    )
}