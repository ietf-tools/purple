<template>
  <div class="h-full bg-white text-black dark:bg-black dark:text-black flex flex-col justify-between">
    <div>
      <Heading :heading-level="3" class="p-5">
        Final Reviews
      </Heading>
      <div class="flex flex-col gap-3 justify-between pr-10">
        <div class="flex flex-col gap-3">
          <DialogFieldText v-model="body" id="body" label="Body" />
          <div>
            <label class="flex flex-row items-center gap-5">
              <b class="text-gray-900 w-[130px] text-right text-sm font-bold">Date (UTC):</b>
              <input type="date" v-model="approvedDate" class="rounded-lg" />
            </label>
          </div>
        </div>
      </div>
    </div>

    <div class="flex flex-row items-end p-5 border-t-2 border-gray-500 bg-gray-800 dark:bg-gray-300">
      <BaseButton btn-type="default">Approve</BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { FinalApproval } from '~/purple_client';
import { DateTime } from 'luxon';
import { overlayModalKey } from '~/providers/providerKeys';

type Props = {
  name: string
  finalApproval: FinalApproval
  onSuccess: () => Promise<void>
}

const snackbar = useSnackbar()

const props = defineProps<Props>()

const api = useApi()

const user = useUserStore()

const body = ref(props.finalApproval.body ?? '')

const approvedDate = ref(new Date())

const overlayModalKeyInjection = inject(overlayModalKey)

if (!overlayModalKeyInjection) {
  throw Error('Expected injection of overlayModalKey')
}

const { closeOverlayModal } = overlayModalKeyInjection

type DocumentsFinalApprovalsCreateArg0 = Parameters<(typeof api)['documentsFinalApprovalsCreate']>[0]
type CreateFinalApprovalRequest = DocumentsFinalApprovalsCreateArg0["createFinalApprovalRequest"]

const approveHandler = async () => {
  const { name: draftName, finalApproval } = props
  const approverPersonId = finalApproval.approver?.personId

  if (approverPersonId === undefined) {
    console.error(props.finalApproval)
    throw Error(`Expected finalApproval to have approver.personId`)
  }

  const dateTime = DateTime.fromObject({
    year: approvedDate.value.getFullYear(),
    month: approvedDate.value.getMonth() + 1,
    day: approvedDate.value.getDate()
  }, { zone: 'utc' })

  const createFinalApprovalRequest: CreateFinalApprovalRequest = {
    body: body.value,
    approverPersonId,
    overridingApproverPersonId: props.finalApproval?.overridingApprover?.personId ?? null,
    approved: dateTime.toJSDate(),
  }

  try {
    await api.documentsFinalApprovalsCreate({
      draftName,
      createFinalApprovalRequest
    })
    await props.onSuccess()
    closeOverlayModal()
  } catch (e) {
    snackbarForErrors({ snackbar, defaultTitle: 'Problem documentsFinalApprovalsCreate', error: e })
  }

}
</script>
