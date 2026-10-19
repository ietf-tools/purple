<template>
  <div class="h-full flex flex-col text-gray-900 dark:text-neutral-100">
    <div class="flex flex-row justify-between border-b border-gray-300 dark:border-neutral-700">
      <h1 class="text-xl font-bold pt-4 px-4 py-3 flex items-center gap-2">
        Assignments for
        <select
          v-model="selectedRole"
          class="text-base font-normal border border-gray-300 dark:border-gray-600 rounded px-2 py-1 bg-white dark:bg-neutral-800 min-w-[14rem]">
          <option v-for="role in roleOptions" :key="role.slug" :value="role.slug">
            {{ role.name }}
          </option>
        </select>
      </h1>
      <BaseButton btnType="cancel" class="m-2 flex items-center" @click="closeOverlayModal">
        <Icon name="uil:times" class="h-5 w-5" aria-hidden="true" />
      </BaseButton>
    </div>
    <div class="flex-1 overflow-y-scroll px-4 pt-4 pb-7">
      <ul class="flex flex-col gap-2">
        <li
          v-if="visiblePeople.length > 0"
          v-for="(person, personIndex) in visiblePeople"
          class="flex mx-1 flex-row gap-4 items-start">
          <input
            type="checkbox"
            name="assign"
            :checked="person.id ? isPersonSelected[person.id] : false"
            :value="person.id"
            :id="generateId(person.id, personIndex)"
            class="mt-1.5 w-7 h-7 cursor-pointer"
            @click="toggleSelection(person.id)" />
          <div class="flex flex-col">
            <label :for="generateId(person.id, personIndex)" class="font-bold cursor-pointer">
              {{ person.name }}
              <span class="font-normal text-gray-700 dark:text-neutral-400"
                >(#{{ person.id }})</span
              >
              <span
                v-if="person.id && heldPeople.has(person.id)"
                class="ml-1 font-normal italic text-gray-700 dark:text-neutral-400"
                >on hold</span
              >
            </label>
            <div v-if="person.capabilities?.length" class="text-sm mb-1">
              Capabilities:
              <ul class="inline-block ml-1">
                <li v-for="capability in person.capabilities" class="inline-block mr-1">
                  <BaseBadge>{{ capability.name }}</BaseBadge>
                </li>
              </ul>
            </div>
            <div>
              <p class="text-sm" v-if="person.id && peopleWorkload[person.id]">
                Currently assigned:
                <WorkloadSummary :workload="peopleWorkload[person.id]!" />
              </p>
              <p v-else class="italic text-sm">(No other assignments)</p>
            </div>
          </div>
        </li>
        <li v-else class="italic">(no people)</li>
      </ul>
    </div>
    <div
      v-if="actions.length > 0"
      class="flex flex-col gap-2 bg-gray-200 dark:bg-neutral-700 py-2 px-4 border-t border-gray-300 dark:border-neutral-700">
      <h2 class="font-bold">Changes to save</h2>
      <div class="flex flex-col gap-y-1 text-sm">
        <div v-for="action in actions">
          <div v-if="action.type === 'withdraw'">
            <p>
              &bull; <b>Withdraw assignment</b> for
              <b>{{ getPersonNameById(action.personId) }}</b> #{{ action.personId }}
              <span class="ml-4"
                >Reason <i>(optional)</i>:
                <input
                  type="text"
                  value=""
                  @input="(e) => changeReason(action, e)"
                  class="text-xs px-2 py-1 bg-white dark:bg-neutral-800 text-gray-900 dark:text-neutral-100 border border-gray-300 dark:border-neutral-600 rounded"
              /></span>
            </p>
          </div>
          <p v-else-if="action.type === 'assign'">
            &bull; <b>Assign</b> <b>{{ getPersonNameById(action.personId) }}</b> #{{
              action.personId
            }}
          </p>
        </div>
      </div>
    </div>
    <div class="flex justify-between p-4 border-t border-gray-300 dark:border-neutral-700">
      <BaseButton btnType="cancel" @click="closeOverlayModal">Cancel</BaseButton>
      <BaseButton btnType="default" @click="saveChanges" :disabled="!canSave"
        >Save changes</BaseButton
      >
    </div>
  </div>
