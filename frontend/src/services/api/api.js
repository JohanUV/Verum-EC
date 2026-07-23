// Cliente de la API JSON de Flask (misma origin, sesion por cookie).
export async function postJSON(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body || {}),
  })
  const data = await res.json().catch(() => ({}))
  return { ok: res.ok, data }
}

export async function getJSON(url) {
  const res = await fetch(url)
  const data = await res.json().catch(() => ({}))
  return { ok: res.ok, data }
}
