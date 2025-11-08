<template>
  <div>
    <header class="relative isolate">
      <div class="absolute inset-0 -z-10 overflow-hidden" aria-hidden="true">
        <div class="absolute left-16 top-full -mt-16 transform-gpu opacity-50 blur-3xl xl:left-1/2 xl:-ml-80">
          <div
            class="aspect-[1154/678] w-[72.125rem] bg-gradient-to-br from-[#FF80B5] to-[#9089FC]"
            style="clip-path: polygon(100% 38.5%, 82.6% 100%, 60.2% 37.7%, 52.4% 32.1%, 47.5% 41.8%, 45.2% 65.6%, 27.5% 23.4%, 0.1% 35.3%, 17.9% 0%, 27.7% 23.4%, 76.2% 2.5%, 74.2% 56%, 100% 38.5%)"/>
        </div>
        <div class="absolute inset-x-0 bottom-0 h-px bg-gray-900/5"/>
      </div>

      <div class="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <div class="mx-auto flex max-w-2xl items-center justify-between gap-x-8 lg:mx-0 lg:max-w-none">
          <div class="flex items-center gap-x-6">
            <img
             :src="person?.picture || `https://i.pravatar.cc/150?img=${route.params.id}`"
             :alt="person?.name || 'Person'"
              class="h-16 w-16 flex-none rounded-full ring-1 ring-gray-900/10">
            <h1>
             <span class="mt-1 text-xl font-semibold leading-6 text-gray-900 dark:text-white">
               {{ person?.name || 'Loading...' }}
             </span>
              <br>
             <span class="text-sm leading-6 text-gray-500 dark:text-neutral-400">
               {{ person?.email || '' }}
             </span>
            </h1>
          </div>
          <div class="flex items-center gap-x-4 sm:gap-x-6">
            <a href="#" class="btn-primary">Edit</a>

            <HeadlessMenu as="div" class="relative sm:hidden">
              <HeadlessMenuButton class="-m-3 block p-3">
                <span class="sr-only">More</span>
                <Icon name="uil:bars" class="h-5 w-5 text-gray-500" aria-hidden="true"/>
              </HeadlessMenuButton>

              <transition
                enter-active-class="transition ease-out duration-100"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95">
                <HeadlessMenuItems
                  class="absolute right-0 z-10 mt-0.5 w-32 origin-top-right rounded-md bg-white py-2 shadow-lg ring-1 ring-gray-900/5 focus:outline-none">
                  <HeadlessMenuItem v-slot="{ active }">
                    <button
                      type="button"
                      :class="[active ? 'bg-gray-50' : '', 'block w-full px-3 py-1 text-left text-sm leading-6 text-gray-900']">
                      Copy URL
                    </button>
                  </HeadlessMenuItem>
                  <HeadlessMenuItem v-slot="{ active }">
                    <a
                      href="#"
                      :class="[active ? 'bg-gray-50' : '', 'block px-3 py-1 text-sm leading-6 text-gray-900']">Edit</a>
                  </HeadlessMenuItem>
                </HeadlessMenuItems>
              </transition>
            </HeadlessMenu>
          </div>
        </div>
      </div>
    </header>

    <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div
        class="mx-auto grid max-w-2xl grid-cols-1 grid-rows-1 items-start gap-x-8 gap-y-8 lg:mx-0 lg:max-w-none lg:grid-cols-3">
        <!-- Invoice summary -->
        <div class="lg:col-start-3 lg:row-end-1">
          <h2 class="sr-only">Summary</h2>
          <div class="rounded-lg bg-white dark:bg-neutral-900 shadow-sm ring-1 ring-gray-900/5">
            <dl class="flex flex-wrap">
              <div class="flex-auto pl-6 pt-6">
                <dt class="text-sm font-semibold leading-6 text-gray-900">Availability</dt>
                <dd class="mt-1 text-base font-semibold leading-6 text-gray-900">
                  {{
                    // FIXME: use person?.availability
                    'Unknown'
                  }}
                </dd>
              </div>
              <div class="flex-none self-end px-6 pt-4">
                <dt class="sr-only">Status</dt>
                <dd
                  :class="[
                    person?.isActive === true ? 'bg-green-50 text-green-600 ring-green-600/20' : 'bg-red-50 text-red-600 ring-red-600/20',
                    'rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset'
                  ]">
                  is active
                </dd>
              </div>
              <div class="flex-none self-end px-6 pt-4">
                <dt class="sr-only">Roles</dt>
                <dd class="mt-1 text-base font-semibold leading-6 text-gray-900">
                  Roles: {{ person?.roles && person.roles.length > 0 ? person.roles.join(', ') : 'No roles assigned' }}
                </dd>
              </div>
            </dl>
            <div class="mt-6 border-t border-gray-900/5 px-6 py-6">
              <a href="#" class="text-sm font-semibold leading-6 text-gray-900">Add unavailability period <span
                aria-hidden="true">&rarr;</span></a>
            </div>
          </div>
        </div>
        <div class="lg:col-start-3 lg:row-end-2">
          <!-- Activity feed -->
          <h2 class="text-sm font-semibold leading-6 text-gray-900">Activity (mocked)</h2>
          <ul role="list" class="mt-6 space-y-6">
            <li
              v-for="(activityItem, activityItemIdx) in activity" :key="activityItem.id"
              class="relative flex gap-x-4">
              <div
                :class="[activityItemIdx === activity.length - 1 ? 'h-6' : '-bottom-6', 'absolute left-0 top-0 flex w-6 justify-center']">
                <div class="w-px bg-gray-200"/>
              </div>
              <div class="relative flex h-6 w-6 flex-none items-center justify-center bg-grey-50">
                <Icon
                  v-if="activityItem.type === 'paid'" name="uil:times" class="h-6 w-6 text-indigo-600"
                  aria-hidden="true"/>
                <div v-else class="h-1.5 w-1.5 rounded-full bg-gray-100 ring-1 ring-gray-300"/>
              </div>
              <p class="flex-auto py-0.5 text-xs leading-5 text-gray-500">
                <span class="font-medium text-gray-900">{{ person?.name }}</span> {{ activityItem.type }}
                the
                document.
              </p>
              <time :datetime="activityItem.dateTime" class="flex-none py-0.5 text-xs leading-5 text-gray-500">
                {{ activityItem.date }}
              </time>
            </li>
          </ul>
        </div>
        <!-- Assignments List -->
        <div class="lg:col-span-2 lg:row-span-2">
          <div class="rounded-lg bg-white dark:bg-neutral-900 shadow-sm ring-1 ring-gray-900/5 p-6">
            <h2 class="text-sm font-semibold leading-6 text-gray-900">Active Assignments</h2>
            <div v-if="assignments && assignments.length > 0" class="mt-6">
              <div class="space-y-4">
                <div
                  v-for="assignment in assignments"
                :key="assignment.id"
                  class="border border-gray-200 rounded-lg p-4 bg-gray-50"
                >
                  <div class="flex items-start justify-between">
                    <div class="flex-1">
                      <h3 class="text-sm font-semibold text-gray-900">
                        {{ assignment.rfcToBe?.draft?.name }}
                      </h3>
                      <span v-if="assignment.comment">
                        {{ assignment.comment }}
                      </span>
                      <div class="mt-2 flex items-center gap-4 text-xs text-gray-500">
                        <span>
                          Time spent: {{ assignment.timeSpent }}
                        </span>
                        <span v-if="assignment.state"
                              :class="[
                                assignment.state === 'done' ? 'text-green-600' :
                                assignment.state === 'in_progress' ? 'text-blue-600' :
                                'text-yellow-600'
                              ]">
                          {{ assignment.role }} ({{ assignment.state }})
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          <!-- No assignments message -->
          <div v-else class="mt-6 text-center py-8">
            <p class="text-sm text-gray-500">No current assignments</p>
          </div>
        </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { RpcPerson } from '~/purple_client'

const route = useRoute()
const api = useApi()

// Fetch person data
const { data: person, error } = await useAsyncData(
  `person-${route.params.id}`,
  async () => {
    return await api.rpcPersonRetrieve({ id: Number(route.params.id) })
  }
)

// Fetch person assignments
const { data: assignments } = await useAsyncData(
  `person-assignments-${route.params.id}`,
  async () => {
    return await api.rpcPersonAssignmentsList({ personId: Number(route.params.id) })
  }
)

// Handle error state
if (error.value) {
  throw createError({
    statusCode: 404,
    statusMessage: "Error fetching person"
  })
}

const activity = [
  { id: 1, type: 'created', person: { name: 'Chelsea Hagon' }, date: '7d ago', dateTime: '2023-01-23T10:32' },
  { id: 2, type: 'edited', person: { name: 'Chelsea Hagon' }, date: '6d ago', dateTime: '2023-01-23T11:03' },
  { id: 3, type: 'published', person: { name: 'Chelsea Hagon' }, date: '6d ago', dateTime: '2023-01-23T11:24' }
]
</script>
