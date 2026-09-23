const BASE = '/api'

async function asJson(r, okStatuses = [200]) {
  if (!okStatuses.includes(r.status)) {
    let detail = r.statusText
    try {
      const body = await r.json()
      detail = body.detail || detail
    } catch {
      // ignore
    }
    throw new Error(detail)
  }
  return r.json()
}

export function listProjects() {
  return fetch(`${BASE}/projects`).then((r) => asJson(r))
}

export function createProject(name, files, stage1Backend = "ollama") {
  const form = new FormData()
  form.append('name', name)
  form.append('stage1_backend', stage1Backend)
  for (const f of files) form.append('files', f)
  return fetch(`${BASE}/projects`, { method: 'POST', body: form }).then((r) => asJson(r))
}

export function getProject(id) {
  return fetch(`${BASE}/projects/${id}`).then((r) => asJson(r))
}

export function runProject(id, stage1Backend = 'ollama') {
  return fetch(`${BASE}/projects/${id}/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ stage1_backend: stage1Backend }),
  }).then((r) => asJson(r, [200, 409]))
}

export function runStage(id, stage, stage1Backend = null) {
  return fetch(`${BASE}/projects/${id}/stages/${stage}/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ stage1_backend: stage === 'stage_1' ? stage1Backend : null }),
  }).then((r) => asJson(r, [200, 409]))
}

export function answerClarifications(id, answers) {
  return fetch(`${BASE}/projects/${id}/clarifications/answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ answers }),
  }).then((r) => asJson(r))
}

export function useDefaultClarifications(id) {
  return fetch(`${BASE}/projects/${id}/clarifications/use-defaults`, { method: 'POST' }).then((r) => asJson(r))
}

export function getArtifact(id, kind) {
  return fetch(`${BASE}/projects/${id}/artifacts/${kind}`).then((r) => {
    if (r.status === 404) return null
    return asJson(r)
  })
}

export function streamLogs(id, { onLog, onStatus }) {
  const es = new EventSource(`${BASE}/projects/${id}/logs/stream`)
  es.onmessage = (ev) => {
    try {
      onLog(JSON.parse(ev.data))
    } catch {
      // ignore malformed line
    }
  }
  es.addEventListener('status', (ev) => {
    try {
      onStatus(JSON.parse(ev.data))
    } catch {
      // ignore
    }
  })
  return es
}
