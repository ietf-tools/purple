<template>
  <li class="flex flex-row gap-4 mb-4 justify-between items-center bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded-md">
    <div class="w-[13em] text-md font-bold">
      {{ props.personName }}:
    </div>
    <form class="flex gap-4 whitespace-nowrap" @submit.prevent>
      <label class="text-xs">time spent:
        <input type="text" size="4" :id="props.assignment.id?.toString() ?? 'assignment'"
          v-model="hours" class="text-xs p-1 bg-white text-black dark:bg-black dark:text-white"
          @blur="patchTimeSpent"
        >
      </label>
      <BaseButton v-if="props.assignment.state !== 'done'" btnType="default" @click="finishAssignment" size="xs"
        :disabled="isSaving">
        Finish
      </BaseButton>
      <BaseBadge v-else color="green">{{ props.assignment.state }}</BaseBadge>
    </form>
  </li>
</template>

<script setup lang="ts">
import { BaseButton } from '#components'
import type { Assignment } from '~/purple_client';

type Props = {
  assignment: Assignment
  personName: string
  onSuccess: () => void
}
const props = defineProps<Props>()

const isSaving = ref(false)

const api = useApi()

const snackbar = useSnackbar()

const hours = ref(durationStringToHours(props.assignment.timeSpent))

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
      patchedAssignmentRequest: {
        timeSpent,
        state: 'done'
      }
    })
    if (updatedAssignment.state !== 'done') {
      console.error("Server response to update assignment to 'done' wasn't set to 'done'. Was: ", updatedAssignment)
      throw Error("Unable to set assignment to 'done'")
    }
    props.assignment.timeSpent = updatedAssignment.timeSpent
    props.assignment.state = updatedAssignment.state
    // if it got this far assume it was successful
  } catch (e) {
    console.error("Unable to update assignment to 'done'", e)
    snackbarForErrors({ snackbar, defaultTitle: "Unable to update assignment to 'done'", error: e })
  }
  isSaving.value = false
  props.onSuccess() // triggers reload of data from page under modal
}

const patchTimeSpent = async () => {
  const { id } = props.assignment
  if (id === undefined) {
    throw Error('Internal error: expected assignment to have id')
  }
  const timeSpent = hoursToDurationString(hours.value)
  try {
    const updatedAssignment = await api.assignmentsPartialUpdate({
      id,
      patchedAssignmentRequest: {
        timeSpent
      }
    })
    props.assignment.timeSpent = updatedAssignment.timeSpent
    if(updatedAssignment.timeSpent !== timeSpent) {
      console.warn('potential time spent translation bug', timeSpent, '!==', updatedAssignment.timeSpent, ' from ', updatedAssignment)
    }
  } catch (e) {
    console.error('Unable to update time spent on assignment', e)
    snackbarForErrors({ snackbar, defaultTitle: 'Unable to update time spent on assignment', error: e })
  }
  props.onSuccess() // triggers reload of data from page under modal
}

</script>
