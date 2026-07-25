<script setup>
import { computed } from 'vue'
import PlatformBadge from './PlatformBadge.vue'

const props = defineProps({
  videoInfo: { type: Object, default: null },
  platformInfo: { type: Object, default: null },
  isLoading: { type: Boolean, default: false },
})

const formattedDuration = computed(() => {
  if (!props.videoInfo?.duration) return null
  const d = props.videoInfo.duration
  const hours = Math.floor(d / 3600)
  const minutes = Math.floor((d % 3600) / 60)
  const seconds = d % 60
  if (hours > 0) {
    return `${hours}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
  }
  return `${minutes}:${String(seconds).padStart(2, '0')}`
})

const formattedViews = computed(() => {
  const count = props.videoInfo?.view_count
  if (!count) return null
  if (count >= 1_000_000) return `${(count / 1_000_000).toFixed(1)}M vistas`
  if (count >= 1_000) return `${(count / 1_000).toFixed(1)}K vistas`
  return `${count} vistas`
})
</script>

<template>
  <!-- Skeleton loader -->
  <div v-if="isLoading" class="video-preview" id="video-preview-skeleton">
    <div class="video-preview-card glass">
      <div class="skeleton skeleton-thumbnail"></div>
      <div class="video-info">
        <div class="skeleton skeleton-text" style="margin-bottom: 0.5rem"></div>
        <div class="skeleton skeleton-text short"></div>
        <div style="margin-top: auto">
          <div class="skeleton skeleton-text short"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- Video info -->
  <div v-else-if="videoInfo" class="video-preview" id="video-preview">
    <div class="video-preview-card glass">
      <div class="video-thumbnail-wrapper" v-if="videoInfo.thumbnail">
        <img
          :src="videoInfo.thumbnail"
          :alt="videoInfo.title"
          class="video-thumbnail"
          loading="lazy"
        />
        <span v-if="formattedDuration" class="video-duration">
          {{ formattedDuration }}
        </span>
      </div>

      <div class="video-info">
        <h2 class="video-title">{{ videoInfo.title }}</h2>
        <p v-if="videoInfo.uploader" class="video-uploader">
          {{ videoInfo.uploader }}
        </p>
        <div class="video-meta">
          <PlatformBadge
            :platform="videoInfo.platform"
            :platform-info="platformInfo"
          />
          <span v-if="formattedViews">{{ formattedViews }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
