<template>
  <div class="flex w-full h-full gap-1 items-center">
    <template v-if="isReadOnly">
      <slot />
    </template>
    <template v-if="!isEditing">
      <div class="flex-1">
        <slot />
      </div>
      <BaseButton @click="switchToEditMode" size="xs" btn-type="outline">
        <Icon name="uil:pen" />
      </BaseButton>
    </template>
    <template v-else-if="props.uiMode.type === 'textbox'">
      <textarea v-if="props.uiMode.rows > 1" :id="props.fieldName" v-model="valueStringRef" :rows="props.uiMode.rows"
        class="px-2 py-1 flex-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-black dark:bg-black dark:text-white"
        :placeholder="props.uiMode.placeholder" />
      <input v-if="props.uiMode.rows === 1" :type="props.uiMode.isNumber ? 'number' : 'text'" :id="props.fieldName"
        v-model="valueStringRef" :class="[
          'px-2 py-1 flex-1 min-w-0 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-black dark:bg-black dark:text-white',
          props.uiMode.isNumber ? 'input-number-no-spinners' : '',
        ]" :placeholder="props.uiMode.placeholder" />
      <div class="flex flex-col gap-1 h-full justify-between">
        <BaseButton @click="isEditing = false" size="xs" btn-type="cancel" aria-label="Cancel editting">
          Cancel
        </BaseButton>
        <BaseButton @click="updateValue" btn-type="default" size="xs">
          Save
          <Icon v-if="isSaving" name="ei:spinner-3" size="1rem" class="animate-spin align-sub" />
        </BaseButton>
      </div>
    </template>
    <template v-else-if="props.uiMode.type === 'checkbox'">
      <div class="flex-1 flex flex-row justify-center">
        <label>
          {{ props.uiMode.label }}
          <input :aria-label="props.uiMode.label" type="checkbox" :id="props.fieldName" v-model="valueBooleanRef"
            :class="[
              'pointer-click border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-black dark:bg-black dark:text-white',
            ]" />
        </label>
      </div>
      <div class="flex flex-col gap-1 h-full justify-between">
        <BaseButton @click="isEditing = false" size="xs" btn-type="cancel" aria-label="Cancel editting">
          Cancel
        </BaseButton>
        <BaseButton @click="updateValue" btn-type="default" size="xs">
          Save
          <Icon v-if="isSaving" name="ei:spinner-3" size="1rem" class="animate-spin align-sub" />
        </BaseButton>
      </div>
    </template>
    <template v-else-if="props.uiMode.type === 'select'">
      <select :id="props.fieldName" v-model="valueStringRef"
        class="px-2 py-1 flex-1 min-w-0 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-black dark:bg-black dark:text-white">
        <option v-if="typeof props.uiMode.options === 'function' && selectOptions.length === 0" readonly value="">
          loading</option>
        <option v-for="(option, index) in selectOptions" :key="index" :value="option.value">
          {{ option.label }}
        </option>
      </select>
      <div class="flex flex-col gap-1 h-full justify-between">
        <BaseButton @click="isEditing = false" size="xs" btn-type="cancel" aria-label="Cancel editting">Cancel
        </BaseButton>
        <BaseButton @click="updateValue" btn-type="default" size="xs">
          Save
          <Icon v-if="isSaving" name="ei:spinner-3" size="1rem" class="animate-spin align-sub" />
        </BaseButton>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { RfcToBe, PatchedRfcToBeRequest } from '~/purple_client'
import { snackbarForErrors } from '~/utils/snackbar'

type UIMode =
  | { type: 'textbox', rows: number, placeholder: string, isNumber?: boolean, initialValue?: string }
  | { type: 'checkbox', label: string, initialValue?: boolean }
  | {
    type: 'select'
    options: SelectOption[] | (() => Promise<SelectOption[]>)
    initialValue?: string
  }

type Props = {
  draftName: NonNullable<RfcToBe["name"]>
  isReadOnly: boolean
  uiMode: UIMode
  fieldName: keyof PatchedRfcToBeRequest
  onSuccess?: () => Promise<void>
}

const props = defineProps<Props>()

const api = useApi()
const snackbar = useSnackbar()

const valueStringRef = ref<string>(props.uiMode.type === 'select' || props.uiMode.type === 'textbox' ? props.uiMode.initialValue ?? '' : '')
const valueBooleanRef = ref<boolean>(props.uiMode.type === 'checkbox' ? props.uiMode.initialValue ?? false : false)

const isEditing = ref(false)
const isSaving = ref(false)

const selectOptions = ref<SelectOption[]>(props.uiMode.type === 'select' ? typeof props.uiMode.options === 'function' ? [] : props.uiMode.options : [])

const switchToEditMode = async () => {
  isEditing.value = true
  if (props.uiMode.type === 'select' && typeof props.uiMode.options === 'function' && selectOptions.value.length === 0) {
    selectOptions.value = await props.uiMode.options()
    if (props.uiMode.initialValue) {
      valueStringRef.value = props.uiMode.initialValue
    }
  }
}

const updateValue = async () => {
  const { fieldName } = props
  if (!fieldName) {
    snackbar.add({ type: 'error', title: `Expected 'fieldName' prop`, text: '' })
    return
  }
  isSaving.value = true
  try {
    switch (props.uiMode.type) {
      case 'select':
      case 'textbox':
        await api.documentsPartialUpdate({
          draftName: props.draftName,
          patchedRfcToBeRequest: {
            [fieldName]: valueStringRef.value
          }
        })
        break
      case 'checkbox':
        await api.documentsPartialUpdate({
          draftName: props.draftName,
          patchedRfcToBeRequest: {
            [fieldName]: valueBooleanRef.value
          }
        })
        break
    }
    if (props.onSuccess) {
      await props.onSuccess()
    }
    snackbar.add({ type: 'success', title: `${JSON.stringify(fieldName)} updated`, text: '' })
    isEditing.value = false
  } catch (error: unknown) {
    snackbarForErrors({ snackbar, error, defaultTitle: `Failed to update ${JSON.stringify(fieldName)}` })
  }
  isSaving.value = false
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
