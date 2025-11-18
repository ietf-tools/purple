<template>
  <div
    class="h-full bg-gray-100 text-black dark:bg-gray-800 dark:text-black flex flex-col justify-between gap-5 px-2 pt-5 pb-2">
    <BaseButton btnType="cancel" class="absolute right-1 top-1 z-50" @click="closeOverlayModal">
      <Icon name="uil:times" class="h-5 w-5" aria-hidden="true" />
    </BaseButton>
    <div class="border rounded-md border-gray-500 bg-white dark:bg-black">
      <Heading :heading-level="3" class="p-5">
        {{ props.finalApproval ? 'Edit Final Review' : 'Add Final Review' }}
      </Heading>
      <div class="flex flex-col gap-3 justify-between">
        <div class="flex flex-col gap-3">
          <DialogFieldPickAuthor v-model="approver" id="approver" label="Approver" :disabled="isFinalReviewApiSuccess" />
          <DialogFieldDate v-model="approvedDateString" id="approvedDate" label="Date of approval?" :disabled="isFinalReviewApiSuccess" />

          <div v-if="!props.finalApproval" class="flex flex-row">
            <span class="w-[160px]"></span>
            <div>
              <RpcCheckbox id="override-approval" label="Has approval override?" :checked="hasApprovalOverride"
                @change="handleOverrideChange" :disabled="isFinalReviewApiSuccess" />
              <div v-if="hasApprovalOverride" class="flex flex-col gap-3">
                <DialogFieldPickAuthor id="overridingApprover" v-model="overridingApprover"
                  label="Overriding approvder" :disabled="isFinalReviewApiSuccess" />
              </div>
              <div v-else>
                <i>(No override)</i>
              </div>
            </div>
          </div>
        </div>
        <div class="flex flex-row items-center p-5 border-t-2 border-gray-500 bg-gray-300 dark:bg-gray-800">
          <BaseButton btn-type="default" @click="clickFinalApprovalHandler" :disabled="isFinalReviewApiSuccess">
            {{ props.finalApproval ?
              'Edit Final Review' :
              'Add Final Review' }}
          </BaseButton>
          <b v-if="isFinalReviewApiSuccess" class="text-green-800 font-bold ml-3">
            Done
          </b>
        </div>
      </div>
    </div>
    <div class="border rounded-md border-gray-500 bg-white dark:bg-black">
      <Heading :heading-level="3" class="p-5">
        Add Comment
      </Heading>
      <DialogFieldText id="comment" v-model="comment" label="Comment" is-multiline :disabled="isCommentApiSuccess" />
      <div class="flex flex-row items-center p-5 border-t-2 border-gray-500 bg-gray-300 dark:bg-gray-800">
        <BaseButton btn-type="default" @click="clickCommentHandler" :disabled="isCommentApiSuccess">
          Add comment
        </BaseButton>
        <b v-if="isCommentApiSuccess" class="text-green-800 font-bold ml-3">
          Done
        </b>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DatatrackerPerson, FinalApproval } from '~/purple_client'
import { overlayModalKey } from '~/providers/providerKeys'
import { jsDateToInputTypeDate, inputTypeDateToDateTime } from '../utils/form'

type Props = {
  /** if finalApproval is provided the modal will be in 'edit' mode.
   *  if none is provided the modal will be in 'add' mode
    */
  finalApproval?: FinalApproval
  name: string
  onSuccess: () => Promise<void>
}

const snackbar = useSnackbar()

const props = defineProps<Props>()

const api = useApi()

const approver = ref<DatatrackerPerson | undefined>(props.finalApproval?.approver ?? undefined)
const approvedDateString = ref<string>(jsDateToInputTypeDate(new Date()))

const hasApprovalOverride = ref(Boolean(props.finalApproval?.overridingApprover))
const overridingApprover = ref<DatatrackerPerson | undefined>(props.finalApproval?.overridingApprover ?? undefined)

const comment = ref('')

const overlayModalKeyInjection = inject(overlayModalKey)

const isFinalReviewApiSuccess = ref<boolean>(false)

const isCommentApiSuccess = ref<boolean>(false)

if (!overlayModalKeyInjection) {
  throw Error('Expected injection of overlayModalKey')
}

const handleOverrideChange = (e: Event) => {
  const { target } = e;
  if (!(target instanceof HTMLInputElement)) {
    console.error(e)
    throw Error(`Unsupported event wasn't from expected element`)
  }
  const { checked } = target
  hasApprovalOverride.value = checked
}

const { closeOverlayModal } = overlayModalKeyInjection

const clickFinalApprovalHandler = async () => {
  let overridingApproverPersonId

  const approverValue = approver.value
  const approverPersonId = approver.value?.personId
  if (!approverValue || approverPersonId === undefined) {
    snackbar.add({
      type: "error",
      title: "An approver is required",
      text: ""
    })
    return
  }

  const approvedDateTime = inputTypeDateToDateTime(approvedDateString.value)
  if (!approvedDateTime.isValid) {
    snackbar.add({
      type: "error",
      title: "An approver date is required",
      text: ""
    })
    return
  }
  if (hasApprovalOverride.value) {
    if (!overridingApprover.value) {
      snackbar.add({
        type: "error",
        title: "An overriding approver is required",
        text: ""
      })
      return
    }
    overridingApproverPersonId = overridingApprover.value.personId
  }

  const { name: draftName } = props

  if (draftName.trim().length === 0) {
    snackbar.add({
      type: "error",
      title: "A draft name is required",
      text: ""
    })
  }

  try {
    if (props.finalApproval) {
      const { id } = props.finalApproval
      if (id === undefined) {
        snackbar.add({
          type: "error",
          title: "Could not edit final approval as it lacked an id",
          text: ""
        })
        return
      }
      await api.documentsFinalApprovalsPartialUpdate({
        draftName,
        id,
        patchedFinalApprovalRequest: {
          approved: approvedDateTime.toJSDate(),
        }
      })
    } else {
      await api.documentsFinalApprovalsCreate({
        draftName,
        createFinalApprovalRequest: {
          approverPersonId,
          approved: approvedDateTime.toJSDate(),
          overridingApproverPersonId,
        }
      })
    }

    await props.onSuccess()
    isFinalReviewApiSuccess.value = true
    snackbar.add({
    type: "success",
    title: props.finalApproval ? "Final Review edited" : "Final Review created",
    text: ""
  })
  } catch (e) {
    snackbarForErrors({ snackbar, defaultTitle: 'Problem creating Final Review', error: e })
  }
}

const clickCommentHandler = async () => {
  const { name: draftName } = props
  const commentValue = comment.value

  if (draftName.trim().length === 0) {
    snackbar.add({
      type: "error",
      title: "A draft name is required",
      text: ""
    })
  }

  if (commentValue.trim().length === 0) {
    snackbar.add({
      type: "error",
      title: "A comment is required",
      text: ""
    })
  }

  await api.documentsCommentsCreate({
    draftName,
    documentCommentRequest: {
      comment: commentValue
    }
  })
  await props.onSuccess()
  isCommentApiSuccess.value = true

  snackbar.add({
    type: "success",
    title: "Comment added",
    text: ""
  })
}
</script>
