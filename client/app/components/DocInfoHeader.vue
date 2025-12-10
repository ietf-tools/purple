<template>
  <header class="relative isolate">
    <div class="absolute inset-0 -z-10 overflow-hidden" aria-hidden="true">
      <div class="absolute left-16 top-full -mt-16 transform-gpu opacity-50 blur-3xl xl:left-1/2 xl:-ml-80">
        <div class="aspect-[1154/678] w-[72.125rem] bg-gradient-to-br from-[#FF80B5] to-[#9089FC]"
          style="clip-path: polygon(100% 38.5%, 82.6% 100%, 60.2% 37.7%, 52.4% 32.1%, 47.5% 41.8%, 45.2% 65.6%, 27.5% 23.4%, 0.1% 35.3%, 17.9% 0%, 27.7% 23.4%, 76.2% 2.5%, 74.2% 56%, 100% 38.5%)" />
      </div>
      <div class="absolute inset-x-0 bottom-0 h-px bg-gray-900/5" />
    </div>

    <div class="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <div class="mx-auto flex max-w-2xl items-center justify-between gap-x-8 lg:mx-0 lg:max-w-none">
        <div class="flex justify-between items-center gap-x-6 text-gray-900 dark:text-white">
          <div class="flex  items-center gap-x-6 justify-between">
            <Icon name="solar:document-text-line-duotone" class="w-10 h-10" />
            <h1>
              <span class="mt-1 text-xl font-semibold leading-6">
                <span>{{ draftName }}</span>
              </span>
            </h1>
          </div>
        </div>
        <div class="flex flex-row gap-5">
          <BaseButton @click="openEmailModal">New Email</BaseButton>
          <BaseButton @click="openAssignmentFinishedModal">Finish assignments</BaseButton>
          <BaseButton @click="openPublishModal">Publish</BaseButton>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { AssignmentFinishedModal, EmailModal, PublishModal } from '#components'
import { overlayModalKey } from '~/providers/providerKeys'

const route = useRoute()
const draftName = computed(() => route.params.id?.toString() ?? '')

type Props = {
  draftName: string
}

const props = defineProps<Props>()

const snackbar = useSnackbar()

const overlayModal = inject(overlayModalKey)

const openEmailModal = async () => {
  if (!overlayModal) {
    throw Error(`Expected modal provider ${JSON.stringify({ overlayModalKey })}`)
  }

  snackbar.add({ type: 'info', title: 'Loading email modal...', text: '' })

  const rfcToBe = await documentsRetrieveSingleton({ draftName: props.draftName })
  if (rfcToBe.id === undefined) {
    throw Error(`Expected rfcToBe to have id`)
  }

  const mailtemplateList = await mailtemplateListSingleton({ rfctobeId: rfcToBe.id })

  const { openOverlayModal } = overlayModal

  openOverlayModal({
    component: EmailModal,
    componentProps: {
      mailTemplates: mailtemplateList,
      onSuccess: () => {

      }
    },
    mode: 'overlay',
  }).catch(e => {
    if (e === undefined) {
      // ignore... it's just signalling that the modal has closed
    } else {
      console.error(e)
      throw e
    }
  })
}

const openAssignmentFinishedModal = async () => {
  if (!overlayModal) {
    throw Error(`Expected modal provider ${JSON.stringify({ overlayModalKey })}`)
  }
  snackbar.add({ type: 'info', title: 'Loading assignments finished modal...', text: '' })

  const { openOverlayModal } = overlayModal

  const rfcToBe = await documentsRetrieveSingleton({ draftName: props.draftName })
  if (rfcToBe.id === undefined) {
    throw Error(`Expected rfcToBe to have id`)
  }

  const [rfcToBeAssignments, people] = await Promise.all([
    rfcAssignmentsListSingleton(rfcToBe.id),
    rpcPersonListSingleton()
  ])

  openOverlayModal({
    component: AssignmentFinishedModal,
    componentProps: {
      assignments: rfcToBeAssignments,
      people: people,
      rfcToBe: rfcToBe,
      onSuccess: () => {

      }
    },
    mode: 'side',
  }).catch(e => {
    if (e === undefined) {
      // ignore... it's just signalling that the modal has closed
    } else {
      console.error(e)
      throw e
    }
  })
}

const openPublishModal = async () => {
  if (!overlayModal) {
    throw Error(`Expected modal provider ${JSON.stringify({ overlayModalKey })}`)
  }


  const api = useApi()

const {
  data: approvalLogsList,
  pending: approvalLogsListPending,
  error: approvalLogsListError,
  refresh: approvalLogsListReload
} = await useAsyncData(
  `approval-log-${draftName}`,
  () => api.documentsApprovalLogsList({ draftName: draftName.value }),
  { server: false, lazy: false }
)


  console.log("commentList", approvalLogsList.value)

  snackbar.add({ type: 'info', title: 'Loading publish modal...', text: '' })

  const [rfcToBe, labels] = await Promise.all([
    documentsRetrieveSingleton({ draftName: props.draftName }),
    labelsListSingleton()
  ])


  const { openOverlayModal } = overlayModal

  openOverlayModal({
    component: PublishModal,
    componentProps: {
      rfcToBe: rfcToBe,
      labels: labels,
      onSuccess: () => {

      }
    },
  }).catch(e => {
    if (e === undefined) {
      // ignore... it's just signalling that the modal has closed
    } else {
      console.error(e)
      throw e
    }
  })
}
</script>
