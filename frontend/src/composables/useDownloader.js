/**
 * Composable for managing video downloads.
 * Handles job creation, progress polling, and file download.
 */
import { ref } from 'vue'
import { startDownload, getDownloadStatus, getFileUrl } from '../services/api'

export function useDownloader() {
  const status = ref('idle') // idle | downloading | processing | completed | failed
  const progress = ref(0)
  const errorMessage = ref(null)
  const jobId = ref(null)

  let pollInterval = null

  /**
   * Start a download and begin polling for progress.
   */
  async function download({ url, formatId = null, audioOnly = false }) {
    // Reset state
    status.value = 'downloading'
    progress.value = 0
    errorMessage.value = null

    try {
      const result = await startDownload({ url, formatId, audioOnly })
      jobId.value = result.job_id

      // Start polling
      pollInterval = setInterval(() => pollProgress(), 1000)
    } catch (e) {
      status.value = 'failed'
      errorMessage.value = e.message || 'Error al iniciar la descarga'
    }
  }

  /**
   * Poll download progress.
   */
  async function pollProgress() {
    if (!jobId.value) return

    try {
      const result = await getDownloadStatus(jobId.value)

      status.value = result.status
      progress.value = result.progress

      if (result.status === 'completed') {
        stopPolling()
        // Trigger browser download
        triggerFileDownload(jobId.value)
      } else if (result.status === 'failed') {
        stopPolling()
        errorMessage.value = result.error || 'Error durante la descarga'
      }
    } catch (e) {
      // Don't stop polling on network hiccups, just log
      console.warn('Poll error:', e)
    }
  }

  /**
   * Trigger the browser's native file download.
   */
  function triggerFileDownload(id) {
    const url = getFileUrl(id)
    const a = document.createElement('a')
    a.href = url
    a.download = ''
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }

  /**
   * Stop polling.
   */
  function stopPolling() {
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
  }

  /**
   * Reset to initial state.
   */
  function reset() {
    stopPolling()
    status.value = 'idle'
    progress.value = 0
    errorMessage.value = null
    jobId.value = null
  }

  return {
    status,
    progress,
    errorMessage,
    jobId,
    download,
    reset,
  }
}
