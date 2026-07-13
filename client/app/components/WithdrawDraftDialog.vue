<template>
  <HeadlessTransitionRoot as="template" :show="props.isShown">
    <HeadlessDialog as="div" class="relative z-[100]" @close="cancel">
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
                  <div class="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left w-full">
                    <HeadlessDialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900 dark:text-neutral-100">
                      Withdraw {{ props.draftName }}
                    </HeadlessDialogTitle>
                    <div class="mt-2">
                      <p class="text-sm text-gray-500 dark:text-neutral-400">
                        This will change the disposition to <strong>withdrawn</strong>. Add an optional comment.
                      </p>
                    </div>
                    <div class="mt-4">
                      <textarea
                        v-model="comment"
                        rows="3"
                        class="block w-full rounded-md border-0 py-1.5 text-gray-900 dark:text-neutral-100 dark:bg-neutral-800 shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-neutral-600 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                        placeholder="Add a comment (optional)..."
                      />
                    </div>
                  </div>
                </div>
              </div>
              <div class="bg-gray-50 dark:bg-neutral-800 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6 gap-2">
                <BaseButton
                  btn-type="delete"
                  class="inline-flex w-full justify-center disabled:opacity-50 sm:w-auto"
                  :disabled="isSubmitting"
                  @click="handleWithdraw"
                >
                  <Icon v-if="isSubmitting" name="ei:spinner-3" size="1.1em" class="animate-spin mr-1" />
                  Withdraw
                </BaseButton>
                <BaseButton btn-type="cancel" class="inline-flex w-full justify-center sm:w-auto" :disabled="isSubmitting" @click="cancel">Cancel</BaseButton>
              </div>
            </HeadlessDialogPanel>
          </HeadlessTransitionChild>
        </div>
      </div>
    </HeadlessDialog>
  </HeadlessTransitionRoot>
</template>

<script setup lang="ts">
import { snackbarForErrors } from '~/utils/snackbar'

type Props = {
  isShown: boolean
  draftName: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:isShown': [value: boolean]
  success: []
}>()

const api = useApi()
const snackbar = useSnackbar()

const comment = ref('')
const isSubmitting = ref(false)

const cancel = () => {
  if (!isSubmitting.value) {
    emit('update:isShown', false)
  }
}

const handleWithdraw = async () => {
  isSubmitting.value = true
  try {
    await api.documentsPartialUpdate({
      draftName: props.draftName,
      patchedRfcToBeRequest: { disposition: 'withdrawn' }
    })
  } catch (error: unknown) {
    snackbarForErrors({ snackbar, defaultTitle: 'Withdrawing draft failed', error })
    isSubmitting.value = false
    return
  }

  // Withdraw committed — the comment is a best-effort annotation.
  try {
    const trimmedComment = comment.value.trim()
    if (trimmedComment) {
      await api.documentsCommentsCreate({
        draftName: props.draftName,
        documentCommentRequest: { comment: trimmedComment }
      })
    }
  } catch (error: unknown) {
    snackbarForErrors({ snackbar, defaultTitle: 'Draft withdrawn, but saving the comment failed', error })
  }

  comment.value = ''
  emit('update:isShown', false)
  emit('success')
  isSubmitting.value = false
}
</script>
