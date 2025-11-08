<template>
  <div class="mt-10 grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
    <div class="sm:col-span-4">
      <HeadlessListbox v-model="model" v-bind="$attrs" as="div">
        <HeadlessListboxLabel class="block text-sm font-medium leading-6 text-gray-900">
          {{ label }}
        </HeadlessListboxLabel>
        <div class="relative mt-2">
          <HeadlessListboxButton
            class="relative w-full cursor-default rounded-md bg-white py-1.5 pl-3 pr-10 text-left text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6">
            <span class="block truncate">{{ model?.name || 'Select&hellip;' }}</span>
            <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
              <Icon name="heroicons:chevron-up-down-solid" class="h-5 w-5 text-gray-400" aria-hidden="true"/>
            </span>
          </HeadlessListboxButton>
          <transition
            leave-active-class="transition ease-in duration-100" leave-from-class="opacity-100"
            leave-to-class="opacity-0">
            <HeadlessListboxOptions
              class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
              <slot/>
            </HeadlessListboxOptions>
          </transition>
        </div>
      </HeadlessListbox>
    </div>
  </div>
</template>

<script setup lang="ts">

// Fallthrough attributes are applied to an internal element via v-bind="$attrs"
defineOptions({ inheritAttrs: false })

type Model = null | ({ name: string } & Record<PropertyKey, unknown>)

const model = defineModel<Model>()

type Props = {
  label: string
}
defineProps<Props>()

</script>
