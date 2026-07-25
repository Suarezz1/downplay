<script setup>
import { ref, computed, watch } from 'vue'
import AppHeader from './components/AppHeader.vue'
import UrlInput from './components/UrlInput.vue'
import VideoPreview from './components/VideoPreview.vue'
import FormatSelector from './components/FormatSelector.vue'
import DownloadButton from './components/DownloadButton.vue'
import { useVideoInfo } from './composables/useVideoInfo'
import { useDownloader } from './composables/useDownloader'

// Video info composable
const {
  videoInfo,
  isLoading: isExtracting,
  error: extractError,
  detectPlatform,
  getPlatformInfo,
  extractInfo,
  videoFormats,
  audioFormats,
  reset: resetVideoInfo,
} = useVideoInfo()

// Downloader composable
const {
  status: downloadStatus,
  progress: downloadProgress,
  errorMessage: downloadError,
  download,
  reset: resetDownloader,
} = useDownloader()

// Local state
const url = ref('')
const selectedFormatId = ref(null)
const audioOnly = ref(false)

// Detected platform (reactive as user types)
const detectedPlatform = computed(() => detectPlatform(url.value))
const platformInfo = computed(() => {
  const p = detectedPlatform.value || videoInfo.value?.platform
  return p ? getPlatformInfo(p) : null
})

// Supported platforms for hero badges
const platforms = [
  { key: 'youtube', name: 'YouTube' },
  { key: 'tiktok', name: 'TikTok' },
  { key: 'instagram', name: 'Instagram' },
  { key: 'facebook', name: 'Facebook' },
  { key: 'x', name: 'X (Twitter)' },
]

// Auto-select best format when info loads
watch(videoFormats, (formats) => {
  if (formats.length > 0 && !selectedFormatId.value) {
    selectedFormatId.value = formats[0].format_id
  }
})

async function handleAnalyze(inputUrl) {
  resetDownloader()
  selectedFormatId.value = null
  audioOnly.value = false
  await extractInfo(inputUrl)
}

function handleSelectFormat(formatId) {
  selectedFormatId.value = formatId
}

function handleToggleAudio(isAudio) {
  audioOnly.value = isAudio
  if (isAudio) {
    selectedFormatId.value = null
  } else if (videoFormats.value.length > 0) {
    selectedFormatId.value = videoFormats.value[0].format_id
  }
}

function handleDownload() {
  download({
    url: url.value,
    formatId: audioOnly.value ? null : selectedFormatId.value,
    audioOnly: audioOnly.value,
  })
}

function handleFullReset() {
  url.value = ''
  selectedFormatId.value = null
  audioOnly.value = false
  resetVideoInfo()
  resetDownloader()
}
</script>

