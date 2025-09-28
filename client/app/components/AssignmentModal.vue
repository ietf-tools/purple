<template>
  <div class="h-full flex flex-col">
    <div class="flex flex-row justify-between border-b border-gray-300">
      <h1 class="text-xl font-bold pt-4 px-4 py-3">
        <span v-if="props.message.type === 'assign'">Assign</span>
        <span v-else-if="props.message.type === 'change'">Change assignment</span>
      </h1>
      <BaseButton btnType="cancel" class="m-2 flex items-center" @click="closeOverlayModal">
        <Icon name="uil:times" class="h-5 w-5" aria-hidden="true" />
      </BaseButton>
    </div>
    <div class="flex-1 overflow-y-scroll px-4 pt-4 pb-7">
      <ul class="flex flex-col gap-2">
        <li v-if="props.people && props.people.length > 0" v-for="(person, personIndex) in props.people" class="flex mx-1 flex-row gap-4 items-start">
          <input type="radio" name="assign" :value="person.id" :id="generateId(person.id, personIndex)"
            class="mt-1.5 w-7 h-7 cursor-pointer">
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
        <li v-else class="italic">
          No people available.
        </li>
      </ul>
    </div>
    <div class="flex justify-between p-4 border-t border-gray-300">
      <BaseButton btnType="cancel" @click="closeOverlayModal">Cancel</BaseButton>
      <BaseButton btnType="default">Save changes</BaseButton>
    </div>
  </div>
</template>
<script setup lang="ts">
import { BaseButton } from '#components'
import { assign, groupBy } from 'lodash-es';
import type { Cluster, RpcPerson } from '~/purple_client';
import type { AssignmentMessageProps } from '~/utils/queue'
import type { ResolvedQueueItem } from './AssignmentsTypes';
import { overlayModalKey } from '~/providers/providerKeys';

type ResolvedCluster = {
  number: number
  documents: ResolvedQueueItem[]
}

type Props = {
  message: AssignmentMessageProps
  selectedPersonId?: number
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

const { closeOverlayModal } = overlayModalKeyInjection


</script>
