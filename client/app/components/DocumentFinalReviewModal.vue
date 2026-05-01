<template>
  <form novalidate class="text-black dark:text-white" @submit.prevent>
    <div class="flex items-center justify-between border-b border-gray-200 dark:border-gray-700 px-6 py-4">
      <Heading :heading-level="3">
        {{ props.finalApproval ? 'Edit Final Review Approver' : 'Add Final Review Approver' }}
      </Heading>
      <BaseButton btnType="outline" @click="closeOverlayModal">
        <Icon name="uil:times" class="h-5 w-5" aria-hidden="true" />
      </BaseButton>
    </div>

    <div class="flex flex-col gap-4 px-6 py-5">
      <DialogFieldPickAuthor v-model="approver" id="approver" label="Approver"
        :disabled="isFinalReviewApiSuccess" person-term="approver" />

      <DialogFieldDate v-if="props.finalApproval" v-model="approvedDateString" id="approvedDate" label="Date of approval"
        :disabled="isFinalReviewApiSuccess" />

      <div v-if="props.finalApproval" class="flex flex-col gap-1">
        <div class="flex flex-row">
          <span class="w-[160px] mr-1"></span>
          <RpcCheckbox id="override-approval"
            label="Set a proxy approver, approving on behalf of the original approver?"
            :checked="hasApprovalOverride" @change="handleOverrideChange" :disabled="isFinalReviewApiSuccess" />
        </div>
        <div v-if="hasApprovalOverride">
          <DialogFieldPickAuthor id="overridingApprover" v-model="overridingApprover" label="Proxy Approver"
            :disabled="isFinalReviewApiSuccess" person-term="approver" />
        </div>
      </div>

      <div class="flex flex-col gap-1">
        <label for="final-review-comment" class="text-sm font-medium">Comment <span class="text-gray-500 font-normal">(optional)</span></label>
        <textarea
          id="final-review-comment"
          v-model="comment"
          rows="3"
          :disabled="isFinalReviewApiSuccess"
          class="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-neutral-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
          placeholder="Optional comment..."
        />
      </div>
    </div>

    <div class="flex flex-row items-center justify-between px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 rounded-b-xl">
      <BaseButton v-if="props.finalApproval" btn-type="delete" @click="deleteFinalApproval" :hidden="isFinalReviewApiSuccess || isDeleted">Delete without approval</BaseButton>
      <div class="flex flex-row items-center ml-auto gap-3">
        <b v-if="isFinalReviewApiSuccess" class="text-green-700 dark:text-green-400 font-bold" aria-atomic aria-live="polite">
          {{ props.finalApproval ? 'Saved' : 'Approver Added' }}
        </b>
        <b v-if="isDeleted" class="text-green-700 dark:text-green-400 font-bold" aria-atomic aria-live="polite">Deleted</b>
        <BaseButton btn-type="default" @click="clickFinalApprovalHandler" :hidden="isFinalReviewApiSuccess || isDeleted">
          {{ props.finalApproval ? 'Save' : 'Add Approver' }}
        </BaseButton>
      </div>
    </div>
  </form>
</template>

<script setup lang="ts">
import { DateTime } from 'luxon'
import type { DatatrackerPerson, FinalApproval } from '~/purple_client'
import { overlayModalKey } from '~/providers/providerKeys'
import { inputTypeDateToDateTime } from '../utils/form'

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
const approvedDateString = ref<string | undefined>(props.finalApproval?.approved ? jsDateToInputTypeDate(props.finalApproval.approved) : undefined)
const comment = ref<string>(props.finalApproval?.comment ?? '')

const hasApprovalOverride = ref(Boolean(props.finalApproval?.overridingApprover))
const overridingApprover = ref<DatatrackerPerson | undefined>(props.finalApproval?.overridingApprover ?? undefined)

const overlayModalKeyInjection = inject(overlayModalKey)