<template>
  <div id="app">
    <!-- Background decoration -->
    <div class="bg-decoration" aria-hidden="true"></div>

    <!-- Header -->
    <AppHeader />

    <!-- Main Content -->
    <main class="container" style="position: relative; z-index: 1;">
      <!-- Hero section -->
      <section class="hero-section animate-fade-in" id="hero-section">
        <h1 class="hero-title">
          Descarga videos de
          <span class="gradient-text">cualquier red social</span>
        </h1>
        <p class="hero-subtitle">
          YouTube, TikTok, Instagram, Facebook y X. Pega el enlace y descarga en máxima calidad.
        </p>

        <!-- Platform badges -->
        <div class="platform-badges stagger-children">
          <span
            v-for="p in platforms"
            :key="p.key"
            class="platform-badge animate-slide-up"
          >
            <span class="badge-icon-svg">
              <svg v-if="p.key === 'youtube'" viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="color: #ff0000;">
                <path d="M23.498 6.163a3.003 3.003 0 0 0-2.11-2.108C19.52 3.5 12 3.5 12 3.5s-7.52 0-9.388.555A3.002 3.002 0 0 0 .502 6.163C0 8.03 0 12 0 12s0 3.97.502 5.837a3.003 3.003 0 0 0 2.11 2.108C4.48 20.5 12 20.5 12 20.5s7.52 0 9.388-.555a3.003 3.003 0 0 0 2.11-2.108C24 15.97 24 12 24 12s0-3.97-.502-5.837zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
              </svg>
              <svg v-else-if="p.key === 'tiktok'" viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="color: var(--text-primary);">
                <path d="M12.53.086c.3-.06.63-.086.95-.086a6.83 6.83 0 0 0 4.19 1.45 6.7 6.7 0 0 0 1.25-.13v3.2a3.52 3.52 0 0 1-2.28-.85V12.1a6.6 6.6 0 1 1-6.6-6.6 6.33 6.33 0 0 1 .9.07v3.22a3.44 3.44 0 0 0-.9-.12 3.4 3.4 0 1 0 3.4 3.4v-12c0-.01 0-.02.04-.02z"/>
              </svg>
              <svg v-else-if="p.key === 'instagram'" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="color: #e1306c;">
                <rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect>
                <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path>
                <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line>
              </svg>
              <svg v-else-if="p.key === 'facebook'" viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="color: #1877f2;">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
              <svg v-else-if="p.key === 'x'" viewBox="0 0 24 24" width="14" height="14" fill="currentColor" style="color: var(--text-primary);">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
              </svg>
            </span>
            <span>{{ p.name }}</span>
          </span>
        </div>
      </section>

      <!-- URL Input -->
      <UrlInput
        v-model="url"
        :detected-platform="detectedPlatform"
        :platform-info="platformInfo"
        :is-loading="isExtracting"
        @analyze="handleAnalyze"
      />

      <!-- Error from extraction -->
      <p v-if="extractError" class="download-status error" style="text-align: center; margin-bottom: 1.5rem;">
        {{ extractError }}
      </p>

      <!-- Video Preview (skeleton or actual) -->
      <VideoPreview
        :video-info="videoInfo"
        :platform-info="platformInfo"
        :is-loading="isExtracting"
      />

      <!-- Format Selector (only when video info available) -->
      <FormatSelector
        v-if="videoInfo"
        :formats="videoFormats"
        :audio-formats="audioFormats"
        :selected-format-id="selectedFormatId"
        :audio-only="audioOnly"
        @select="handleSelectFormat"
        @toggle-audio="handleToggleAudio"
      />

      <!-- Download Button (only when format selected or audio mode) -->
      <DownloadButton
        v-if="videoInfo && (selectedFormatId || audioOnly)"
        :status="downloadStatus"
        :progress="downloadProgress"
        :error-message="downloadError"
        :disabled="!selectedFormatId && !audioOnly"
        @download="handleDownload"
        @reset="handleFullReset"
      />

      <!-- Feature cards (only when no video is loaded and not loading) -->
      <section v-if="!videoInfo && !isExtracting" class="features-grid stagger-children" id="features-section">
        <div class="feature-card glass animate-slide-up">
          <div class="feature-icon-box">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
            </svg>
          </div>
          <h3 class="feature-title">Alta Velocidad</h3>
          <p class="feature-text">
            Nuestros servidores están optimizados para ofrecerte descargas instantáneas sin límites de ancho de banda.
          </p>
        </div>

        <div class="feature-card glass animate-slide-up">
          <div class="feature-icon-box">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
              <line x1="8" y1="21" x2="16" y2="21"></line>
              <line x1="12" y1="17" x2="12" y2="21"></line>
            </svg>
          </div>
          <h3 class="feature-title">Máxima Calidad</h3>
          <p class="feature-text">
            Descarga en 4K, 1080p o extrae el audio en formatos de alta fidelidad como MP3 a 320kbps.
          </p>
        </div>

        <div class="feature-card glass animate-slide-up">
          <div class="feature-icon-box">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            </svg>
          </div>
          <h3 class="feature-title">Seguro y Privado</h3>
          <p class="feature-text">
            Tu privacidad es lo primero. No guardamos registros de tus descargas ni almacenamos datos personales.
          </p>
        </div>
      </section>
    </main>

    <!-- Footer -->
    <footer class="app-footer" id="app-footer">
      <div class="container footer-grid">
        <div class="footer-left">
          <div class="logo" style="margin-bottom: var(--space-sm);">
            <svg class="logo-icon-svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10" fill="currentColor" fill-opacity="0.1"></circle>
              <polyline points="8 12 12 16 16 12"></polyline>
              <line x1="12" y1="8" x2="12" y2="16"></line>
            </svg>
            <span class="logo-text" style="font-size: 1.15rem;">DownPlay</span>
          </div>
          <p class="footer-desc">La herramienta definitiva para guardar tus videos favoritos de la web.</p>
          <p class="footer-copy">© 2026 DownPlay. Creado para uso personal y educativo.</p>
        </div>
        <div class="footer-right">
          <div class="footer-col">
            <h4>LEGAL</h4>
            <a href="#" class="footer-link">Términos</a>
            <a href="#" class="footer-link">Privacidad</a>
          </div>
          <div class="footer-col">
            <h4>SOPORTE</h4>
            <a href="#" class="footer-link">Contacto</a>
            <a href="#" class="footer-link">Ayuda</a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>
