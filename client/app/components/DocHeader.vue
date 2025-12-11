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
                <span v-if="props.draftName">{{ props.draftName }}</span>
              </span>
            </h1>
          </div>
        </div>
        <div class="flex flex-row gap-5">
          <BaseButton @click="openEmailModal" class="flex items-center">
            <span>New Email</span>
            <span v-if="isLoadingNewEmailModal" class="w-3">
              <Icon name="ei:spinner-3" size="1.3rem" class="animate-spin" />
            </span>
          </BaseButton>
          <BaseButton @click="openAssignmentFinishedModal" class="flex items-center">
            <span>Finish assignments</span>
            <span v-if="isLoadingFinishAssignmentsModal" class="w-3">
              <Icon name="ei:spinner-3" size="1.3rem" class="animate-spin" />
            </span>
          </BaseButton>
          <BaseButton @click="openPublishModal" class="flex items-center">
            <span> Publish</span>
            <span v-if="isLoadingPublishModal" class="w-3">
              <Icon name="ei:spinner-3" size="1.3rem" class="animate-spin" />
            </span>
          </BaseButton>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { AssignmentFinishedModal, EmailModal, PublishModal } from '#components';
import { overlayModalKey } from '~/providers/providerKeys';
import type { MailTemplate, RfcToBe, RpcPerson } from '~/purple_client';

type Props = {
  draftName: string,
  rfcToBe?: RfcToBe
  people?: RpcPerson[]
}

const props = defineProps<Props>()

const overlayModal = inject(overlayModalKey)

if (!overlayModal) {
  throw Error(`Expected modal provider ${JSON.stringify({ overlayModalKey })}`)
}

const api = useApi()

const snackbar = useSnackbar()

const isLoadingNewEmailModal = ref(false)
const isLoadingFinishAssignmentsModal = ref(false)
const isLoadingPublishModal = ref(false)

// Cache API responses for slow APIs and/or APIs that don't change much
const personsRef = ref<RpcPerson[] | undefined>(undefined)
watch(() => props.people, () => {
  // if the parent page loads people first then use that instead of loading from the API
  if (!props.people || props.people.length === 0) {
    return
  }
  personsRef.value = props.people
})

const mailTemplateList = ref<MailTemplate[] | undefined>(undefined)

const openAssignmentFinishedModal = async () => {
  if (!props.rfcToBe || !props.rfcToBe.id) {
    snackbar.add({
      type: 'warning',
      title: `Still loading RFC...`,
      text: 'Try again in a few seconds'
    })
    return
  }

  const { openOverlayModal } = overlayModal

  isLoadingFinishAssignmentsModal.value = true

  try {
    const [assignments, rpcPersonList] = await Promise.all([
      api.assignmentsList(),
      personsRef.value ? personsRef.value : api.rpcPersonList()
    ])

    personsRef.value = rpcPersonList

    openOverlayModal({
      component: AssignmentFinishedModal,
      componentProps: {
        assignments,
        people: rpcPersonList,
        rfcToBe: props.rfcToBe,
        onSuccess: () => { }
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
  } catch (e) {
    console.error(e)
  }

  isLoadingFinishAssignmentsModal.value = false
}

const openEmailModal = async () => {
  if (!props.rfcToBe || !props.rfcToBe.id) {
    snackbar.add({
      type: 'warning',
      title: `Still loading RFC...`,
      text: 'Try again in a few seconds'
    })
    return
  }

  const { openOverlayModal } = overlayModal

  isLoadingNewEmailModal.value = true

  try {

    const [mailTemplates, rpcPersonList] = await Promise.all([
      mailTemplateList.value ? mailTemplateList.value : api.mailtemplateList({
        rfctobeId: props.rfcToBe.id,
      }),
      personsRef.value ? personsRef.value : api.rpcPersonList()
    ])

    mailTemplateList.value = mailTemplates
    personsRef.value = rpcPersonList

    openOverlayModal({
      component: EmailModal,
      componentProps: {
        mailTemplates,
        onSuccess: () => { }
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

  } catch (e) {
    console.error(e)
  }

  isLoadingNewEmailModal.value = false
}

const openPublishModal = async () => {
  if (!props.rfcToBe) {
    snackbar.add({
      type: 'warning',
      title: `Still loading RFC...`,
      text: 'Try again in a few seconds'
    })
    return
  }

  const { openOverlayModal } = overlayModal

  isLoadingPublishModal.value = true

  try {
    const [labels] = await Promise.all([
      api.labelsList()
    ])

    openOverlayModal({
      component: PublishModal,
      componentProps: {
        rfcToBe: props.rfcToBe,
        labels,
        onSuccess: () => { }
      },
    }).catch(e => {
      if (e === undefined) {
        // ignore... it's just signalling that the modal has closed
      } else {
        console.error(e)
        throw e
      }
    })

  } catch (e) {
    console.error(e)
  }

  isLoadingNewEmailModal.value = false
}
</script>
