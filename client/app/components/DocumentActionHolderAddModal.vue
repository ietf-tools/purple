<template>
  <form novalidate class="text-black dark:text-white" @submit.prevent>
    <div class="flex items-center justify-between border-b border-gray-200 dark:border-gray-700 px-6 py-4">
      <Heading :heading-level="3">Add Action Holder</Heading>
      <BaseButton btnType="outline" @click="closeOverlayModal">
        <Icon name="uil:times" class="h-5 w-5" aria-hidden="true" />
      </BaseButton>
    </div>

    <div class="flex flex-col gap-4 px-6 py-5">
      <DialogFieldPickAuthor v-model="person" id="person" label="Person" :disabled="isSuccess"
        person-term="action holder" />
      <DialogFieldDate v-model="deadlineDateString" id="deadline" label="Deadline" :disabled="isSuccess" />

      <div class="flex flex-row items-start">
        <label for="body" class="text-gray-900 dark:text-gray-200 w-[160px] text-right text-sm font-bold mr-3 pt-1">Action:</label>
        <input v-model="body" id="body" type="text" maxlength="64" :disabled="isSuccess"
          class="flex-1 text-sm border border-gray-300 dark:border-gray-600 rounded px-2 py-1 bg-white dark:bg-neutral-800 dark:text-white disabled:opacity-50"
          placeholder="Short description (optional)" />
      </div>

      <div class="flex flex-row items-start">
        <label for="comment" class="text-gray-900 dark:text-gray-200 w-[160px] text-right text-sm font-bold mr-3 pt-1">Comment:</label>
        <textarea v-model="comment" id="comment" rows="3" :disabled="isSuccess"
          class="flex-1 text-sm border border-gray-300 dark:border-gray-600 rounded px-2 py-1 bg-white dark:bg-neutral-800 dark:text-white resize-y disabled:opacity-50"
          placeholder="Optional comment" />
      </div>
    </div>

    <div class="flex flex-row items-center justify-end px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 rounded-b-xl gap-3">
      <b v-if="isSuccess" class="text-green-700 dark:text-green-400 font-bold" aria-atomic aria-live="polite">Action Holder Added</b>
      <BaseButton btn-type="default" @click="add" :hidden="isSuccess">Add Action Holder</BaseButton>
    </div>
  </form>
</template>

<script setup lang="ts">
import type { BaseDatatrackerPerson } from '~/purple_client'
import { overlayModalKey } from '~/providers/providerKeys'
import { inputTypeDateToDateTime } from '~/utils/form'

type Props = {
  draftName: string
  onSuccess: () => Promise<void>
}

const props = defineProps<Props>()
const snackbar = useSnackbar()
const api = useApi()

const overlayModalKeyInjection = inject(overlayModalKey)
if (!overlayModalKeyInjection) throw Error('Expected injection of overlayModalKey')
const { closeOverlayModal } = overlayModalKeyInjection

const isSuccess = ref(false)
const person = ref<BaseDatatrackerPerson | undefined>()
const deadlineDateString = ref<string | undefined>()
const body = ref('')
const comment = ref('')

const add = async () => {
  const personId = person.value?.personId
  if (personId === undefined) {
    snackbar.add({ type: 'error', title: 'A person is required', text: '' })
    return
  }

  let deadline: Date | null | undefined = null
  if (deadlineDateString.value) {
    const dt = inputTypeDateToDateTime(deadlineDateString.value)
    if (!dt.isValid) {
      snackbar.add({ type: 'error', title: 'Invalid deadline date', text: '' })
      return
    }
    deadline = dt.toJSDate()
  }

  try {
    await api.documentsActionHoldersCreate({
      draftName: props.draftName,
      createActionHolderRequest: {
        personId,
        deadline,
        comment: comment.value,
        body: body.value,
      },
    })
    isSuccess.value = true
    snackbar.add({ type: 'success', title: 'Action holder added', text: '' })
    await props.onSuccess()
    closeOverlayModal()
  } catch (e) {
    snackbarForErrors({ snackbar, defaultTitle: 'Problem adding action holder', error: e })
  }
}
</script>
