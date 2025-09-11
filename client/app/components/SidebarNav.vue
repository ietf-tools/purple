<template>
  <HeadlessTransitionRoot as="template" :show="siteStore.sidebarIsOpen">
    <HeadlessDialog as="div" class="relative z-50 lg:hidden" @close="siteStore.sidebarIsOpen = false">
      <HeadlessTransitionChild as="template" enter="transition-opacity ease-linear duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="transition-opacity ease-linear duration-300" leave-from="opacity-100" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-900/80" />
      </HeadlessTransitionChild>

      <div class="fixed inset-0 flex">
        <HeadlessTransitionChild as="template" enter="transition ease-in-out duration-300 transform" enter-from="-translate-x-full" enter-to="translate-x-0" leave="transition ease-in-out duration-300 transform" leave-from="translate-x-0" leave-to="-translate-x-full">
          <HeadlessDialogPanel class="relative mr-16 flex w-full max-w-xs flex-1">
            <HeadlessTransitionChild as="template" enter="ease-in-out duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in-out duration-300" leave-from="opacity-100" leave-to="opacity-0">
              <div class="absolute left-full top-0 flex w-16 justify-center pt-5">
                <button type="button" class="-m-2.5 p-2.5" @click="siteStore.sidebarIsOpen = false">
                  <span class="sr-only">Close sidebar</span>
                  <Icon name="uil:times" class="h-6 w-6 text-white" aria-hidden="true" />
                </button>
              </div>
            </HeadlessTransitionChild>
            <div class="flex grow flex-col gap-y-5 overflow-y-auto bg-white px-6 pb-2">
              <div class="flex h-16 shrink-0 items-center text-violet-500 dark:text-violet-300 font-light">
                <SvgoRpcIcon filled class="mr-2 text-xl" />
                RFC Production Center
              </div>
              <nav class="flex flex-1 flex-col">
                <ul role="list" class="flex flex-1 flex-col gap-y-7">
                  <li>
                    <ul role="list" class="-mx-2 space-y-1">
                      <li v-for="item in navigation" :key="item.name">
                        <Anchor :href="item.href" :class="[item.current ? 'bg-gray-50 text-violet-600' : 'text-gray-700 hover:text-violet-600 hover:bg-gray-50', 'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold']">
                          <component :is="item.icon" :class="[item.current ? 'text-violet-600' : 'text-gray-400 group-hover:text-violet-600', 'h-6 w-6 shrink-0']" aria-hidden="true" />
                          {{ item.name }}
                        </Anchor>
                      </li>
                    </ul>
                  </li>
                  <li>
                    <div class="text-xs font-semibold leading-6 text-gray-400">Your teams</div>
                    <ul role="list" class="-mx-2 mt-2 space-y-1">
                      <li v-for="team in teams" :key="team.name">
                        <Anchor :href="team.href" :class="[team.current ? 'bg-gray-50 text-violet-600' : 'text-gray-700 hover:text-violet-600 hover:bg-gray-50', 'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold']">
                          <span :class="[team.current ? 'text-violet-600 border-violet-600' : 'text-gray-400 border-gray-200 group-hover:border-violet-600 group-hover:text-violet-600', 'flex h-6 w-6 shrink-0 items-center justify-center rounded-lg border text-[0.625rem] font-medium bg-white']">{{ team.initial }}</span>
                          <span class="truncate">{{ team.name }}</span>
                        </Anchor>
                      </li>
                    </ul>
                  </li>
                </ul>
              </nav>
            </div>
          </HeadlessDialogPanel>
        </HeadlessTransitionChild>
      </div>
    </HeadlessDialog>
  </HeadlessTransitionRoot>

  <!-- Static sidebar for desktop -->
  <div class="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-72 lg:flex-col">
    <!-- Sidebar component, swap this element with another sidebar if you like -->
    <div class="flex grow flex-col gap-y-5 overflow-y-auto border-r border-gray-200 dark:border-violet-600 bg-white dark:bg-violet-900 bg-gradient-to-tr from-violet-50 to-white dark:from-violet-950 dark:to-violet-900 px-6">
      <div class="flex h-16 shrink-0 items-center text-violet-500 dark:text-violet-300 font-light">
        <SvgoRpcIcon filled class="mr-2 text-xl" />
        <span class="font-medium mr-1">RFC</span> Production Center
      </div>
      <nav class="flex flex-1 flex-col">
        <ul role="list" class="flex flex-1 flex-col gap-y-7">
          <li>
            <ul role="list" class="-mx-2 space-y-1">
              <li v-for="item in navigation" :key="item.name">
                <Anchor :href="item.href" :class="[item.href === currentBaseLink ? 'bg-violet-50 dark:bg-violet-600 text-violet-600 dark:text-white' : 'text-gray-700 dark:text-violet-300 hover:text-violet-600 hover:bg-violet-50 dark:hover:text-violet-100 dark:hover:bg-violet-800', 'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold']">
                  <component :is="item.icon" :class="[item.href === currentBaseLink ? 'text-violet-600 dark:text-white' : 'text-gray-400 dark:text-violet-400 group-hover:text-violet-600 dark:group-hover:text-violet-100', 'h-6 w-6 shrink-0']" aria-hidden="true" />
                  {{ item.name }}
                </Anchor>
              </li>
            </ul>
          </li>
          <li>
            <div class="text-xs font-semibold leading-6 text-gray-400 dark:text-violet-400">Misc</div>
            <ul role="list" class="-mx-2 mt-2 space-y-1">
              <li v-for="link in links" :key="link.name">
                <Anchor :href="link.href" :class="[link.href === currentBaseLink ? 'bg-gray-50 text-violet-600' : 'text-gray-700 dark:text-violet-300 hover:text-violet-600 hover:bg-gray-50 dark:hover:bg-violet-800', 'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold']">
                  <component :is="link.icon" :class="[link.href === currentBaseLink ? 'text-violet-600 dark:text-white' : 'text-gray-400 dark:text-violet-400 group-hover:text-violet-600 dark:group-hover:text-violet-100', 'h-6 w-6 shrink-0']" aria-hidden="true" />
                  <span class="truncate">{{ link.name }}</span>
                </Anchor>
              </li>
            </ul>
          </li>
          <li class="mx-3 mt-auto">
            <span class="cursor-pointer select-none text-purple-50 dark:text-purple-950 hover:text-purple-500 dark:hover:text-purple-800 text-xs font-medium" @click="pi">π</span>
          </li>
          <li class="-mx-6">
            <a :href="$config.public.datatrackerBase" class="flex items-center gap-x-4 px-6 py-3 text-sm font-semibold leading-6 text-gray-500 dark:text-violet-400 hover:text-violet-500 dark:hover:text-violet-200 hover:bg-violet-500/5">
              <Icon name="solar:database-bold-duotone" class="h-8 w-8 opacity-70" aria-hidden="true" />
              <span>Go to Datatracker</span>
            </a>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useSiteStore } from '@/stores/site'
