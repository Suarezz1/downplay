/**
 * Composable for dark/light theme management.
 * Persists preference in localStorage, respects system preference.
 */
import { ref, watchEffect } from 'vue'

const STORAGE_KEY = 'downplay-theme'

// Detect system preference
function getSystemPreference() {
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
    return 'light'
  }
  return 'dark'
}

// Load saved preference or use system default
function loadTheme() {
  const saved = localStorage.getItem(STORAGE_KEY)
  return saved || getSystemPreference()
}

// Shared reactive state (singleton)
const theme = ref(loadTheme())

export function useTheme() {
  const isDark = ref(theme.value === 'dark')

  function toggleTheme() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
    isDark.value = theme.value === 'dark'
  }

  // Sync theme to DOM and localStorage
  watchEffect(() => {
    document.documentElement.setAttribute('data-theme', theme.value)
    localStorage.setItem(STORAGE_KEY, theme.value)
    isDark.value = theme.value === 'dark'
  })

  return {
    theme,
    isDark,
    toggleTheme,
  }
}
