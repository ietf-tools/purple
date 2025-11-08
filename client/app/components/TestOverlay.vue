<template>
  <div class="bg-white dark:bg-neutral-900 h-full dark:text-white">
    <!-- Header -->
    <div class="bg-violet-700 bg-gradient-to-tr from-violet-800 to-violet-600 px-4 pr-2 py-4 sm:pl-6">
      <div class="flex items-center justify-between">
        <HeadlessDialogTitle class="text-base font-semibold leading-6 text-white">Gondor calls for aid!</HeadlessDialogTitle>
        <div class="ml-3 flex h-7 items-center">
          <button
            type="button"
            class="mr-3 inline-flex items-center gap-x-1.5 rounded-md bg-violet-500 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-violet-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-300 bg-opacity-50"
            @click="cancel"
            >
            <Icon name="uil:times" class="h-6 w-6 -ml-1" aria-hidden="true" />
            <span>Discard</span>
          </button>
          <button
            type="button"
            class="inline-flex items-center gap-x-1.5 rounded-md bg-violet-500 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-violet-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-300 bg-opacity-50"
            @click="save"
            >
            <Icon name="uil:check" class="h-6 w-6 -ml-1" aria-hidden="true" />
            <span>Save</span>
          </button>
        </div>
      </div>
    </div>

    <div class="p-6">
      AND ROHAN WILL ANSWER!
    </div>
  </div>
</template>

<script setup lang="ts">
import { overlayModalMethodsKey } from '~/providers/providerKeys'

const overlayModalMethods = inject(overlayModalMethodsKey)
if (!overlayModalMethods) {
  throw Error('expected injection of overlayModalMethods')
}
const { ok, cancel } = overlayModalMethods

function save () {
  ok(
    // { beep: true, boop: 1 }
  )
}

</script>
