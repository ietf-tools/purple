<template>
  <div class="h-full flex flex-col">
    <div class="flex flex-row justify-between border-b border-gray-300">
      <h1 class="text-xl font-bold pt-4 px-4 py-3">
        <span v-if="props.message.type === 'assign'">
          Assign
          <BaseBadge :label="props.message.role" size="xl"></BaseBadge>
        </span>
        <span v-else-if="props.message.type === 'change'">
          Change
          <BaseBadge :label="props.message.role" size="xl"></BaseBadge>
          assignment
        </span>
      </h1>
      <BaseButton btnType="cancel" class="m-2 flex items-center" @click="closeOverlayModal">
        <Icon name="uil:times" class="h-5 w-5" aria-hidden="true" />
      </BaseButton>
    </div>
    <div class="flex-1 overflow-y-scroll px-4 pt-4 pb-7">
      <ul class="flex flex-col gap-2">
        <li v-if="visiblePeople.length > 0" v-for="(person, personIndex) in visiblePeople"
          class="flex mx-1 flex-row gap-4 items-start">
          <input type="checkbox" name="assign" :checked="person.id ? isPersonSelected[person.id] : false"
            :value="person.id" :id="generateId(person.id, personIndex)" class="mt-1.5 w-7 h-7 cursor-pointer"
            @click="toggleSelection(person.id)">
          <div class="flex flex-col">
            <label :for="generateId(person.id, personIndex)" class="font-bold cursor-pointer">
              {{ person.name }}
              <span class="font-normal text-gray-700">(#{{ person.id }})</span>
            </label>
            <div v-if="person.capabilities.length > 0" class="text-sm mb-1">
              Capabilities:
              <ul class="inline-block ml-1">
                <li v-for="capability in person.capabilities" class="inline-block mr-1">
                  <BaseBadge>{{ capability.name }}</BaseBadge>
                </li>
              </ul>
            </div>
            <div>
              <p class="text-sm" v-if="person.id && person.id in peopleWorkload">
                Currently assigned:
                <WorkloadSummary :workload="peopleWorkload[person.id]" />
              </p>
              <p v-else class="italic text-sm">(No other assignments)</p>
            </div>
          </div>
        </li>
        <li v-else class="italic">
          (no people)
        </li>
      </ul>
    </div>
    <div v-if="actions.length > 0" class="flex flex-col gap-2 bg-gray-200 py-2 px-4 border-t border-gray-300">
      <h2 class="font-bold">Changes to save</h2>
      <div class="flex flex-col gap-y-1 text-sm">

        <div v-for="(action) in actions">
          <div v-if="action.type === 'withdraw'">
            <p>
              &bull; <b>Withdraw assignment</b> for <b>{{ getPersonNameById(action.personId) }}</b> #{{ action.personId
              }}
              <span class="ml-4">Reason <i>(optional)</i>: <input type="text" value=""
                  @input="e => changeReason(action, e)" class="text-xs px-2 py-1 "></span>
            </p>
          </div>
          <p v-else-if="action.type === 'assign'">
            &bull; <b>Assign</b> editor <b>{{ getPersonNameById(action.personId) }}</b> #{{ action.personId }}
          </p>
        </div>
      </div>
    </div>
    <div class="flex justify-between p-4 border-t border-gray-300">
      <BaseButton btnType="cancel" @click="closeOverlayModal">Cancel</BaseButton>
      <BaseButton btnType="default" @click="saveChanges" :disabled="!canSave">Save changes</BaseButton>
    </div>
  </div>
</template>
<script setup lang="ts">
import { watch } from 'vue'
import { BaseButton } from '#components'
import type { Assignment, RpcPerson } from '~/purple_client';
import type { AssignmentMessageProps } from '~/utils/queue'
import type { ResolvedQueueItem } from './AssignmentsTypes';
import { overlayModalKey } from '~/providers/providerKeys';

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

const generateId = (personId: number | undefined, personIndex: number): string => `person-${personId ?? personIndex}`

const overlayModalKeyInjection = inject(overlayModalKey)

if (!overlayModalKeyInjection) {
  throw Error('Expected injection of overlayModalKey')
}

type SelectedPeople = Record<number, boolean>

const getInitialState = (message: AssignmentMessageProps): SelectedPeople => {
  if (message.type === 'assign') {
    return {}
  }
  return message.assignments.reduce((acc, assignment) => {
    if (assignment.person) {
      acc[assignment.person] = true
    }
    return acc
  }, {} as SelectedPeople)
}

const isPersonSelected = ref(getInitialState(props.message))

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

type ActionWithdrawn = { type: 'withdraw', personId: number, reason: string, existingComment?: string, assignmentId: number }
type ActionAssign = { type: 'assign', personId: number, rfcToBeId: number, role: Assignment["role"] }
type Action = ActionWithdrawn | ActionAssign

const isSaving = ref(false)
const actions = ref<Action[]>([])

