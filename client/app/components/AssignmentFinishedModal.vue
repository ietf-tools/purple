<template>
  <div class="h-full flex flex-col bg-white text-black dark:bg-black dark:text-white">
    <div class="flex flex-row justify-between border-b border-gray-300">
      <h1 class="text-xl font-bold pt-4 px-4 py-3">
        Finish Assignments of
        <span class="mt-1 text-xl font-semibold leading-6">
          {{ props.rfcToBe.name }}
        </span>
      </h1>
      <BaseButton btnType="cancel" class="m-2 flex items-center" @click="closeOverlayModal">
        <Icon name="uil:times" class="h-5 w-5" aria-hidden="true" />
      </BaseButton>
    </div>
    <div class="flex-1 overflow-y-scroll px-4 pt-4 pb-7">
      <ul class="flex flex-col gap-4">
        <li v-if="assignments.length > 0" v-for="([role, assignments], assignmentIndex) in assignmentsByRoles"
          :key="role" class="w-full flex mx-1 flex-row gap-4 items-start">
          <h2 class="text-lg font-bold w-[10em]">
            <BaseBadge :label="role" size="xl"></BaseBadge>
          </h2>
          <ul class="">
            <li v-for="assignment in assignments" class="flex flex-row gap-4 mb-4 justify-between items-center">
              <div class="w-[13em] text-xs font-bold">
                {{ getPersonNameById(assignment.person) }}:
              </div>
              <form class="flex gap-4">
                <label class="text-xs">time spent: <input type="text" size="4" v-model="assignment.timeSpent" class="text-xs p-1"></label>
                <BaseButton btnType="default" @click="" size="xs">Finish</BaseButton>
              </form>
            </li>
          </ul>
        </li>
        <li v-else class="italic">
          (no assignments)
        </li>
      </ul>
    </div>
  </div>
</template>
<script setup lang="ts">
import { BaseButton } from '#components'
import type { Assignment, RpcPerson } from '~/purple_client';
import { overlayModalKey } from '~/providers/providerKeys';
import { groupBy } from 'lodash-es';

type Props = {
  rfcToBe: CookedDraft
  assignments: Assignment[]
  people: RpcPerson[]
  onSuccess: () => void
}
const props = defineProps<Props>()

const assignmentsByRolesObj = groupBy(
  props.assignments,
  (assignment) => assignment.role
)

const assignmentsByRoles = ref(Object.entries(assignmentsByRolesObj).sort(([keyA], [keyB]) => keyA.localeCompare(keyB)))

const getPersonNameById = (personId?: number | null): string => {
  if (personId === undefined || personId === null) return 'Unknown'
  const person = props.people.find(person => person.id === personId)
  return person?.name ?? 'Unknown'
}

const overlayModalKeyInjection = inject(overlayModalKey)

if (!overlayModalKeyInjection) {
  throw Error('Expected injection of overlayModalKey')
}

const { closeOverlayModal } = overlayModalKeyInjection

const canSave = ref(false)

const isSaving = ref(false)

const api = useApi()

const snackbar = useSnackbar()

const saveChanges = async () => {
  isSaving.value = true
  // if it got this far assume it was successful
  props.onSuccess() // triggers reload of page table data
  closeOverlayModal()
}

</script>
