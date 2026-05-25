<template>
  <div class="px-4 sm:px-6 lg:px-8">
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-base font-semibold leading-6 text-gray-900 dark:text-neutral-300">Labels</h1>
      </div>
      <div class="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
        <button
          type="button"
          class="block rounded-md bg-indigo-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          @click="addLabel()">Add Label
        </button>
      </div>
    </div>
    <ErrorAlert v-if="labelsError" title="API Error">
      API error while requesting labels: {{ labelsError }}
    </ErrorAlert>
    <template v-else>
      <LabelsSection title="Assignable" :labels="labelsInUse" @edit="editLabel" />
      <LabelsSection title="Not Assignable" :labels="labelsNotInUse" @edit="editLabel" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { RpcLabelEditDialog } from '#components'
import { overlayModalKey } from '~/providers/providerKeys'
import type { Label } from '~/purple_client'

const api = useApi()
const snackbar = useSnackbar()

const sortedLabels = computed(() => labels.value?.toSorted((a, b) => a.slug.localeCompare(b.slug, 'en')) ?? [])
const labelsInUse = computed(() => sortedLabels.value.filter(l => l.used))
const labelsNotInUse = computed(() => sortedLabels.value.filter(l => !l.used))

const { data: labels, error: labelsError, refresh } = await useAsyncData(
  () => api.labelsList(),
  { server: false, lazy: true }
)

const val = inject(overlayModalKey)
if (!val) {
  throw Error('Expected injection of overlayModal')
}
const { openOverlayModal } = val

async function addLabel() {
  try {
    // Empty componentProps => create a new label
    await openOverlayModal({ component: RpcLabelEditDialog })
  } catch {
    snackbar.add({
      type: 'info',
      title: 'Canceled',
      text: 'No new label was created'
    })
    return
  }
  snackbar.add({
    type: 'success',
    title: 'Success',
    text: 'Created new label'
  })
  if (refresh) {
    await refresh()
  }
}


async function editLabel(label: Label) {
  try {
    await openOverlayModal({
      component: RpcLabelEditDialog,
      componentProps: {
        label,
        create: false
      }
    })
  } catch {
    snackbar.add({
      type: 'info',
      title: 'Canceled',
      text: 'Changes to the label were not saved'
    })
    return
  }
  snackbar.add({
    type: 'success',
    title: 'Success',
    text: 'Label updated'
  })
  if (refresh) {
    await refresh()
  }
}

useHead({
  title: 'Manage Labels'
})
</script>
