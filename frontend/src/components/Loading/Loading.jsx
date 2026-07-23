export default function Loading({ texto }) {
  return (
    <div className="loading active">
      <div className="spinner"></div>
      <p style={{ color: 'var(--text-secondary)' }}>{texto}</p>
    </div>
  )
}
