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
              src="https://i.pravatar.cc/150?img=5" alt=""
              class="h-16 w-16 flex-none rounded-full ring-1 ring-gray-900/10">
            <h1>
              <span class="mt-1 text-xl font-semibold leading-6 text-gray-900 dark:text-white">Ada Lovelace</span>
              <br>
              <span class="text-sm leading-6 text-gray-500 dark:text-neutral-400">ada.lovelace@ietf.org</span>
            </h1>
          </div>
          <div class="flex items-center gap-x-4 sm:gap-x-6">
            <button type="button" class="hidden text-sm font-semibold leading-6 text-gray-900 sm:block">Link 1</button>
            <a href="#" class="hidden text-sm font-semibold leading-6 text-gray-900 sm:block">Edit</a>
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
                <dd class="mt-1 text-base font-semibold leading-6 text-gray-900">123</dd>
              </div>
              <div class="flex-none self-end px-6 pt-4">
                <dt class="sr-only">Status</dt>
                <dd
                  class="rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-600 ring-1 ring-inset ring-green-600/20">
                  Available
                </dd>
              </div>
              <div class="mt-6 flex w-full flex-none gap-x-4 border-t border-gray-900/5 px-6 pt-6">
                <dt class="flex-none">
                  <span class="sr-only">Client</span>
                  <Icon name="uil:times" class="h-6 w-5 text-gray-400" aria-hidden="true"/>
                </dt>
                <dd class="text-sm font-medium leading-6 text-gray-900">123</dd>
              </div>
              <div class="mt-4 flex w-full flex-none gap-x-4 px-6">
                <dt class="flex-none">
                  <span class="sr-only">Due date</span>
                  <Icon name="uil:times" class="h-6 w-5 text-gray-400" aria-hidden="true"/>
                </dt>
                <dd class="text-sm leading-6 text-gray-500">
                  <time datetime="2023-01-31">123</time>
                </dd>
              </div>
              <div class="mt-4 flex w-full flex-none gap-x-4 px-6">
                <dt class="flex-none">
                  <span class="sr-only">Status</span>
                  <Icon name="uil:times" class="h-6 w-5 text-gray-400" aria-hidden="true"/>
                </dt>
                <dd class="text-sm leading-6 text-gray-500">123</dd>
              </div>
            </dl>
            <div class="mt-6 border-t border-gray-900/5 px-6 py-6">
              <a href="#" class="text-sm font-semibold leading-6 text-gray-900">Add unavailability period <span
                aria-hidden="true">&rarr;</span></a>
            </div>
          </div>
        </div>

        <!-- Invoice -->
        <div
          class="-mx-4 px-4 py-8 bg-white dark:bg-neutral-900 shadow-sm ring-1 ring-gray-900/5 sm:mx-0 sm:rounded-lg sm:px-8 sm:pb-14 lg:col-span-2 lg:row-span-2 lg:row-end-2 xl:px-16 xl:pb-20 xl:pt-16">
          <h2 class="text-base font-semibold leading-6 text-gray-900">Currently working on</h2>
          <dl class="mt-6 grid grid-cols-1 text-sm leading-6 sm:grid-cols-2">
            <div class="sm:pr-4">
              <dt class="inline text-gray-500">Issued on</dt>
              {{ ' ' }}
              <dd class="inline text-gray-700">
                <time datetime="2023-23-01">January 23, 2023</time>
              </dd>
            </div>
            <div class="mt-2 sm:mt-0 sm:pl-4">
              <dt class="inline text-gray-500">Due on</dt>
              {{ ' ' }}
              <dd class="inline text-gray-700">
                <time datetime="2023-31-01">January 31, 2023</time>
              </dd>
            </div>
            <div class="mt-6 border-t border-gray-900/5 pt-6 sm:pr-4">
              <dt class="font-semibold text-gray-900">From</dt>
              <dd class="mt-2 text-gray-500">111</dd>
            </div>
            <div class="mt-8 sm:mt-6 sm:border-t sm:border-gray-900/5 sm:pl-4 sm:pt-6">
              <dt class="font-semibold text-gray-900">To</dt>
              <dd class="mt-2 text-gray-500">111</dd>
            </div>
          </dl>
          <table class="mt-16 w-full whitespace-nowrap text-left text-sm leading-6">
            <colgroup>
              <col class="w-full">
              <col>
              <col>
              <col>
            </colgroup>
            <thead class="border-b border-gray-200 text-gray-900">
            <tr>
              <th scope="col" class="px-0 py-3 font-semibold">Projects</th>
              <th scope="col" class="hidden py-3 pl-8 pr-0 text-right font-semibold sm:table-cell">A</th>
              <th scope="col" class="hidden py-3 pl-8 pr-0 text-right font-semibold sm:table-cell">B</th>
              <th scope="col" class="py-3 pl-8 pr-0 text-right font-semibold">C</th>
            </tr>
            </thead>
          </table>
        </div>

        <div class="lg:col-start-3">
          <!-- Activity feed -->
          <h2 class="text-sm font-semibold leading-6 text-gray-900">Activity</h2>
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
                <span class="font-medium text-gray-900">{{ activityItem.person.name }}</span> {{ activityItem.type }}
                the
                document.
              </p>
              <time :datetime="activityItem.dateTime" class="flex-none py-0.5 text-xs leading-5 text-gray-500">
                {{ activityItem.date }}
              </time>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const activity = [
  { id: 1, type: 'created', person: { name: 'Chelsea Hagon' }, date: '7d ago', dateTime: '2023-01-23T10:32' },
  { id: 2, type: 'edited', person: { name: 'Chelsea Hagon' }, date: '6d ago', dateTime: '2023-01-23T11:03' },
  { id: 3, type: 'published', person: { name: 'Chelsea Hagon' }, date: '6d ago', dateTime: '2023-01-23T11:24' }
]
</script>
