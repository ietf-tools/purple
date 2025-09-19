<template>
  <div class="flex justify-center items-center">
    <TabNav :tabs="tabs" :selected="props.currentTab" />
  </div>
</template>

<script setup lang="ts">
import type { TabId } from '../utils/queue'
import { tabs } from '~/utils/queue'

type Props = {
  currentTab: TabId
}

const props = defineProps<Props>()
</script>
