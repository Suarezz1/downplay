<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, default: 'idle' },
  progress: { type: Number, default: 0 },
  errorMessage: { type: String, default: null },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['download', 'reset'])

const buttonText = computed(() => {
  switch (props.status) {
    case 'downloading':
      return `Descargando... ${Math.round(props.progress)}%`
    case 'processing':
      return 'Procesando...'
    case 'completed':
      return '¡Descarga completa!'
    case 'failed':
      return 'Error en la descarga'
    default:
      return 'Descargar'
  }
})

const isActive = computed(() =>
  ['downloading', 'processing'].includes(props.status)
)

const statusClass = computed(() => {
  if (props.status === 'completed') return 'success'
  if (props.status === 'failed') return 'error'
  return ''
})
</script>

<template>
  <div class="download-section" id="download-section">
    <button
      class="download-btn"
      :class="{ 'animate-gradient': isActive }"
      :disabled="disabled || isActive"
      :id="'download-btn'"
      @click="status === 'completed' || status === 'failed' ? emit('reset') : emit('download')"
    >
      <span v-if="isActive" class="spinner"></span>
      <span v-else class="btn-icon" style="display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; margin-right: 6px;">
        <svg v-if="status === 'completed'" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
        <svg v-else-if="status === 'failed'" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
        <svg v-else viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <polyline points="19 12 12 19 5 12"></polyline>
        </svg>
      </span>
      <span>{{ buttonText }}</span>

      <!-- Progress bar overlay -->
      <div
        v-if="status === 'downloading'"
        class="download-progress-bar"
        :style="{ width: `${progress}%` }"
      ></div>
    </button>

    <!-- Status message -->
    <p v-if="errorMessage" class="download-status error">
      {{ errorMessage }}
    </p>
    <p v-else-if="status === 'completed'" class="download-status success">
      El archivo se descargó en tu carpeta de descargas
    </p>
    <p v-else-if="status === 'downloading'" class="download-status animate-progress-pulse">
      No cierres esta ventana mientras se descarga
    </p>

    <!-- Try again button -->
    <p v-if="status === 'completed' || status === 'failed'" class="download-status">
      <button
        class="analyze-btn"
        style="margin-top: 0.5rem; font-size: 0.85rem; padding: 0.5rem 1.5rem;"
        id="download-reset-btn"
        @click="emit('reset')"
      >
        Descargar otro video
      </button>
    </p>
  </div>
</template>
