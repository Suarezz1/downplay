<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  detectedPlatform: { type: String, default: null },
  platformInfo: { type: Object, default: null },
  isLoading: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'analyze'])

const inputRef = ref(null)
const errorMsg = ref('')

const hasValue = computed(() => props.modelValue.trim().length > 0)

function isValidUrl(str) {
  try {
    const url = new URL(str)
    return url.protocol === 'http:' || url.protocol === 'https:'
  } catch {
    return false
  }
}

function handleAnalyze() {
  const url = props.modelValue.trim()
  if (!url) {
    errorMsg.value = 'Ingresa una URL para continuar'
    return
  }
  if (!isValidUrl(url)) {
    errorMsg.value = 'La URL no es válida. Asegúrate de incluir https://'
    return
  }
  errorMsg.value = ''
  emit('analyze', url)
}

function handleInput(e) {
  emit('update:modelValue', e.target.value)
  if (errorMsg.value) errorMsg.value = ''
}

function handleKeydown(e) {
  if (e.key === 'Enter' && !props.isLoading) {
    handleAnalyze()
  }
}

// Clear error when platform changes
watch(() => props.detectedPlatform, () => {
  if (errorMsg.value) errorMsg.value = ''
})
</script>

<template>
  <div class="url-input-wrapper" id="url-input-section">
    <div class="url-input-container" :class="{ 'has-error': errorMsg }">
      <!-- Left icon (link icon or platform icon) -->
      <div class="input-icon-left">
        <template v-if="detectedPlatform">
          <svg v-if="detectedPlatform === 'youtube'" viewBox="0 0 24 24" width="18" height="18" fill="currentColor" style="color: #ff0000;">
            <path d="M23.498 6.163a3.003 3.003 0 0 0-2.11-2.108C19.52 3.5 12 3.5 12 3.5s-7.52 0-9.388.555A3.002 3.002 0 0 0 .502 6.163C0 8.03 0 12 0 12s0 3.97.502 5.837a3.003 3.003 0 0 0 2.11 2.108C4.48 20.5 12 20.5 12 20.5s7.52 0 9.388-.555a3.003 3.003 0 0 0 2.11-2.108C24 15.97 24 12 24 12s0-3.97-.502-5.837zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
          </svg>
          <svg v-else-if="detectedPlatform === 'tiktok'" viewBox="0 0 24 24" width="18" height="18" fill="currentColor" style="color: var(--text-primary);">
            <path d="M12.53.086c.3-.06.63-.086.95-.086a6.83 6.83 0 0 0 4.19 1.45 6.7 6.7 0 0 0 1.25-.13v3.2a3.52 3.52 0 0 1-2.28-.85V12.1a6.6 6.6 0 1 1-6.6-6.6 6.33 6.33 0 0 1 .9.07v3.22a3.44 3.44 0 0 0-.9-.12 3.4 3.4 0 1 0 3.4 3.4v-12c0-.01 0-.02.04-.02z"/>
          </svg>
          <svg v-else-if="detectedPlatform === 'instagram'" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="color: #e1306c;">
            <rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect>
            <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path>
            <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line>
          </svg>
          <svg v-else-if="detectedPlatform === 'facebook'" viewBox="0 0 24 24" width="18" height="18" fill="currentColor" style="color: #1877f2;">
            <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
          </svg>
          <svg v-else-if="detectedPlatform === 'x'" viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="color: var(--text-primary);">
            <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
        </template>
        <span v-else class="link-icon">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
            <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
          </svg>
        </span>
      </div>

      <input
        ref="inputRef"
        type="url"
        class="url-input"
        :value="modelValue"
        @input="handleInput"
        @keydown="handleKeydown"
        placeholder="Pega el enlace del video aquí..."
        autocomplete="off"
        spellcheck="false"
        id="url-input"
      />

      <button
        class="analyze-btn"
        id="analyze-btn"
        :disabled="!hasValue || isLoading"
        @click="handleAnalyze"
      >
        <span v-if="isLoading" class="spinner"></span>
        <template v-else>
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 2px;">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <span>Analizar</span>
        </template>
      </button>
    </div>

    <p v-if="errorMsg" class="input-error animate-shake">{{ errorMsg }}</p>
  </div>
</template>
