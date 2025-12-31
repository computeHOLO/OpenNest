'use client'

import { useState } from 'react'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const submit = async () => {
    setError('')
    const body = new URLSearchParams()
    body.append('username', username)
    body.append('password', password)
    body.append('grant_type', 'password')
    const res = await fetch('http://localhost:8080/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body
    })
    if (!res.ok) {
      setError('Invalid credentials')
      return
    }
    const data = await res.json()
    localStorage.setItem('token', data.access_token)
    window.location.href = '/'
  }

  return (
    <main style={{ maxWidth: 360, margin: '80px auto', fontFamily: 'system-ui' }}>
      <h1>Login</h1>
      <div style={{ display: 'grid', gap: 12, marginTop: 16 }}>
        <input value={username} onChange={e => setUsername(e.target.value)} placeholder="username" />
        <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="password" />
        <button onClick={submit}>Sign in</button>
        {error && <p style={{ color: 'crimson' }}>{error}</p>}
      </div>
    </main>
  )
}
