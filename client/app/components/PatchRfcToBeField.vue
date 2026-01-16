<template>
  <div class="w-full flex gap-1 items-center">
    <template v-if="props.uiMode.type === 'textbox'">
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
        type="text"
        :id="props.key"
        v-model="valueRef"
        class="px-2 py-1 flex-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-black dark:bg-black dark:text-white"
        :placeholder="props.uiMode.placeholder"
      />
    </template>
    <template v-else-if="props.uiMode.type === 'select'">
      <select
        :id="props.key"
        v-model="valueRef"
        class="px-2 py-1 flex-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-black dark:bg-black dark:text-white"
      >
        <option v-for="(option, index) in props.uiMode.options" :key="index" :value="option.value">
          {{ option.label }}
        </option>
      </select>
    </template>
    <BaseButton @click="updateValue" btn-type="outline" size="xs">Save</BaseButton>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { startCase } from 'lodash-es'
import type { RfcToBe, PatchedRfcToBeRequest } from '~/purple_client'
import { snackbarForErrors } from '~/utils/snackbar'

type UIMode =
  | { type: 'textbox', rows: number, placeholder: string }
  | {
    type: 'select'
    options: { value: string, label: string }[]
  }

const props = defineProps<{
  draftName: NonNullable<RfcToBe["name"]>
  initialValue?: string
  uiMode: UIMode
  key: keyof PatchedRfcToBeRequest
  onSuccess: () => void
}>()

const api = useApi()
const snackbar = useSnackbar()

const valueRef = ref(props.initialValue)

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
