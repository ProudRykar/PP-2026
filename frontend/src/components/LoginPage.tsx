import { useState } from 'react'
import { useAuth } from '../hooks/AuthContext'

interface LoginPageProps {
  onSwitchToRegister: () => void
}

export function LoginPage({ onSwitchToRegister }: LoginPageProps) {
  const { login } = useAuth()
  const [formLogin, setFormLogin] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      console.debug('[LoginPage] submitting...', { formLogin })
      await login(formLogin, password)
      console.debug('[LoginPage] login ok, isAuthenticated should be true now')
    } catch (err) {
      console.debug('[LoginPage] login error:', err)
      setError(err instanceof Error ? err.message : 'Ошибка входа')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100 dark:bg-gray-950">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm rounded-2xl bg-white p-8 shadow-lg dark:bg-gray-800"
      >
        <h1 className="mb-6 text-center text-2xl font-bold text-gray-800 dark:text-gray-100">
          Вход
        </h1>

        {error && (
          <p className="mb-4 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-600 dark:bg-red-900/30 dark:text-red-400">
            {error}
          </p>
        )}

        <div className="mb-4">
          <label className="mb-1 block text-sm font-medium text-gray-600 dark:text-gray-400">
            Логин
          </label>
          <input
            type="text"
            value={formLogin}
            onChange={e => setFormLogin(e.target.value)}
            className="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
            required
            autoFocus
          />
        </div>

        <div className="mb-6">
          <label className="mb-1 block text-sm font-medium text-gray-600 dark:text-gray-400">
            Пароль
          </label>
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            className="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
            required
          />
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-lg bg-blue-500 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-600 disabled:opacity-50"
        >
          {submitting ? 'Вход...' : 'Войти'}
        </button>

        <p className="mt-4 text-center text-sm text-gray-400 dark:text-gray-500">
          Нет аккаунта?{' '}
          <button
            type="button"
            onClick={onSwitchToRegister}
            className="font-medium text-blue-500 hover:text-blue-600"
          >
            Зарегистрироваться
          </button>
        </p>
      </form>
    </div>
  )
}
