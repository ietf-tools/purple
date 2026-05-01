<template>
  <div class="h-full flex flex-col bg-white text-black dark:bg-black dark:text-white">
    <div class="flex flex-row justify-between border-b border-gray-300">
      <h1 class="text-xl font-bold pt-4 px-4 py-3">
        Manage Assignments of
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
          <div class="w-[15em] shrink-0 flex items-start">
            <BaseBadge :label="role" size="xl"></BaseBadge>
          </div>
          <ul class="flex-1 min-w-0">
            <AssignmentFinishedModalPerson
              v-for="assignment in assignments"
              :assignment="assignment"
              :on-success="props.onSuccess"
              :person-name="getPersonNameById(assignment.person)"
            />
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
import { assignmentRoleOrder } from '~/utils/sort';

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

const assignmentsByRoles = ref(Object.entries(assignmentsByRolesObj).sort(([keyA], [keyB]) => {
  const a = assignmentRoleOrder.indexOf(keyA as typeof assignmentRoleOrder[number])
  const b = assignmentRoleOrder.indexOf(keyB as typeof assignmentRoleOrder[number])
  return (a === -1 ? Infinity : a) - (b === -1 ? Infinity : b)
}))

const getPersonNameById = (personId?: number | null): string => {
  if (personId === undefined || personId === null) return '(System)'
  const person = props.people.find(person => person.id === personId)
  return person?.name ?? 'Unknown'
}

const overlayModalKeyInjection = inject(overlayModalKey)

if (!overlayModalKeyInjection) {
  throw Error('Expected injection of overlayModalKey')
}

const { closeOverlayModal } = overlayModalKeyInjection

</script>
