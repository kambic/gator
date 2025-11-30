<template>
  <button class="btn btn-primary" :class="{ 'loading': loading }" :disabled="loading">
    <slot />
  </button>
</template>

<script setup lang="ts">
defineProps<{ loading: boolean }>()
</script>
