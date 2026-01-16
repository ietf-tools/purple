<template>
  <div class="w-full flex gap-1 items-center">
    <textarea
      id="title"
      v-model="title"
      type="text"
      rows="5"
      class="px-2 py-1 flex-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-black dark:bg-black dark:text-white"
      placeholder="title"
    />
    <BaseButton @click="updateTitle" btn-type="outline" size="xs">Save</BaseButton>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { RfcToBe } from '~/purple_client'
import { snackbarForErrors } from '~/utils/snackbar'

const props = defineProps<{
  draftName: NonNullable<RfcToBe["name"]>
  initialTitle?: string
  onSuccess: () => void
}>()

const api = useApi()
const snackbar = useSnackbar()

const title = ref(props.initialTitle)

const updateTitle = async () => {
  try {
    await api.documentsPartialUpdateRaw({
      draftName: props.draftName,
      patchedRfcToBeRequest: {
        title: title.value
      }
    })
    snackbar.add({ type: 'success', title: `Title updated`, text: '' })
    props.onSuccess()
  } catch (error: unknown) {
    snackbarForErrors({ snackbar, error, defaultTitle: `Failed to update title` })
  }
}
</script>

<style>
.input-number-no-spinners,
.input-number-no-spinners::-webkit-inner-spin-button,
.input-number-no-spinners::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
</style>