import { Icon } from '#components'
import confetti from 'canvas-confetti'

// STORES

const siteStore = useSiteStore()
const userStore = useUserStore()

// ROUTER

const route = useRoute()
const currentBaseLink = computed(() => route.path.indexOf('/', 1) > 0 ? `/${route.path.split('/')[1]}` : route.path)

// DATA

type Navigation = {
  name: string
  href: string
  icon: ReturnType<typeof h>
  current?: boolean
}

const navigation: Navigation[] = [
  { name: 'Dashboard', href: '/', icon: h(Icon, { name: 'solar:widget-6-bold-duotone' }) },
  { name: 'Queue', href: '/queue', icon: h(Icon, { name: 'solar:layers-minimalistic-bold-duotone' }) },
  { name: 'My Documents', href: '/docs', icon: h(Icon, { name: 'solar:documents-minimalistic-line-duotone' }) },
  { name: 'Team', href: '/team', icon: h(Icon, { name: 'solar:users-group-rounded-bold-duotone' }) },
  { name: 'Statistics', href: '/stats', icon: h(Icon, { name: 'solar:chart-line-duotone' }) },
  { name: 'Final Reviews', href: '/auth48', icon: h(Icon, { name: 'solar:diploma-verified-broken' }) }
]

type Team = {
  name: string
  href: string
  current: boolean
  initial: string
}

const teams: Team[] = []

const links = computed(() => {
  const val = userStore.isManager
    ? [
        { name: 'Manage RFC Numbers', href: '/rfcs', icon: h(Icon, { name: 'fluent-mdl2:number-field' }) },
        { name: 'Cluster Management', href: '/clusters', icon: h(Icon, { name: 'pajamas:group' }) },
        { name: 'Legal Requests', href: '/legal', icon: h(Icon, { name: 'octicon:law-24' }) }
      ]
    : []

  // links for everyone
  val.push(
    { name: 'Manage Labels', href: '/labels', icon: h(Icon, { name: 'pajamas:labels' }) }
  )
  return val
})

// METHODS

function pi () {
  const end = Date.now() + (5 * 1000)
  const colors = ['#c084fc', '#14b8a6']

  ;(function frame () {
    confetti({
      particleCount: 2,
      angle: 60,
      spread: 55,
      origin: { x: 0 },
      colors
    })
    confetti({
      particleCount: 2,
      angle: 120,
      spread: 55,
      origin: { x: 1 },
      colors
    })

    if (Date.now() < end) {
      requestAnimationFrame(frame)
    } else {
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 }
      })
    }
  }())
}
</script>
