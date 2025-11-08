<template>
  <HeadlessListboxOption v-slot="{ active, selected }" as="template">
    <li
      :class="[active ? 'bg-indigo-600 text-white' : 'text-gray-900', 'relative cursor-default select-none py-2 pl-8 pr-4']">
      <span :class="[selected ? 'font-semibold' : 'font-normal', 'block truncate']">{{ name }}</span>
      <p v-if="desc" :class="[active ? 'text-indigo-200' : 'text-gray-500', 'ml-2']">{{ desc }}</p>

      <span
        v-if="selected"
        :class="[active ? 'text-white' : 'text-indigo-600', 'absolute inset-y-0 left-1 flex items-center pr-1.5']">
                            <Icon name="heroicons:check" class="h-5 w-5" aria-hidden="true"/>
                          </span>
    </li>
  </HeadlessListboxOption>

</template>

<script setup lang="ts">
type Props = {
  /**
   * Display name
   */
  name: string,
  /**
   * Extended description of the option
   */
  desc?: string
}

defineProps<Props>()

</script>
