const catalog = document.querySelector('#catalog')
const stats = document.querySelector('#stats')
const search = document.querySelector('#search')
let entries = []
let filter = 'all'

function escapeHtml(value = '') {
  return value.replace(/[&<>'"]/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[char])
}

function render() {
  const term = search.value.trim().toLocaleLowerCase('es')
  const visible = entries.filter((entry) => {
    const matchesType = filter === 'all' || entry.type === filter
    const haystack = `${entry.title} ${entry.description} ${entry.source}`.toLocaleLowerCase('es')
    return matchesType && (!term || haystack.includes(term))
  })

  const slidevCount = entries.filter((entry) => entry.type === 'slidev').length
  const marpCount = entries.filter((entry) => entry.type === 'marp').length
  stats.innerHTML = `<strong>${visible.length}</strong> presentaciones · ${slidevCount} Slidev · ${marpCount} Marp`

  if (!visible.length) {
    catalog.innerHTML = '<div class="empty">No hay presentaciones que coincidan con la búsqueda.</div>'
    return
  }

  catalog.innerHTML = visible.map((entry) => `
    <article class="card">
      <div class="card-top">
        <span class="badge badge-${entry.type}">${escapeHtml(entry.type)}</span>
        <span class="collection">${escapeHtml(entry.collection)}</span>
      </div>
      <h2>${escapeHtml(entry.title)}</h2>
      <p>${escapeHtml(entry.description || 'Presentación técnica y material de apoyo.')}</p>
      <div class="card-source">${escapeHtml(entry.source)}</div>
      <a class="open" href="./${entry.url}" target="_blank" rel="noopener">Abrir presentación <span aria-hidden="true">↗</span></a>
    </article>
  `).join('')
}

document.querySelectorAll('[data-filter]').forEach((button) => {
  button.addEventListener('click', () => {
    filter = button.dataset.filter
    document.querySelectorAll('[data-filter]').forEach((item) => item.classList.toggle('is-active', item === button))
    render()
  })
})
search.addEventListener('input', render)

fetch('./catalog.json')
  .then((response) => response.json())
  .then((data) => {
    entries = data.presentations || []
    render()
  })
  .catch(() => {
    catalog.innerHTML = '<div class="empty">Ejecuta <code>just portal-build</code> para generar el catálogo.</div>'
  })
