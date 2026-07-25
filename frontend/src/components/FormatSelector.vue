<script setup>
import { computed } from 'vue'

const props = defineProps({
  formats: { type: Array, default: () => [] },
  audioFormats: { type: Array, default: () => [] },
  selectedFormatId: { type: String, default: null },
  audioOnly: { type: Boolean, default: false },
})

const emit = defineEmits(['select', 'toggle-audio'])

/**
 * Deduplicate video formats by quality label, keeping best of each.
 */
const uniqueVideoFormats = computed(() => {
  const seen = new Set()
  return props.formats.filter((f) => {
    if (seen.has(f.quality)) return false
    seen.add(f.quality)
    return true
  })
})

function formatFilesize(bytes) {
  if (!bytes) return '—'
  if (bytes >= 1_073_741_824) return `${(bytes / 1_073_741_824).toFixed(1)} GB`
  if (bytes >= 1_048_576) return `${(bytes / 1_048_576).toFixed(1)} MB`
  if (bytes >= 1024) return `${(bytes / 1024).toFixed(0)} KB`
  return `${bytes} B`
}

function handleSelect(format) {
  emit('select', format.format_id)
}
</script>

<template>
  <div class="format-selector" id="format-selector">
    <div class="format-selector-card glass">
      <!-- Header with Video/Audio toggle -->
      <div class="format-header">
        <h3 class="format-title">Formato de descarga</h3>
        <div class="format-toggle" id="format-type-toggle">
          <button
            class="format-toggle-btn"
            :class="{ active: !audioOnly }"
            @click="emit('toggle-audio', false)"
          >
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="toggle-icon">
              <path d="M23 7l-7 5 7 5V7z"></path>
              <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
            </svg>
            <span>Video</span>
          </button>
          <button
            class="format-toggle-btn"
            :class="{ active: audioOnly }"
            @click="emit('toggle-audio', true)"
          >
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="toggle-icon">
              <path d="M9 18V5l12-2v13"></path>
              <circle cx="6" cy="18" r="3"></circle>
              <circle cx="18" cy="16" r="3"></circle>
            </svg>
            <span>MP3</span>
          </button>
        </div>
      </div>

      <!-- Video quality grid -->
      <div v-if="!audioOnly" class="format-grid stagger-children" id="video-formats-grid">
        <button
          v-for="format in uniqueVideoFormats"
          :key="format.format_id"
          class="format-option animate-scale-in"
          :class="{ selected: selectedFormatId === format.format_id }"
          :id="`format-${format.format_id}`"
          @click="handleSelect(format)"
        >
          <div class="format-quality">{{ format.quality }}</div>
          <div class="format-details">
            {{ format.ext.toUpperCase() }}
            <template v-if="format.filesize || format.filesize_approx">
              · {{ formatFilesize(format.filesize || format.filesize_approx) }}
            </template>
          </div>
        </button>
      </div>

      <!-- Audio mode info -->
      <div v-else class="format-grid" id="audio-format-info">
        <button
          class="format-option selected"
          id="audio-mp3-option"
        >
          <div class="format-quality">MP3</div>
          <div class="format-details">192 kbps · Mejor calidad</div>
        </button>
      </div>
    </div>
  </div>
</template>
