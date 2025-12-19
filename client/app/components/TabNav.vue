<template>
  <nav
    class="isolate grow flex divide-x divide-gray-200 dark:divide-neutral-950 rounded-lg shadow max-w-7xl my-4"
    aria-label="Tabs"
    >
    <Anchor
      v-for="(tab, tabIdx) in props.tabs"
      :key="tab.id"
      :href="tab.to"
      :class="[
        'group relative min-w-0 flex-1 flex justify-center overflow-hidden py-3 px-4 text-sm font-medium hover:bg-gray-50 hover:dark:bg-neutral-800 focus:z-10',
        tab.id === props.selected ? 'bg-white dark:bg-neutral-800 text-violet-700 dark:text-violet-300' : 'bg-white dark:bg-neutral-700 text-gray-500 dark:text-neutral-300 hover:text-gray-700 hover:dark:text-neutral-200',
        tabIdx === 0 ? 'rounded-l-lg' : '',
        tabIdx === tabs.length - 1 ? 'rounded-r-lg' : '',
      ]"
      :aria-current="tab.id === props.selected ? 'page' : undefined"
      >
      <Icon
        :name="tab.icon"
        :class="[
          'h-5 w-5 mr-2',
          tab.iconAnimate ? `group-hover:animate-spin` : ''
        ]"
        aria-hidden="true"
      />
      <span>{{ tab.name }}</span>
      <span
        aria-hidden="true"
        :class="[
          tab.id === props.selected ? 'bg-violet-500' : 'bg-transparent',
          'absolute inset-x-0 bottom-0 h-0.5'
        ]"
      />
    </Anchor>
  </nav>
</template>

<script setup lang="ts">
import type { Tab } from '~/utils/tab'

type Props = {
  tabs: Tab[]
  selected?: string
}

const props = withDefaults(defineProps<Props>(), {
  tabs: () => []
})

// defineEmits(['update:selected'])

</script>
