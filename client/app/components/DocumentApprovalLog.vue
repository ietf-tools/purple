<!--
History feed component
Based on https://tailwindui.com/components/application-ui/lists/feeds#component-81e5ec57a92ddcadaa913e7bb68336fe
-->
<template>
  <div
    :class="[
      props.isLastComment ? 'h-6' : '-bottom-6',
      'absolute left-0 top-0 flex w-6 justify-center'
    ]"
  >
  </div>
  <img
    v-if="approvalLogMessage.by?.picture"
    :src="approvalLogMessage.by.picture"
    alt=""
    class="relative mt-3 h-6 w-6 flex-none rounded-full bg-gray-50"
  />
  <div class="flex-auto rounded-md p-3 ring-1 ring-inset ring-gray-200">
    <div class="flex justify-between gap-x-4">
      <div v-if="approvalLogMessage.by" class="py-0.5 text-xs leading-5 text-gray-500">
        <span
          class="font-medium text-gray-900"
          :title="approvalLogMessage.by.rpcperson ? `${approvalLogMessage.by.name} (user #${approvalLogMessage.by.rpcperson})` : undefined"
        >
          {{ approvalLogMessage.by.name }}
        </span>
        commented
        <time
          v-if="approvalLogMessage.time"
          :datetime="approvalLogMessage.time.toISOString()"
          class="text-gray-500"
        >
          {{ approvalLogMessage.ago }}
        </time>
      </div>
      <div class="flex-none py-0.5 text-xs leading-5">
        <button type="button" aria-label="Edit" class="border-0 ml-2" v-show="!isEditing" @click="handleEdit">
          <Icon name="circum:edit" class="w-5 h-5 no-underline text-gray-600 hover:text-indigo-900 cursor-pointer" />
        </button>
      </div>
    </div>
    <p v-if="!isEditing" class="text-sm leading-6 text-gray-500 whitespace-pre-wrap">
      {{ approvalLogMessage.logMessage }}
    </p>
    <div v-else>
      <textarea
        v-model="editApprovalLogMessage"
        rows="3"
        name="comment"
        class="block w-full resize-none border-1 bg-transparent text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6"
        placeholder="Edit approval log message..."
      />
      <div class="flex justify-between pt-1">
        <BaseButton btn-type="cancel" @click="isEditing = false" :disabled="isUpdating">Cancel</BaseButton>
        <BaseButton btn-type="default" @click="handleUpdateApprovalLogMessage" :disabled="isUpdating">
          <Icon v-show="isUpdating" name="ei:spinner-3" size="1.5em" class="animate-spin" />
          Update approval log message
        </BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type {ApprovalLogMessage } from '~/purple_client'
import {snackbarForErrors} from '~/utils/snackbar'

type Props = {
  draftName: string
  approvalLogMessage: ApprovalLogMessage & {
    // added by parent component
    ago?: string | null
    lastEditAgo?: string | null
  }
  isLastComment: boolean,
  reloadComments: () => Promise<void>
}

const props = defineProps<Props>()

const isEditing = ref(false)
const isUpdating = ref(false)

const editApprovalLogMessage = ref(props.approvalLogMessage.logMessage)

watch(() => props.approvalLogMessage, (newValue, oldValue) => {
  if(newValue.logMessage !== oldValue.logMessage) {
    // then a new comment has been saved and we're receiving the props,
    // so clobber the editComment ref with the current value
    editApprovalLogMessage.value = newValue.logMessage
  }
})

const handleEdit = () => {
  isEditing.value = true
}

const snackbar = useSnackbar()

const api = useApi()

const handleUpdateApprovalLogMessage = async () => {
  isUpdating.value = true
  try {
    await api.documentsApprovalLogsPartialUpdate({
      draftName: props.draftName,
      id: props.approvalLogMessage.id!,
      patchedApprovalLogMessageRequest    : {
        logMessage: editApprovalLogMessage.value
      }
    })
    isEditing.value = false
    snackbar.add({
      type: 'success',
      title: 'Comment updated successfully',
      text: ''
    })
    await props.reloadComments()
  } catch(error: unknown) {
    snackbarForErrors({ snackbar, error, defaultTitle: "Problem updating comment" })
  }
  isUpdating.value = false
}
</script>
