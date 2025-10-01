<template>
  <div class="h-full flex flex-col">
    <div class="flex flex-row justify-between border-b border-gray-300">
      <h1 class="text-xl font-bold pt-4 px-4 py-3">
        <span v-if="props.message.type === 'assign'">
          Assign
          <BaseBadge :label="props.message.rpcRole.slug" size="xl"></BaseBadge>
        </span>
        <span v-else-if="props.message.type === 'change'">
          Change
          <BaseBadge :label="props.message.assignments[0]?.role ?? undefined" size="xl"></BaseBadge>
          assignment
        </span>
      </h1>
      <BaseButton btnType="cancel" class="m-2 flex items-center" @click="closeOverlayModal">
        <Icon name="uil:times" class="h-5 w-5" aria-hidden="true" />
      </BaseButton>
    </div>
    <div class="flex-1 overflow-y-scroll px-4 pt-4 pb-7">
      <ul class="flex flex-col gap-2">
        <li v-for="(person, personIndex) in props.people" class="flex mx-1 flex-row gap-4 items-start">
          <input type="checkbox" name="assign" :checked="person.id ? isPersonSelected[person.id] : false"
            :value="person.id" :id="generateId(person.id, personIndex)" class="mt-1.5 w-7 h-7 cursor-pointer"
            @click="toggleSelection(person.id)">
          <div class="flex flex-col">
            <label :for="generateId(person.id, personIndex)" class="font-bold cursor-pointer">
              {{ person.name }}
              <span class="font-normal text-gray-700">(#{{ person.id }})</span>
            </label>
            <ul>
              <li v-for="capability in person.capabilities" class="inline-block">
                <BaseBadge>{{ capability.name }}</BaseBadge>
              </li>
            </ul>
            <div>
              <p class="text-gray-500" v-if="person.id && person.id in clustersByPerson">
                Currently assigned:
                <template v-for="cluster in clustersByPerson[person.id]" :key="cluster.number">
                  {{ cluster.number }}
                  <span v-for="document in cluster.documents" :key="document.id">
                    {{ document.name }}, {{ document.pages }} pages
                  </span>
                </template>
              </p>
              <p v-else class="italic text-sm">(No other assignments)</p>
            </div>
          </div>
        </li>
      </ul>
    </div>
    <div v-if="actions.length > 0" class="flex flex-col gap-2 bg-gray-200 py-2 px-4 border-t border-gray-300">
      <h2 class="font-bold">Changes to save</h2>
      <div class="flex flex-col gap-y-1 text-sm">

        <div v-for="action in actions">
          <div v-if="action.type === 'withdraw'">
            <p>
            &bull; <b>Withdraw assignment</b> for <b>{{ getPersonNameById(action.personId) }}</b> #{{ action.personId }}
            <span class="ml-4">Reason <i>(optional)</i>: <input type="text" value="" class="text-xs px-2 py-1 "></span>
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
      <BaseButton btnType="default">Save changes</BaseButton>
    </div>
  </div>
</template>
<script setup lang="ts">
import { watch } from 'vue'
import { BaseButton } from '#components'
import type { RpcPerson } from '~/purple_client';
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
  clusters: ResolvedCluster[]
}
const props = defineProps<Props>()

const generateId = (personId: number | undefined, personIndex: number): string => `person-${personId ?? personIndex}`

const currentTime = useCurrentTime()

const clustersByPerson = computed(() => {
  return props.clusters.reduce((acc, cluster) => {
    cluster.documents.forEach(document => {
      console.log(Object.keys(document))
      document.assignments?.forEach(assignment => {
        const personId = assignment.person?.id
        if (personId) {
          if (!Array.isArray(acc[personId])) {
            acc[personId] = []
          }
          acc[personId].push(cluster)
        }
      })
    })
    return acc
  }, {} as Record<number, ResolvedCluster[]>)
})

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
  console.log('toggle', personId)
  const toggledValue = !isPersonSelected.value[personId]
  isPersonSelected.value = {
    ...isPersonSelected.value,
    [personId]: toggledValue
  }
  console.log(toggledValue)
}

type ActionWithdrawn = { type: 'withdraw', personId: number, reason: string }
type ActionAssign = { type: 'assign', personId: number }
type Action = ActionWithdrawn | ActionAssign

const actions = ref<Action[]>([])

watch(isPersonSelected, () => {
  const newActions: Action[] = []

  if (props.message.type === 'change') {
    const message = props.message
    // withdrawns
    newActions.push(
      ...message.assignments.filter(assignment => {
        const { person } = assignment
        if (person === undefined || person === null) {
          throw Error('Internal error: An assignment should have a person but it did not')
        }
        return !isPersonSelected.value[person]
      }).map((withdrawAssignments): ActionWithdrawn => {
        const { person } = withdrawAssignments
        if (person === undefined || person === null) {
          throw Error('Internal error: An assignment should have a person but it did not')
        }

        const existingAction = actions.value.find(action => action.type === 'withdraw' && action.personId === person)

        return {
          type: 'withdraw',
          personId: person,
          reason: existingAction?.type === 'withdraw' ? existingAction.reason : ''
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
        }
      })

    )
  } else if (props.message.type === 'assign') {
    newActions.push(
      ...Object.entries(isPersonSelected.value).map(([personIdString]): ActionAssign => {
        const personId = parseInt(personIdString, 10)
        return {
          type: 'assign',
          personId,
        }
      })
    )
  }

  actions.value = newActions

}, { deep: true })

const getPersonNameById = (personId?: number): string => {
  if (personId === undefined) return 'Unknown'
  const person = props.people.find(person => person.id === personId)
  return person?.name ?? 'Unknown'
}

</script>
