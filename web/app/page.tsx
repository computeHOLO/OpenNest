'use client'

import { useEffect, useState } from 'react'

type Rule = { domain: string }

export default function Home() {
  const [rules, setRules] = useState<Rule[]>([])
  const [domain, setDomain] = useState('')

  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null

  const load = async () => {
    if (!token) {
      window.location.href = '/login'
      return
    }
    const res = await fetch('http://localhost:8080/rules', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
      return
    }
    const data = await res.json()
    setRules(data)
  }

  useEffect(() => { load() }, [])

  const addRule = async () => {
    if (!domain || !token) return
    await fetch('http://localhost:8080/rules', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ domain })
    })
    setDomain('')
    load()
  }

  const deleteRule = async (d: string) => {
    if (!token) return
    await fetch(`http://localhost:8080/rules/${encodeURIComponent(d)}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    })
    load()
  }

  return (
    <main style={{ maxWidth: 720, margin: '40px auto', fontFamily: 'system-ui' }}>
      <h1>🪺 OpenNest</h1>
      <p>Manage blocked domains</p>
      <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
        <input
          value={domain}
          onChange={(e) => setDomain(e.target.value)}
          placeholder="badsite.com"
          style={{ flex: 1, padding: 8 }}
        />
        <button onClick={addRule} style={{ padding: '8px 12px' }}>Add</button>
      </div>
      <h3 style={{ marginTop: 24 }}>Blocked domains</h3>
      <ul>
        {rules.map(r => (
          <li key={r.domain} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0' }}>
            <span>{r.domain}</span>
            <button onClick={() => deleteRule(r.domain)}>Remove</button>
          </li>
        ))}
      </ul>
    </main>
  )
}