const isFinalReviewApiSuccess = ref<boolean>(false)
const isDeleted = ref<boolean>(false)

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
  let approvedDateTime: undefined | DateTime = undefined
  let approverPersonId: undefined | number = undefined

  const validationError = (title: string) => {
    snackbar.add({
      type: "error",
      title,
      text: ""
    })
    return
  }

  const approverValue = approver.value
  approverPersonId = approver.value?.personId
  if (!approverValue || approverPersonId === undefined) {
    return validationError("An approver is required")
  }
  if (hasApprovalOverride.value) {
    if (!overridingApprover.value) {
      return validationError("An overriding approver is required")
    }
    overridingApproverPersonId = overridingApprover.value.personId
  }

  if (approvedDateString.value) {
    approvedDateTime = inputTypeDateToDateTime(approvedDateString.value)
    if (!approvedDateTime.isValid) {
      return validationError("An approver date is required")
    }
  }

  const approved = approvedDateTime ? approvedDateTime.toJSDate() : null

  const { name: draftName } = props

  if (draftName.trim().length === 0) {
    return validationError("A draft name is required",)
  }

  if (props.finalApproval) {
    const { id } = props.finalApproval
    if (id === undefined) {
      return validationError("Could not edit final review as it lacked an id")
    }
    try {
      const approved = approvedDateTime ? approvedDateTime.toJSDate() : null
      const approverPersonId = approver.value?.personId
      const overridingApproverPersonId = hasApprovalOverride.value ?
        overridingApprover.value?.personId : undefined
      const result = await api.documentsFinalApprovalsPartialUpdate({
        draftName,
        id,
        patchedFinalApprovalRequest: {
          approved,
          comment: comment.value || undefined,
          approverPersonId,
          overridingApproverPersonId
        }
      })
      if (approved === undefined && result.approved) {
        return validationError(`Server rejected final review edit. Approved was undefined but received ${result.approved}`)
      } else if (approved) {
        if (!result.approved) {
          return validationError(`Server rejected final review edit. Approved was ${approved.toString()} but received undefined`)
        } else if (approvedDateTime && DateTime.fromJSDate(result.approved).equals(approvedDateTime)) {
          return validationError(`Server rejected final review edit. Approved was ${approved.toString()} but received ${result.approved.toString()}`)
        }
      }
    } catch (e) {
      snackbarForErrors({ snackbar, defaultTitle: 'Problem updating Final Review', error: e })
      return
    }
  } else {
    try {
      if (approverPersonId === undefined) {
        return validationError('An approver is required',)
      }
      const result = await api.documentsFinalApprovalsCreate({
        draftName,
        createFinalApprovalRequest: {
          approverPersonId,
          approved,
          overridingApproverPersonId,
          comment: comment.value || undefined,
        }
      })

      if (approverPersonId && result.approver?.personId !== approverPersonId) {
        return validationError(`Server rejected final review edit. Approver id requested was ${approverPersonId} but received ${result.approver?.personId}`)
      }
      if (approved === undefined && result.approved) {
        return validationError(`Server rejected final review edit. Approved was undefined but received ${result.approved}`)
      } else if (approved) {
        if (!result.approved) {
          return validationError(`Server rejected final review edit. Approved was ${approved.toString()} but received undefined`)
        } else if (approvedDateTime && DateTime.fromJSDate(result.approved).equals(approvedDateTime)) {
          return validationError(`Server rejected final review edit. Approved was ${approved.toString()} but received ${result.approved.toString()}`)
        }
      }
    } catch (e) {
      snackbarForErrors({ snackbar, defaultTitle: 'Problem creating Final Review', error: e })
      return
    }
  }

  await props.onSuccess()
  isFinalReviewApiSuccess.value = true
  snackbar.add({
    type: "success",
    title: props.finalApproval ? "Final Review edited" : "Final Review created",
    text: ""
  })
  closeOverlayModal()
}

const deleteFinalApproval = async () => {
  if (!props.finalApproval) return
  const { id } = props.finalApproval
  if (id === undefined) {
    snackbar.add({ type: 'error', title: 'Missing final review id', text: '' })
    return
  }
  const { name: draftName } = props
  try {
    await api.documentsFinalApprovalsDestroy({ draftName, id })
    isDeleted.value = true
    snackbar.add({ type: 'success', title: 'Final Review deleted', text: '' })
    await props.onSuccess()
    closeOverlayModal()
  } catch (e) {
    snackbarForErrors({ snackbar, defaultTitle: 'Problem deleting Final Review', error: e })
  }
}
</script>
