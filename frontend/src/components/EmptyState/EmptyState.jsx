export default function EmptyState({ icono, children }) {
  return (
    <div className="empty-state">
      <i className={`fas ${icono}`}></i>
      {children}
    </div>
  )
}