</template>
<script setup lang="ts">
import { watch } from 'vue'
import { BaseButton } from '#components'
import type { Assignment, RpcPerson, RpcRole } from '~/purple_client'
import { StateEnum } from '~/purple_client'
import { assignmentRoleOrder } from '~/utils/sort'
import type { AssignmentMessageProps } from '~/utils/queue'
import type { ResolvedQueueItem } from './AssignmentsTypes'
import { overlayModalKey } from '~/providers/providerKeys'

type ResolvedCluster = {
  number: number
  documents: ResolvedQueueItem[]
}

type Props = {
  message: AssignmentMessageProps
  people: RpcPerson[]
  peopleWorkload: Record<number, RpcPersonWorkload>
  clusters: ResolvedCluster[]
  onSuccess: () => void
}
const props = defineProps<Props>()

const api = useApi()

const roles = ref<RpcRole[]>([])
api.rpcRolesList().then((list) => {
  roles.value = list
})

const roleOrderIndex = (slug: string) =>
  assignmentRoleOrder.indexOf(slug as (typeof assignmentRoleOrder)[number])

// Pipeline roles in pipeline order, plus the role the dialog was opened for.
const roleOptions = computed(() =>
  roles.value
    .filter((role) => roleOrderIndex(role.slug) !== -1 || role.slug === props.message.role)
    .sort((a, b) => roleOrderIndex(a.slug) - roleOrderIndex(b.slug))
)

const selectedRole = ref<Assignment['role']>(props.message.role ?? '')

watch(roleOptions, (options) => {
  if (!selectedRole.value && options[0]) {
    selectedRole.value = options[0].slug
  }
})

const generateId = (personId: number | undefined, personIndex: number): string =>
  `person-${personId ?? personIndex}`

const overlayModalKeyInjection = inject(overlayModalKey)

if (!overlayModalKeyInjection) {
  throw Error('Expected injection of overlayModalKey')
}

type SelectedPeople = Record<number, boolean>

const holders = computed(() =>
  props.message.assignments.filter(
    (assignment) => assignment.role === selectedRole.value && assignment.person != null
  )
)

const heldPeople = computed(
  () =>
    new Set(
      holders.value
        .filter((assignment) => assignment.state === StateEnum.ClosedForHold)
        .map((assignment) => assignment.person)
    )
)

const tickHolders = (): SelectedPeople =>
  Object.fromEntries(holders.value.map((assignment) => [assignment.person, true]))

const isPersonSelected = ref<SelectedPeople>(tickHolders())

watch(selectedRole, () => {
  isPersonSelected.value = tickHolders()
})

const { closeOverlayModal } = overlayModalKeyInjection

const toggleSelection = (personId?: number) => {
  if (personId === undefined) {
    throw Error('Internal error: An assignment should have a person but it did not')
  }
  const toggledValue = !isPersonSelected.value[personId]
  isPersonSelected.value = {
    ...isPersonSelected.value,
    [personId]: toggledValue
  }
}

type ActionWithdrawn = {
  type: 'withdraw'
  personId: number
  reason: string
  existingComment?: string
  assignmentId: number
}
type ActionAssign = {
  type: 'assign'
  personId: number
  rfcToBeId: number
  role: Assignment['role']
}
type Action = ActionWithdrawn | ActionAssign

const isSaving = ref(false)
const actions = ref<Action[]>([])

