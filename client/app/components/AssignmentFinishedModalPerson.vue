<template>
  <li class="flex flex-row gap-4 mb-4 justify-between items-center bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded-md">
    <div class="w-[13em] text-md font-bold">
      {{ props.personName }}:
    </div>
    <form class="flex gap-4 whitespace-nowrap" @submit.prevent>
      <label class="text-xs">time spent:
        <input type="text" size="4" :id="props.assignment.id?.toString() ?? 'assignment'"
          v-model="props.assignment.timeSpent"
          class="text-xs p-1 bg-white text-black dark:bg-black dark:text-white"
          :readonly="isDone"
          >
      </label>
      <BaseButton v-if="!isDone" btnType="default" @click="finishAssignment" size="xs" :disabled="isSaving">
        Finish
      </BaseButton>
      <BaseBadge v-else color="green" @click="reopenAssignment">
        done
      </BaseBadge>
    </form>
  </li>
</template>
<script setup lang="ts">
import { BaseButton } from '#components'
import type { Assignment } from '~/purple_client';

type Props = {
  rfcToBe: CookedDraft
  assignment: Assignment
  personName: string
  onSuccess: () => void
}
const props = defineProps<Props>()

const isDone = ref(props.assignment.state === 'done')
const isSaving = ref(false)

const api = useApi()

const snackbar = useSnackbar()

const finishAssignment = async () => {
  isSaving.value = true
  const { id, timeSpent } = props.assignment
  if (id === undefined) {
    throw Error('Internal error: expected assignment to have id')
  }
  if (timeSpent === undefined) {
    throw Error('Internal error: expected assignment to have timeSpent when saving (not undefined)')
  }
  try {
    const updatedAssignment = await api.assignmentsPartialUpdate({
      id,
      patchedAssignment: {
        timeSpent,
        state: 'done'
      }
    })
    if (updatedAssignment.state !== 'done') {
      throw Error("Unable to set assignment to 'done'")
    }
    props.assignment.timeSpent = updatedAssignment.timeSpent
    // if it got this far assume it was successful
    isDone.value = true
  } catch (e) {
    snackbarForErrors({ snackbar, error: e })
  }
  isSaving.value = false
  props.onSuccess() // triggers reload of page table data, doesn't close modal
}

const reopenAssignment = async () => {
  isSaving.value = true
  const { id  } = props.assignment
  if (id === undefined) {
    throw Error('Internal error: expected assignment to have id')
  }
  try {
    const updatedAssignment = await api.assignmentsPartialUpdate({
      id,
      patchedAssignment: {
        state: 'in_progress'
      }
    })
    if (updatedAssignment.state !== 'in_progress') {
      throw Error("Unable to set assignment to 'in_progress'")
    }
    // if it got this far assume it was successful
    isDone.value = false
  } catch (e) {
    snackbarForErrors({ snackbar, error: e })
  }
  isSaving.value = false
  props.onSuccess() // triggers reload of page table data, doesn't close modal
}

</script>
