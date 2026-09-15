<template>
  <div>
    <DocHeader :draft-name="draftName" :rfc-to-be="rfcToBe" @withdrawn="rfcToBeRefresh" />

    <DocTabs :current-tab="currentTab" :draft-name="draftName" />

    <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <ErrorAlert v-if="noteError" title="Error loading editorial notes">
        {{ noteError }}
      </ErrorAlert>

      <BaseCard class="w-full">
        <div class="flex items-center justify-between">
          <h3 class="text-base font-semibold leading-7">
            Editorial Notes
            <Icon
              v-show="noteStatus === 'pending'"
              name="ei:spinner-3"
              size="1.5em"
              class="animate-spin" />
          </h3>
          <div class="flex gap-2">
            <template v-if="isEditing">
              <BaseButton btn-type="cancel" size="xs" :disabled="isSaving" @click="cancelEdit">
                Cancel
              </BaseButton>
              <BaseButton btn-type="default" size="xs" :disabled="isSaving" @click="save">
                Save
                <Icon
                  v-if="isSaving"
                  name="ei:spinner-3"
                  size="1rem"
                  class="animate-spin align-sub" />
              </BaseButton>
            </template>
            <BaseButton v-else btn-type="outline" size="xs" :disabled="!note" @click="startEdit">
              <Icon name="uil:pen" class="mr-1" />
              Edit
            </BaseButton>
          </div>
        </div>

        <p v-if="note?.updatedAt" class="mt-1 text-xs text-gray-500">
          Last edited {{ updatedAgo }}
          <template v-if="note.updatedBy">by {{ note.updatedBy.name }}</template>
        </p>

        <textarea
          v-if="isEditing"
          v-model="draftText"
          rows="20"
          aria-label="Editorial notes"
          class="mt-4 block w-full rounded border border-gray-300 bg-white px-3 py-2 text-sm text-black focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-black dark:text-white"
          placeholder="Notes for the editors working on this document" />
        <LinkifiedText
          v-else-if="note?.text"
          :text="note.text"
          class="mt-4 whitespace-pre-wrap text-sm leading-6" />
        <p v-else-if="note" class="mt-4 text-sm italic text-gray-500">No editorial notes yet.</p>
      </BaseCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { DateTime } from 'luxon'
import { type DocTabId } from '~/utils/doc'
import { snackbarForErrors } from '~/utils/snackbar'

const route = useRoute()
const api = useApi()
const snackbar = useSnackbar()

const currentTab: DocTabId = 'editorial-notes'
const draftName = computed(() => route.params.id?.toString() ?? '')

const { data: rfcToBe, refresh: rfcToBeRefresh } = await useAsyncData(
  () => `editorial-notes-draft-${draftName.value}`,
  () => api.documentsRetrieve({ draftName: draftName.value }),
  { server: false, lazy: true, deep: true }
)

const {
  data: note,
  error: noteError,
  status: noteStatus
} = await useAsyncData(
  () => `editorial-note-${draftName.value}`,
  () => api.documentsEditorialNoteRetrieve({ draftName: draftName.value }),
  { server: false, lazy: true }
)

const isEditing = ref(false)
const isSaving = ref(false)
const draftText = ref('')

const updatedAgo = computed(() =>
  note.value?.updatedAt ? DateTime.fromJSDate(note.value.updatedAt).toRelative() : null
)

const startEdit = () => {
  draftText.value = note.value?.text ?? ''
  isEditing.value = true
}

const cancelEdit = () => {
  isEditing.value = false
}

const save = async () => {
  isSaving.value = true
  try {
    note.value = await api.documentsEditorialNoteUpdate({
      draftName: draftName.value,
      editorialNoteRequest: { text: draftText.value }
    })
    isEditing.value = false
    snackbar.add({ type: 'success', title: 'Editorial notes saved', text: '' })
  } catch (error: unknown) {
    snackbarForErrors({ snackbar, error, defaultTitle: 'Failed to save editorial notes' })
  }
  isSaving.value = false
}
</script>
