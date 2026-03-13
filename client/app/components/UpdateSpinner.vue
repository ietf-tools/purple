<template>
  <TooltipProvider>
    <TooltipRoot>
      <TooltipTrigger>
        <span class="text-black dark:text-white">
          <Icon v-if="props.status === 'idle'" name="ei:question" size="1em" />
          <Icon v-else-if="props.status === 'pending'" name="ei:spinner-3" size="1em" class="animate-spin" />
          <Icon v-else-if="props.status === 'success'" name="heroicons:check" size="1em"  />
          <Icon v-else-if="props.status === 'error'" name="ei:exclamation" size="1em" />
          <Icon v-else name="ei:question" size="1em" :title="props.status"/>
          {{ props.status }}
        </span>
      </TooltipTrigger>
      <TooltipPortal>
        <TooltipContent class="shadow-md bg-white text-black dark:bg-black dark:text-white rounded px-2 py-1">
          <span v-if="props.status === 'idle'"></span>
          <span v-else-if="props.status === 'pending'">Pending...</span>
          <span v-else-if="props.status === 'success' ">Success</span>
          <span v-else-if="props.status === 'error' ">
            Error: {{ props.error }}
          </span>
        </TooltipContent>
      </TooltipPortal>
    </TooltipRoot>
  </TooltipProvider>
</template>

<script setup lang="ts">
import { TooltipContent, TooltipPortal, TooltipProvider, TooltipRoot, TooltipTrigger } from 'reka-ui'
import { type UpdateStatus } from '../utils/update-status'

type Props = {
  status: UpdateStatus
  error?: string
}

const props = defineProps<Props>()
</script>
