<template>
  <div class="flex justify-center items-center">
    <TabNav :tabs="docTabs" :selected="props.currentTab" />
  </div>
</template>

<script setup lang="ts">
import type { QueueTabId } from '../utils/queue'
import { docTabsFactory } from '~/utils/doc'

type Props = {
  currentTab: QueueTabId
  draftName: string
}

const props = defineProps<Props>()

const docTabs = computed(() => docTabsFactory(props.draftName))
</script>
