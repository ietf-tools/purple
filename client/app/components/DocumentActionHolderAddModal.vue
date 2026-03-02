<template>
  <div
    class="h-full bg-gray-100 text-black dark:bg-gray-800 dark:text-black flex flex-col justify-between gap-5 px-2 pt-10 pb-2">
    <BaseButton btnType="outline" class="absolute right-1 top-1 z-50" @click="closeOverlayModal">
      <Icon name="uil:times" class="h-5 w-5" aria-hidden="true" />
    </BaseButton>
    <form novalidate class="border rounded-md border-gray-500 bg-white dark:bg-black">
      <Heading :heading-level="3" class="p-5">
        Add Action Holder
      </Heading>
      <div class="flex flex-col gap-3 justify-between">
        <div class="flex flex-col gap-3 px-5">
          <DialogFieldPickAuthor v-model="person" id="person" label="Person" :disabled="isSuccess"
            person-term="action holder" />
          <DialogFieldDate v-model="deadlineDateString" id="deadline" label="Deadline" :disabled="isSuccess" />
          <div class="flex flex-row items-start">
            <label for="body"
              class="text-gray-900 dark:text-gray-200 w-[160px] text-right text-sm font-bold mr-1 pt-1">Body:</label>
            <input v-model="body" id="body" type="text" maxlength="64" :disabled="isSuccess"
              class="flex-1 text-sm border border-gray-400 rounded px-2 py-1 bg-white dark:bg-gray-900 dark:text-white"
              placeholder="Body (optional if no person provided)" />
          </div>
          <div class="flex flex-row items-start">
            <label for="comment"
              class="text-gray-900 dark:text-gray-200 w-[160px] text-right text-sm font-bold mr-1 pt-1">Comment:</label>
            <textarea v-model="comment" id="comment" rows="3" :disabled="isSuccess"
              class="flex-1 text-sm border border-gray-400 rounded px-2 py-1 bg-white dark:bg-gray-900 dark:text-white resize-y"
              placeholder="Optional comment" />
          </div>
        </div>

        <div
          class="flex flex-row items-center justify-end px-5 py-3 border-t-2 border-gray-500 bg-gray-200 dark:bg-gray-800">
          <BaseButton btn-type="default" @click="add" :hidden="isSuccess">Add Action Holder</BaseButton>
          <b v-if="isSuccess" class="text-green-800 font-bold ml-3" aria-atomic aria-live="polite">Action Holder Added</b>
        </div>
      </div>
    </form>
  </div>
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
