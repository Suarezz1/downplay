/**
 * API client for DownPlay backend.
 * Uses native fetch — no external HTTP dependencies.
 */

const BASE_URL = 'http://localhost:8000'

/**
 * Generic fetch wrapper with error handling.
 */
async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`

  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  }

  const response = await fetch(url, config)

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response
}

/**
 * Extract video metadata and available formats.
 */
export async function getVideoInfo(url) {
  const response = await request('/api/video/info', {
    method: 'POST',
    body: JSON.stringify({ url }),
  })
  return response.json()
}

/**
 * Start a download job.
 * Returns { job_id, status }.
 */
export async function startDownload({ url, formatId = null, audioOnly = false }) {
  const response = await request('/api/video/download', {
    method: 'POST',
    body: JSON.stringify({
      url,
      format_id: formatId,
      audio_only: audioOnly,
    }),
  })
  return response.json()
}

/**
 * Poll the status of a download job.
 */
export async function getDownloadStatus(jobId) {
  const response = await request(`/api/video/status/${jobId}`)
  return response.json()
}

/**
 * Get the download URL for a completed job.
 */
export function getFileUrl(jobId) {
  return `${BASE_URL}/api/video/file/${jobId}`
}

/**
 * Health check.
 */
export async function checkHealth() {
  const response = await request('/api/health')
  return response.json()
}
