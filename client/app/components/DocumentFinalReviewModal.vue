<template>
  <div
    class="h-full bg-gray-100 text-black dark:bg-gray-800 dark:text-black flex flex-col justify-between gap-5 px-2 pt-10 pb-2">
    <BaseButton btnType="outline" class="absolute right-1 top-1 z-50" @click="closeOverlayModal">
      <Icon name="uil:times" class="h-5 w-5" aria-hidden="true" />
    </BaseButton>
    <form novalidate class="border rounded-md border-gray-500 bg-white dark:bg-black">
      <Heading :heading-level="3" class="p-5">
        {{ props.finalApproval ? 'Edit Final Review Approver' : 'Add Final Review Approver' }}
      </Heading>
      <div class="flex flex-col gap-3 justify-between">
        <div class="flex flex-col gap-3">
          <DialogFieldPickAuthor v-model="approver" id="approver" label="Approver"
            :disabled="isFinalReviewApiSuccess" />
          <DialogFieldDate v-model="approvedDateString" id="approvedDate" label="Date of approval"
            :disabled="isFinalReviewApiSuccess" />

          <div v-if="props.finalApproval" class="flex flex-col gap-1">
            <div class="flex flex-row">
              <span class="w-[160px] mr-1"></span>
              <div>
                <RpcCheckbox id="override-approval"
                  label="Set a proxy approver, approving on behalf of the original approver?"
                  :checked="hasApprovalOverride" @change="handleOverrideChange" :disabled="isFinalReviewApiSuccess" />
              </div>
            </div>
            <div v-if="hasApprovalOverride">
              <DialogFieldPickAuthor id="overridingApprover" v-model="overridingApprover" label="Proxy Approver"
                :disabled="isFinalReviewApiSuccess" />
            </div>
          </div>
        </div>
        <div
          class="flex flex-row items-center justify-end px-5 py-3 border-t-2 border-gray-500 bg-gray-200 dark:bg-gray-800">
          <BaseButton btn-type="default" @click="clickFinalApprovalHandler" :hidden="isFinalReviewApiSuccess">
            {{ props.finalApproval ?
              'Edit Approver' :
              'Add Approver' }}
          </BaseButton>
          <b v-if="isFinalReviewApiSuccess" class="text-green-800 font-bold ml-3" aria-atomic aria-live="polite">
            {{ props.finalApproval ?
              'Approver Edited' :
              'Approver Added' }}
          </b>
        </div>
      </div>
    </form>
  </div>
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

const hasApprovalOverride = ref(Boolean(props.finalApproval?.overridingApprover))
const overridingApprover = ref<DatatrackerPerson | undefined>(props.finalApproval?.overridingApprover ?? undefined)

const overlayModalKeyInjection = inject(overlayModalKey)

const isFinalReviewApiSuccess = ref<boolean>(false)

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
  let bodyText: string | undefined = undefined

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
          body: bodyText,
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
</script>
