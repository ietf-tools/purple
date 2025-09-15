<!-- Document Card
Based on https://tailwindui.com/components/application-ui/lists/grid-lists#component-2beafc928684743ff886c0b164edb126
-->
<template>
  <li
    :key="cookedDocument.id"
    :class="[props.selected ? 'border-violet-700' : 'border-gray-200', 'rounded-xl border']">
    <div class="flex items-center gap-x-4 border-b border-gray-900/5 bg-gray-50 dark:bg-gray-700 p-6 rounded-t-xl">
      <Icon
        name="solar:document-text-line-duotone"
        class="text-gray-900 dark:text-gray-100 h-8 w-8 flex-none"/>
      <div class="text-sm font-medium leading-6 text-gray-900 dark:text-gray-100">{{ cookedDocument.name }}</div>
      <div v-for="rpcRole in cookedDocument.needsAssignment">
        <BaseBadge :label="`Needs ${rpcRole.name ?? ''}`"/>
      </div>
      <HeadlessMenu as="div" class="relative ml-auto">
        <HeadlessMenuButton class="-m-2.5 block p-2.5 text-gray-400 hover:text-gray-500">
          <span class="sr-only">Open options</span>
          <Icon name="heroicons:ellipsis-horizontal-20-solid" class="h-5 w-5" aria-hidden="true"/>
        </HeadlessMenuButton>
        <transition
          enter-active-class="transition ease-out duration-100"
          enter-from-class="transform opacity-0 scale-95" enter-to-class="transform opacity-100 scale-100"
          leave-active-class="transition ease-in duration-75"
          leave-from-class="transform opacity-100 scale-100" leave-to-class="transform opacity-0 scale-95">
          <HeadlessMenuItems
            class="absolute right-0 z-10 mt-0.5 w-32 origin-top-right rounded-md bg-white py-2 shadow-lg ring-1 ring-gray-900/5 focus:outline-none">
            <HeadlessMenuItem v-slot="{ active }">
              <Anchor href="#" :class="[active ? 'bg-gray-50' : '', 'block px-3 py-1 text-sm leading-6 text-gray-900']">
                View<span class="sr-only">, {{ cookedDocument.name }}</span>
              </Anchor>
            </HeadlessMenuItem>
            <HeadlessMenuItem v-slot="{ active }">
              <Anchor href="#" :class="[active ? 'bg-gray-50' : '', 'block px-3 py-1 text-sm leading-6 text-gray-900']">
                Edit<span class="sr-only">, {{ cookedDocument.name }}</span>
              </Anchor>
            </HeadlessMenuItem>
          </HeadlessMenuItems>
        </transition>
      </HeadlessMenu>
    </div>
    <dl class="-my-3 divide-y divide-gray-100 px-6 py-4 text-sm leading-6 text-gray-500 dark:text-gray-200">
      <div class="flex justify-between gap-x-4 py-3">
        <dt>Deadline</dt>
        <dd class="grow flex items-start gap-x-2">
          {{ cookedDocument.externalDeadline?.toLocaleString(DateTime.DATE_FULL) || '-' }}
        </dd>
      </div>
      <div class="flex justify-between gap-x-4 py-3">
        <dt>Pages</dt>
        <dd class="grow flex items-start gap-x-2">{{ cookedDocument.pages || '-' }}</dd>
      </div>
      <div class="flex justify-between gap-x-4 py-3">
        <dt>Assignments</dt>
        <dd>
          <DocumentCardAssignment
            :cooked-document="cookedDocument"
            :document="props.document"
          />
        </dd>
      </div>
    </dl>
  </li>
</template>
<script setup lang="ts">
import { DateTime } from 'luxon'
import type { ResolvedQueueItem, ResolvedPerson } from './AssignmentsTypes'
import { cookQueueItem } from '~/utils/rpc'

type Props = {
  document: ResolvedQueueItem
  selected?: boolean
  editors?: ResolvedPerson[]
  editorAssignedDocuments?: Record<string, ResolvedQueueItem[] | undefined>
}

const props = defineProps<Props>()

const currentTime = useCurrentTime()

const cookedDocument = computed(() => cookQueueItem({
  ...props,
  currentTime
}))
</script>
