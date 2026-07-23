// Verum - logica de la pantalla de login
async function doLogin() {
    const user = document.getElementById('username').value.trim();
    const pwd = document.getElementById('password').value;
    const err = document.getElementById('errorMsg');
    if (!user || !pwd) { err.textContent = 'Completa ambos campos'; err.style.display = 'block'; return; }
    try {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: user, password: pwd})
        });
        const data = await res.json();
        if (data.ok) { window.location.href = '/app'; }
        else { err.textContent = data.error || 'Error'; err.style.display = 'block'; }
    } catch (e) { err.textContent = 'Error de conexion'; err.style.display = 'block'; }
}
document.querySelectorAll('input').forEach(i => i.addEventListener('keydown', e => { if (e.key === 'Enter') doLogin(); }));