watch(
  isPersonSelected,
  () => {
    const withdrawals = holders.value
      .filter((assignment) => !isPersonSelected.value[assignment.person!])
      .map((assignmentToWithdraw): ActionWithdrawn => {
        const person = assignmentToWithdraw.person!
        if (!assignmentToWithdraw.id) {
          throw Error(
            `Assignment to withdraw was missing an id. Was ${JSON.stringify(assignmentToWithdraw)}`
          )
        }
        const existingAction = actions.value.find(
          (action) => action.type === 'withdraw' && action.personId === person
        )
        return {
          type: 'withdraw',
          personId: person,
          reason: existingAction?.type === 'withdraw' ? existingAction.reason : '',
          assignmentId: assignmentToWithdraw.id,
          existingComment: assignmentToWithdraw.comment
        }
      })

    const assignments = Object.entries(isPersonSelected.value)
      .filter(([personIdString, isSelected]) => {
        const personId = parseInt(personIdString, 10)
        return isSelected && !holders.value.some((assignment) => assignment.person === personId)
      })
      .map(([personIdString]): ActionAssign => ({
        type: 'assign',
        personId: parseInt(personIdString, 10),
        rfcToBeId: props.message.rfcToBeId,
        role: selectedRole.value
      }))

    actions.value = [...withdrawals, ...assignments]
  },
  { deep: true, immediate: true }
)

// filter the list of editors to those who are active or currently hold the role
const visiblePeople = computed(() =>
  props.people.filter(
    (person) =>
      person.isActive || holders.value.some((assignment) => assignment.person === person.id)
  )
)

const canSave = computed(() => {
  return actions.value.length === 0 || !isSaving.value
})

const getPersonNameById = (personId?: number): string => {
  if (personId === undefined) return 'Unknown'
  const person = props.people.find((person) => person.id === personId)
  return person?.name ?? 'Unknown'
}

const snackbar = useSnackbar()

const saveChanges = async () => {
  isSaving.value = true

  await Promise.all(
    actions.value.map(async (action) => {
      switch (action.type) {
        case 'withdraw':
          // make new `patchedAssignment.comment` string with the goal of preserving any existing comment by appending `action.reason` to it
          const newComment = `${
            // existing comment
            action.existingComment ?? ''
          }${
            // linebreak between if there's both an existing comment and a reason provided
            action.existingComment && action.reason.trim().length > 0 ? '\n' : ''
          }${
            // the reason
            action.reason.trim().length > 0 ? `Withdrawn reason: ${action.reason}` : ''
          }`.trim()

          return api
            .assignmentsPartialUpdate({
              id: action.assignmentId,
              patchedAssignmentRequest: {
                state: 'withdrawn',
                comment: newComment.trim().length > 0 ? newComment : undefined // only save newComment when it has content, not just an empty string
              }
            })
            .then((assignment) => {
              if (assignment.state !== 'withdrawn') {
                const errorMessage =
                  "Problem updating assignment. Saved data didn't match requested data."
                console.error(errorMessage, assignment, action)
                throw Error(errorMessage)
              }
              return assignment
            })
        case 'assign':
          return api
            .assignmentsCreate({
              assignmentRequest: {
                rfcToBe: action.rfcToBeId,
                person: action.personId,
                role: action.role
              }
            })
            .then((assignment) => {
              if (
                assignment.rfcToBe !== action.rfcToBeId ||
                assignment.person !== action.personId ||
                assignment.role !== action.role
              ) {
                const errorMessage =
                  "Problem creating assignment. Saved data didn't match requested data."
                console.error(errorMessage, assignment, action)
                throw Error(errorMessage)
              }
              return assignment
            })
      }
      assertNever(action)
    })
  )
    .catch((e) => {
      console.error(e)
      snackbar.add({
        type: 'error',
        title: `Problem saving assignment changes. See console for more.`,
        text: JSON.stringify(e).substring(0, 100) // substring because the JSON could be too long for a snackbar toast
      })
      throw e
    })
    .finally(() => {
      isSaving.value = false
    })

  // if it got this far assume it was successful

  props.onSuccess() // triggers reload of page table data

  closeOverlayModal()
}

const changeReason = (action: ActionWithdrawn, e: Event): void => {
  assert(e.target instanceof HTMLInputElement)
  action.reason = e.target.value
}
</script>
