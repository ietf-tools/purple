<template>
  <div :id="props.id" :class="{
    'highlight-section': isFlashing
  }">
    <slot />
  </div>
</template>

<script setup lang="ts">
type Props = {
  id: string
}
const props = defineProps<Props>()

const isFlashing = ref(false)

const checkForFlash = () => {
  const hash = document.location.hash.replace(/^#/, '')
  isFlashing.value = hash === props.id
}

onMounted(() => {
  setTimeout(checkForFlash, 250)
  addEventListener("hashchange", checkForFlash)
})

onUnmounted(() => {
  removeEventListener("hashchange", checkForFlash)
})
</script>

<style>
@keyframes flash {
  1%,
  50%,
  99% {
    outline-color: #00558800;
  }

  25%,
  75% {
    outline-color: #005588ff;
  }
}

.highlight-section {
  outline: 2px solid transparent;
  animation-duration: 2s;
  animation-name: flash;
}
</style>