watch(isPersonSelected, () => {
  const newActions: Action[] = []

  if (props.message.type === 'change') {
    const message = props.message
    // withdrawals
    newActions.push(
      ...message.assignments.filter(assignment => {
        const { person } = assignment
        if (person === undefined || person === null) {
          throw Error('Internal error: An assignment should have a person but it did not')
        }
        return !isPersonSelected.value[person]
      }).map((assignmentToWithdraw): ActionWithdrawn => {
        const { person } = assignmentToWithdraw
        if (person === undefined || person === null) {
          throw Error('Internal error: An assignment should have a person but it did not')
        }
        if (!assignmentToWithdraw.id) {
          throw Error(`Assignment to withdraw was missing an id. Was ${JSON.stringify(assignmentToWithdraw)}`)
        }

        const existingAction = actions.value.find(action => action.type === 'withdraw' && action.personId === person)

        return {
          type: 'withdraw',
          personId: person,
          reason: existingAction?.type === 'withdraw' ? existingAction.reason : '',
          assignmentId: assignmentToWithdraw.id,
          existingComment: assignmentToWithdraw.comment
        }
      })
    )

    // new assignments
    newActions.push(
      ...Object.entries(isPersonSelected.value).filter(([personIdString, isSelected]) => {
        if (!isSelected) return false
        const personId = parseInt(personIdString, 10)
        return !message.assignments.some(assignment => assignment.person === personId)
      }).map(([personIdString]): ActionAssign => {
        const personId = parseInt(personIdString, 10)
        return {
          type: 'assign',
          personId,
          rfcToBeId: message.rfcToBeId,
          role: message.role
        }
      })

    )
  } else if (props.message.type === 'assign') {
    const message = props.message
    // withdrawals
    // there are no withdrawals when initially assigning

    // new assignments
    newActions.push(
      ...Object.entries(isPersonSelected.value).map(([personIdString]): ActionAssign => {
        const personId = parseInt(personIdString, 10)
        return {
          type: 'assign',
          personId,
          rfcToBeId: message.rfcToBeId,
          role: message.role
        }
      })
    )
  }

  actions.value = newActions
}, { deep: true })

// filter the list of editors to those who are active or currently assigned
const visiblePeople = computed(() => {
  return props.people.filter(person => {
    // if the person is active show them
    if (person.isActive) {
      return true
    }
    if (props.message.type === 'change') {
      // if the person isActive===false but currently assigned show them so that we can unassign them
      if (props.message.assignments.some(assignment => assignment.person === person.id)) {
        return true
      }
    }
    return false
  })
})

const canSave = computed(() => {
  return actions.value.length === 0 || !isSaving.value
})

const getPersonNameById = (personId?: number): string => {
  if (personId === undefined) return 'Unknown'
  const person = props.people.find(person => person.id === personId)
  return person?.name ?? 'Unknown'
}

const api = useApi()

const snackbar = useSnackbar()

const saveChanges = async () => {
  isSaving.value = true

  await Promise.all(actions.value.map(async (action) => {
    switch (action.type) {
      case 'withdraw':
        // make new `patchedAssignment.comment` string with the goal of preserving any existing comment by appending `action.reason` to it
        const newComment = `${
          // existing comment
          action.existingComment ?? ''}${
          // linebreak between if there's both an existing comment and a reason provided
          action.existingComment && action.reason.trim().length > 0 ? '\n' : ''}${
          // the reason
          action.reason.trim().length > 0 ? `Withdrawn reason: ${action.reason}` : ''}`.trim()

        return api.assignmentsPartialUpdate({
          id: action.assignmentId,
          patchedAssignment: {
            state: 'withdrawn',
            comment: newComment.trim().length > 0 ? newComment : undefined // only save newComment when it has content, not just an empty string
          }
        }).then(assignment => {
          if (assignment.state !== 'withdrawn') {
            const errorMessage = "Problem updating assignment. Saved data didn't match requested data."
            console.error(errorMessage, assignment, action)
            throw Error(errorMessage)
          }
          return assignment
        })
      case 'assign':
        return api.assignmentsCreate({
          assignment: {
            rfcToBe: action.rfcToBeId,
            person: action.personId,
            role: action.role
          }
        }).then(assignment => {
          if (assignment.rfcToBe !== action.rfcToBeId || assignment.person !== action.personId || assignment.role !== action.role) {
            const errorMessage = "Problem creating assignment. Saved data didn't match requested data."
            console.error(errorMessage, assignment, action)
            throw Error(errorMessage)
          }
          return assignment
        })
    }
    assertNever(action)
  })).catch(e => {
    console.error(e)
    snackbar.add({
      type: 'error',
      title: `Problem saving assignment changes. See console for more.`,
      text: JSON.stringify(e).substring(0, 100) // substring because the JSON could be too long for a snackbar toast
    })
    throw e
  }).finally(() => {
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
