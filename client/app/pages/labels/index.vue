<template>
  <div class="px-4 sm:px-6 lg:px-8">
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-base font-semibold leading-6 text-gray-900 dark:text-neutral-300">
          Labels
        </h1>
      </div>
      <div class="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
        <button
          type="button"
          class="block rounded-md bg-indigo-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          @click="addLabel()">
          Add Label
        </button>
      </div>
    </div>
    <div class="mt-4 flex flex-wrap items-center gap-2">
      <span class="text-sm text-gray-500 dark:text-neutral-400">Filter:</span>
      <button
        v-for="t in filterToggles"
        :key="t.key"
        type="button"
        :aria-pressed="filters[t.key]"
        :class="[
          'inline-flex items-center gap-1 rounded-md border px-2.5 py-1 text-sm transition-colors',
          filters[t.key]
            ? 'bg-violet-100 border-violet-400 text-violet-900 dark:bg-violet-900/30 dark:border-violet-500 dark:text-violet-200'
            : 'border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700'
        ]"
        @click="filters[t.key] = !filters[t.key]">
        <Icon :name="t.icon" />{{ t.label }}
      </button>
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

const sortedLabels = computed(
  () => labels.value?.toSorted((a, b) => a.slug.localeCompare(b.slug, 'en')) ?? []
)
const filterToggles = [
  { key: 'isException', label: 'Exception', icon: 'pajamas:warning' },
  { key: 'isComplexity', label: 'Complexity', icon: 'uil:layer-group' },
  { key: 'isPublic', label: 'Public', icon: 'uil:globe' }
] as const

const filters = reactive({ isException: false, isComplexity: false, isPublic: false })

// No toggle active → show all; otherwise show labels matching any active flag.
const filteredLabels = computed(() => {
  if (!filters.isException && !filters.isComplexity && !filters.isPublic) {
    return sortedLabels.value
  }
  return sortedLabels.value.filter(
    (l) =>
      (filters.isException && l.isException) ||
      (filters.isComplexity && l.isComplexity) ||
      (filters.isPublic && l.isPublic)
  )
})
const labelsInUse = computed(() => filteredLabels.value.filter((l) => l.used))
const labelsNotInUse = computed(() => filteredLabels.value.filter((l) => !l.used))

const {
  data: labels,
  error: labelsError,
  refresh
} = await useAsyncData(() => api.labelsList(), { server: false, lazy: true })

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
