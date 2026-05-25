<template>
  <form>
    <div class="bg-white dark:bg-neutral-900 h-full dark:text-white">
      <!-- Should this be part of the overlay control with this control just passing a title? -->
      <div class="bg-violet-700 bg-gradient-to-tr from-violet-800 to-violet-600 px-4 pr-2 py-4 sm:pl-6">
        <div class="flex items-center justify-between">
          <HeadlessDialogTitle class="text-base font-semibold leading-6 text-white">Edit Label</HeadlessDialogTitle>
          <div class="ml-3 flex h-7 items-center">
            <button
              type="button"
              class="mr-3 inline-flex items-center gap-x-1.5 rounded-md bg-violet-500 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-violet-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-300 bg-opacity-50"
              @click="cancel"
            >
              <Icon name="uil:times" class="h-6 w-6 -ml-1" aria-hidden="true"/>
              <span>Discard</span>
            </button>
            <button
              type="button"
              class="inline-flex items-center gap-x-1.5 rounded-md bg-violet-500 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-violet-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-300 bg-opacity-50"
              @click="save"
            >
              <Icon name="uil:check" class="h-6 w-6 -ml-1" aria-hidden="true"/>
              <span>Save</span>
            </button>
          </div>
        </div>
      </div>

      <div
        class="mt-10 space-y-8 border-b border-gray-900/10 p-6 sm:space-y-0 sm:divide-y sm:divide-gray-900/10 sm:border-t sm:pb-0">

        <div class="sm:grid sm:grid-cols-3 sm:items-start sm:gap-4 sm:py-6">
          <label for="slug" class="block text-sm font-medium leading-6 text-gray-900 sm:pt-1.5">Label Name</label>
          <div class="mt-2 sm:col-span-2 sm:mt-0">
            <div
              class="flex rounded-md shadow-sm ring-1 ring-inset ring-gray-300 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-600 sm:max-w-md">
              <input
                id="slug" v-model="label.slug" type="text" name="slug"
                class="block flex-1 border-0 bg-transparent py-1.5 pl-1 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6"
                placeholder="e.g. 'markdown'">
            </div>
          </div>
        </div>

        <div class="sm:grid sm:grid-cols-3 sm:items-start sm:gap-4 sm:py-6">
          <label for="is-exception" class="block text-sm font-medium leading-6 text-gray-900 sm:pt-1.5">
            Is Exception
          </label>
          <div class="mt-2 sm:col-span-2 sm:mt-0">
            <input
              id="is-exception" v-model="label.isException" name="is-exception" type="checkbox"
              class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600">
            <p class="text-gray-500">This label indicates an exception.</p>
          </div>
        </div>

        <div class="sm:grid sm:grid-cols-3 sm:items-start sm:gap-4 sm:py-6">
          <label for="is-complexity" class="block text-sm font-medium leading-6 text-gray-900 sm:pt-1.5">
            Is Complexity
          </label>
          <div class="mt-2 sm:col-span-2 sm:mt-0">
            <input
              id="is-complexity" v-model="label.isComplexity" name="is-complexity" type="checkbox"
              class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600">
            <p class="text-gray-500">This label indicates a complexity.</p>
          </div>
        </div>

        <div class="sm:grid sm:grid-cols-3 sm:items-start sm:gap-4 sm:py-6">
          <label class="block text-sm font-medium leading-6 text-gray-900 sm:pt-1.5">Color</label>
          <div class="mt-2 sm:col-span-2 sm:mt-0">
            <HeadlessListbox v-model="label.color" as="div" class="relative sm:max-w-xs">
              <HeadlessListboxButton
                class="relative w-full cursor-default rounded-md bg-white py-1.5 pl-3 pr-10 text-left text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6"
              >
                <span :class="['inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset', badgeColors[label.color as ColorEnum]]">
                  {{ label.color }}
                </span>
                <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
                  <Icon name="heroicons:chevron-up-down-solid" class="h-5 w-5 text-gray-400" aria-hidden="true" />
                </span>
              </HeadlessListboxButton>
              <transition leave-active-class="transition ease-in duration-100" leave-from-class="opacity-100" leave-to-class="opacity-0">
                <HeadlessListboxOptions class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
                  <HeadlessListboxOption v-for="color in ColorEnum" :key="color" :value="color" v-slot="{ active, selected }">
                    <div :class="['flex cursor-default select-none items-center px-3 py-2 gap-2', active ? 'bg-gray-100' : '']">
                      <span :class="['inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset', badgeColors[color]]">
                        {{ color }}
                      </span>
                      <Icon v-if="selected" name="heroicons:check-solid" class="h-4 w-4 text-indigo-600" />
                    </div>
                  </HeadlessListboxOption>
                </HeadlessListboxOptions>
              </transition>
            </HeadlessListbox>
          </div>
        </div>

        <div class="sm:grid sm:grid-cols-3 sm:items-start sm:gap-4 sm:py-6">
          <label for="is-used" class="block text-sm font-medium leading-6 text-gray-900 sm:pt-1.5">
            Is Assignable
          </label>
          <div class="mt-2 sm:col-span-2 sm:mt-0">
            <input
              id="is-used" v-model="label.used" name="is-used" type="checkbox"
              class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600">
            <p class="text-gray-500">This label is assignable and actively in use.</p>
          </div>
        </div>
      </div>
    </div>

  </form>
</template>

<script setup lang="ts">
import { ColorEnum } from '~/purple_client'
import type { Label } from '~/purple_client'
import { badgeColors } from '~/utils/badge'
import { overlayModalMethodsKey } from '../providers/providerKeys'

const api = useApi()

const _overlayModalMethods = inject(overlayModalMethodsKey)
if (!_overlayModalMethods) {
  throw Error('Expected injection of overlayModalMethods')
}
const { ok, cancel } = _overlayModalMethods
const snackbar = useSnackbar()

type Props = { label: Label | undefined }
const props = defineProps<Props>()

const NEW_LABEL_DEFAULTS: Label = {
  slug: '',
  isException: false,
  color: 'slate',
  used: true
}

const label = reactive<Label>(
  props.label ? { ...props.label } : NEW_LABEL_DEFAULTS
)

async function save() {
  try {
    if (label.id === undefined) {
      await api.labelsCreate({ labelRequest: label })
    } else {
      await api.labelsUpdate({ id: label.id, labelRequest: label })
    }
  } catch {
    snackbar.add({
      type: 'error',
      title: 'Save not successful',
      text: 'Something is wrong with the data - either the label name is blank or a label with that name already exists'
    })
  }
  ok()
}
</script>
