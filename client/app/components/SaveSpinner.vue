<template>
  <TooltipProvider>
    <TooltipRoot>
      <TooltipTrigger type="button" :style="`font-size:${props.size}; width: ${props.size}; height: ${props.size}`" class="text-black dark:text-white relative">
        <Icon v-if="throttledStatus === 'pending'" name="ei:spinner-3" :size="props.size" class="absolute top-0 left-0 animate-spin" />
        <Icon v-else-if="throttledStatus === 'success'" name="heroicons:check" :size="props.size" class="absolute top-0 left-0" />
        <Icon v-else-if="throttledStatus === 'error'" name="ei:exclamation" :size="props.size" class="absolute top-0 left-0" />
      </TooltipTrigger>
      <TooltipPortal>
        <TooltipContent class="shadow-md bg-white text-black dark:bg-black dark:text-white rounded px-2 py-1">
          <span v-if="throttledStatus === 'idle'"></span>
          <span v-else-if="throttledStatus === 'pending'">Pending...</span>
          <span v-else-if="throttledStatus === 'success' ">Success</span>
          <span v-else-if="throttledStatus === 'error' ">
            Error: {{ saveStatusError }}
          </span>
        </TooltipContent>
      </TooltipPortal>
    </TooltipRoot>
  </TooltipProvider>
</template>

<script setup lang="ts">
import { TooltipContent, TooltipPortal, TooltipProvider, TooltipRoot, TooltipTrigger } from 'reka-ui'
import { type SaveStatus, type SaveStatusError } from '../utils/save-spinner'
import { watchThrottled } from '@vueuse/core'

type Props = {
  size?: string
}

const saveStatus = defineModel<SaveStatus>('status', { required: true })
const saveStatusError = defineModel<SaveStatusError>('error', { required: false })

const props = withDefaults(defineProps<Props>(),  { size: '1.2rem' })

const throttledStatus = ref<SaveStatus>(saveStatus.value)

watchThrottled(
  saveStatus,
  () => {
    throttledStatus.value = saveStatus.value
  },
  { throttle: 1000 }
)
</script>
