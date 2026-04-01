<template>
  <div
    class="h-full bg-gray-100 text-black dark:bg-gray-800 dark:text-black flex flex-col justify-between gap-5 px-2 pt-10 pb-2">
    <BaseButton btnType="outline" class="absolute right-1 top-1 z-50" @click="closeOverlayModal">
      <Icon name="uil:times" class="h-5 w-5" aria-hidden="true" />
    </BaseButton>
    <form novalidate class="border rounded-md border-gray-500 bg-white dark:bg-black">
      <Heading :heading-level="3" class="p-5">
        Edit Action Holder
      </Heading>
      <div class="flex flex-col gap-3 justify-between">
        <div class="flex flex-col gap-3 px-5">
          <div class="flex flex-row items-center">
            <label class="text-gray-900 dark:text-gray-200 w-[160px] text-right text-sm font-bold mr-1">Name:</label>
            <span class="text-sm dark:text-white">{{ props.actionHolder.person?.name ?? '(unknown)' }}</span>
          </div>
          <div class="flex flex-row items-center">
            <label class="text-gray-900 dark:text-gray-200 w-[160px] text-right text-sm font-bold mr-1">Since:</label>
            <span class="text-sm dark:text-white">{{ sinceWhenDisplay }}</span>
          </div>

          <DialogFieldDate v-model="deadlineDateString" id="deadline" label="Deadline" :disabled="isSuccess" />
          <DialogFieldDate v-model="completedDateString" id="completed" label="Date Completed" :disabled="isSuccess" />

          <div class="flex flex-row items-start">
            <label for="body"
              class="text-gray-900 dark:text-gray-200 w-[160px] text-right text-sm font-bold mr-1 pt-1">Action:</label>
            <input v-model="body" id="body" type="text" maxlength="64" :disabled="isSuccess"
              class="flex-1 text-sm border border-gray-400 rounded px-2 py-1 bg-white dark:bg-gray-900 dark:text-white"
              placeholder="Short description (optional)" />
          </div>

          <div class="flex flex-row items-start">
            <label class="text-gray-900 dark:text-gray-200 w-[160px] text-right text-sm font-bold mr-1 pt-1">Comment:</label>
            <textarea
              v-model="comment"
              id="comment"
              rows="3"
              :disabled="isSuccess"
              class="flex-1 text-sm border border-gray-400 rounded px-2 py-1 bg-white dark:bg-gray-900 dark:text-white resize-y"
              placeholder="Optional comment"
            />
          </div>
        </div>

        <div
          class="flex flex-row items-center justify-between px-5 py-3 border-t-2 border-gray-500 bg-gray-200 dark:bg-gray-800">
          <BaseButton btn-type="delete" @click="deleteActionHolder" :hidden="isSuccess || isDeleted">Delete</BaseButton>
          <div class="flex flex-row items-center">
            <BaseButton btn-type="default" @click="save" :hidden="isSuccess || isDeleted">Save</BaseButton>
            <b v-if="isSuccess" class="text-green-800 font-bold ml-3" aria-atomic aria-live="polite">Saved</b>
            <b v-if="isDeleted" class="text-green-800 font-bold ml-3" aria-atomic aria-live="polite">Deleted</b>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { DateTime } from 'luxon'
import type { ActionHolder } from '~/purple_client'
import { overlayModalKey } from '~/providers/providerKeys'
import { inputTypeDateToDateTime, jsDateToInputTypeDate } from '~/utils/form'

type Props = {
  actionHolder: ActionHolder
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
const isDeleted = ref(false)

const deadlineDateString = ref<string | undefined>(
  props.actionHolder.deadline ? jsDateToInputTypeDate(props.actionHolder.deadline) : undefined
)
const completedDateString = ref<string | undefined>(
  props.actionHolder.completed ? jsDateToInputTypeDate(props.actionHolder.completed) : undefined
)
const comment = ref(props.actionHolder.comment ?? '')
const body = ref(props.actionHolder.body ?? '')

const sinceWhenDisplay = computed(() => {
  if (!props.actionHolder.sinceWhen) return '(N/A)'
  return DateTime.fromJSDate(props.actionHolder.sinceWhen).toLocaleString(DateTime.DATE_MED_WITH_WEEKDAY)
})

const save = async () => {
  const id = props.actionHolder.id
  if (id === undefined) {
    snackbar.add({ type: 'error', title: 'Missing action holder id', text: '' })
    return
  }

  let deadline: Date | null | undefined = undefined
  let completed: Date | null | undefined = undefined

  if (deadlineDateString.value) {
    const dt = inputTypeDateToDateTime(deadlineDateString.value)
    if (!dt.isValid) {
      snackbar.add({ type: 'error', title: 'Invalid deadline date', text: '' })
      return
    }
    deadline = dt.toJSDate()
  } else {
    deadline = null
  }

  if (completedDateString.value) {
    const dt = inputTypeDateToDateTime(completedDateString.value)
    if (!dt.isValid) {
      snackbar.add({ type: 'error', title: 'Invalid completed date', text: '' })
      return
    }
    completed = dt.toJSDate()
  } else {
    completed = null
  }

  try {
    await api.documentsActionHoldersPartialUpdate({
      draftName: props.draftName,
      id,
      patchedActionHolderRequest: { deadline, completed, comment: comment.value, body: body.value },
    })
    isSuccess.value = true
    snackbar.add({ type: 'success', title: 'Action holder saved', text: '' })
    await props.onSuccess()
    closeOverlayModal()
  } catch (e) {
    snackbarForErrors({ snackbar, defaultTitle: 'Problem saving action holder', error: e })
  }
}

const deleteActionHolder = async () => {
  const id = props.actionHolder.id
  if (id === undefined) {
    snackbar.add({ type: 'error', title: 'Missing action holder id', text: '' })
    return
  }
  try {
    await api.documentsActionHoldersDestroy({ draftName: props.draftName, id })
    isDeleted.value = true
    snackbar.add({ type: 'success', title: 'Action holder deleted', text: '' })
    await props.onSuccess()
    closeOverlayModal()
  } catch (e) {
    snackbarForErrors({ snackbar, defaultTitle: 'Problem deleting action holder', error: e })
  }
}
</script>
