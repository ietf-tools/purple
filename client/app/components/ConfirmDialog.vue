<template>
  <HeadlessTransitionRoot as="template" :show="isShown">
    <HeadlessDialog as="div" class="relative z-[100]" @close="close">
      <HeadlessTransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500 dark:bg-black bg-opacity-75 dark:bg-opacity-50 transition-opacity backdrop-blur" />
      </HeadlessTransitionChild>

      <div class="fixed inset-0 z-10 overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <HeadlessTransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from="opacity-100 translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
            <HeadlessDialogPanel class="relative transform overflow-hidden rounded-lg bg-white dark:bg-neutral-900 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg">
              <div class="bg-white dark:bg-neutral-900 px-4 pb-4 pt-5 sm:p-6 sm:pb-4">
                <div class="sm:flex sm:items-start">
                  <div class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-rose-100 dark:bg-rose-600 sm:mx-0 sm:h-10 sm:w-10">
                    <Icon name="uil:exclamation-triangle" class="h-6 w-6 text-rose-600 dark:text-rose-50" aria-hidden="true" />
                  </div>
                  <div class="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left">
                    <HeadlessDialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900 dark:text-neutral-100">{{ title }}</HeadlessDialogTitle>
                    <div class="mt-2">
                      <p class="text-sm text-gray-500 dark:text-neutral-400">{{ caption }}</p>
                    </div>
                  </div>
                </div>
              </div>
              <div class="bg-gray-50 dark:bg-neutral-800 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
                <button type="button" class="inline-flex w-full justify-center rounded-md bg-rose-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-rose-500 sm:ml-3 sm:w-auto" @click="close">Confirm</button>
                <button type="button" class="btn-secondary" @click="close">Cancel</button>
              </div>
            </HeadlessDialogPanel>
          </HeadlessTransitionChild>
        </div>
      </div>
    </HeadlessDialog>
  </HeadlessTransitionRoot>
</template>

<script setup lang="ts">
// PROPS / EMITS

type Props = {
  isShown: boolean
  title?: string
  caption?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Confirm',
  caption: 'Are you sure you want to continue?'
})

const emit = defineEmits(['update:isShown'])

// METHODS

function close () {
  emit('update:isShown', false)
}

</script>
