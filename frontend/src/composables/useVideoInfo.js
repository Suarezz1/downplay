/**
 * Composable for extracting video information.
 * Handles loading state, error state, and format parsing.
 */
import { ref, computed } from 'vue'
import { getVideoInfo } from '../services/api'

// Platform detection from URL (client-side, before API call)
const PLATFORM_PATTERNS = {
  youtube: [/youtube\.com/, /youtu\.be/],
  tiktok: [/tiktok\.com/],
  instagram: [/instagram\.com/],
  facebook: [/facebook\.com/, /fb\.watch/],
  x: [/twitter\.com/, /x\.com/],
}

const PLATFORM_INFO = {
  youtube: { name: 'YouTube', icon: '▶️', color: 'var(--youtube)' },
  tiktok: { name: 'TikTok', icon: '🎵', color: 'var(--tiktok)' },
  instagram: { name: 'Instagram', icon: '📷', color: '#e1306c' },
  facebook: { name: 'Facebook', icon: '📘', color: 'var(--facebook)' },
  x: { name: 'X', icon: '𝕏', color: 'var(--twitter)' },
  other: { name: 'Video', icon: '🎬', color: 'var(--accent-primary)' },
}

export function useVideoInfo() {
  const videoInfo = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  /**
   * Detect platform from URL string (instant, no API call).
   */
  function detectPlatform(url) {
    if (!url) return null
    for (const [platform, patterns] of Object.entries(PLATFORM_PATTERNS)) {
      for (const pattern of patterns) {
        if (pattern.test(url)) return platform
      }
    }
    return null
  }

  /**
   * Get platform display info.
   */
  function getPlatformInfo(platform) {
    return PLATFORM_INFO[platform] || PLATFORM_INFO.other
  }

  /**
   * Extract video info from the backend.
   */
  async function extractInfo(url) {
    isLoading.value = true
    error.value = null
    videoInfo.value = null

    try {
      const info = await getVideoInfo(url)
      videoInfo.value = info
      return info
    } catch (e) {
      error.value = e.message || 'Error al obtener información del video'
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Video formats filtered for display.
   */
  const videoFormats = computed(() => {
    if (!videoInfo.value?.formats) return []
    return videoInfo.value.formats.filter((f) => f.has_video && f.quality !== 'audio_only')
  })

  const audioFormats = computed(() => {
    if (!videoInfo.value?.formats) return []
    return videoInfo.value.formats.filter((f) => f.quality === 'audio_only' || !f.has_video)
  })

  /**
   * Reset state.
   */
  function reset() {
    videoInfo.value = null
    isLoading.value = false
    error.value = null
  }

  return {
    videoInfo,
    isLoading,
    error,
    detectPlatform,
    getPlatformInfo,
    extractInfo,
    videoFormats,
    audioFormats,
    reset,
  }
}
