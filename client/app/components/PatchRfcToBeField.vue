<template>
  <div class="flex w-full h-full gap-1 items-center">
    <template v-if="isReadOnly">
      <slot />
    </template>
    <template v-if="!isEditing">
      <div class="flex-1">
        <slot />
      </div>
      <BaseButton @click="switchToEditMode" size="xs" btn-type="outline"><Icon name="uil:pen" /></BaseButton>
    </template>
    <template v-else-if="props.uiMode.type === 'textbox'">
      <textarea
        v-if="props.uiMode.rows > 1"
        :id="props.key"
        v-model="valueRef"
        :rows="props.uiMode.rows"
        class="px-2 py-1 flex-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-black dark:bg-black dark:text-white"
        :placeholder="props.uiMode.placeholder"
      />
      <input
        v-if="props.uiMode.rows === 1"
        :type="props.uiMode.isNumber ? 'number' : 'text'"
        :id="props.key"
        v-model="valueRef"
        class="px-2 py-1 flex-1 min-w-0 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-black dark:bg-black dark:text-white"
        :placeholder="props.uiMode.placeholder"
      />
      <div class="flex flex-col gap-1 h-full justify-between">
        <BaseButton @click="isEditing = false" size="xs" btn-type="cancel" aria-label="Cancel editting">Cancel</BaseButton>
        <BaseButton @click="updateValue" btn-type="default" size="xs">Save</BaseButton>
      </div>
    </template>
    <template v-else-if="props.uiMode.type === 'select'">
      <select
        :id="props.key"
        v-model="valueRef"
        class="px-2 py-1 flex-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-black dark:bg-black dark:text-white"
      >
        <option v-if="typeof props.uiMode.options === 'function' && selectOptions.length === 0" readonly value="">loading</option>
        <option v-for="(option, index) in selectOptions" :key="index" :value="option.value">
          {{ option.label }}
        </option>
      </select>
      <div class="flex flex-col gap-1 h-full justify-between">
        <BaseButton @click="isEditing = false" size="xs" btn-type="cancel" aria-label="Cancel editting">Cancel</BaseButton>
        <BaseButton @click="updateValue" btn-type="default" size="xs">Save</BaseButton>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { startCase } from 'lodash-es'
import type { RfcToBe, PatchedRfcToBeRequest } from '~/purple_client'
import { snackbarForErrors } from '~/utils/snackbar'

type UIMode =
  | { type: 'textbox', rows: number, placeholder: string, isNumber?: boolean }
  | {
    type: 'select'
    options: SelectOption[] | (() => Promise<SelectOption[]>)
  }

const props = defineProps<{
  draftName: NonNullable<RfcToBe["name"]>
  isReadOnly: boolean
  initialValue?: string
  uiMode: UIMode
  key: keyof PatchedRfcToBeRequest
  onSuccess: () => void
}>()

const api = useApi()
const snackbar = useSnackbar()

const valueRef = ref(props.initialValue)

const isEditing = ref(false)

const selectOptions = ref<SelectOption[]>( props.uiMode.type === 'select' ? typeof props.uiMode.options === 'function' ? [] : props.uiMode.options : [])

const switchToEditMode = async () => {
  isEditing.value = true
  if(props.uiMode.type === 'select' && typeof props.uiMode.options === 'function') {
    selectOptions.value = await props.uiMode.options()
  }
}

const updateValue = async () => {
  try {
    await api.documentsPartialUpdate({
      draftName: props.draftName,
      patchedRfcToBeRequest: {
        [props.key]: valueRef.value
      }
    })
    snackbar.add({ type: 'success', title: `RFC ${startCase(props.key)} updated`, text: '' })
    props.onSuccess()
  } catch (error: unknown) {
    snackbarForErrors({ snackbar, error, defaultTitle: `Failed to update title` })
  }
}
</script>
