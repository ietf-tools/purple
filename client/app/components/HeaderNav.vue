<template>
  <div class="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 dark:border-neutral-700 bg-white dark:bg-neutral-900 px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
    <button type="button" class="-m-2.5 p-2.5 text-gray-700 lg:hidden" @click="siteStore.sidebarIsOpen = true">
      <span class="sr-only">Open sidebar</span>
      <Icon name="uil:bars" class="h-6 w-6" aria-hidden="true" />
    </button>

    <!-- Separator -->
    <div class="h-6 w-px bg-gray-900/10 lg:hidden" aria-hidden="true" />

    <div class="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
      <form class="relative flex flex-1" action="#" method="GET">
        <label for="search-field" class="sr-only">Search</label>
        <Icon name="uil:search" class="pointer-events-none absolute inset-y-0 left-0 h-full w-5 text-gray-400" aria-hidden="true" />
        <input id="search-field" v-model="siteStore.search" class="block h-full w-full border-0 py-0 pl-8 pr-0 bg-white dark:bg-neutral-900 text-gray-900 dark:text-neutral-200 placeholder:text-gray-400 dark:placeholder:text-neutral-400 focus:ring-0 sm:text-sm" placeholder="Search..." type="search" name="search" >
      </form>
      <div class="flex items-center gap-x-4 lg:gap-x-6">
        <!-- Site Theme Switcher -->
        <HeadlessMenu as="div" class="relative inline-block mr-2">
          <HeadlessMenuButton :id="buttonId" class="rounded focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-500">
            <span class="sr-only">Site Theme</span>
            <ColorScheme placeholder="..." tag="span">
              <Icon v-if="$colorMode.value === 'dark'" name="solar:moon-bold-duotone" class="text-gray-500 dark:text-neutral-400 hover:text-violet-400 dark:hover:text-violet-400" size="1.25em" aria-hidden="true" />
              <Icon v-else name="solar:sun-2-line-duotone" class="text-gray-500 dark:text-white hover:text-violet-400 dark:hover:text-violet-400" size="1.25em" aria-hidden="true" />
            </ColorScheme>
          </HeadlessMenuButton>

          <transition enter-active-class="transition ease-out duration-100" enter-from-class="transform opacity-0 scale-95" enter-to-class="transform opacity-100 scale-100" leave-active-class="transition ease-in duration-75" leave-from-class="transform opacity-100 scale-100" leave-to-class="transform opacity-0 scale-95">
            <HeadlessMenuItems class="absolute right-0 z-10 mt-2 w-40 origin-top-right rounded-md bg-white dark:bg-neutral-800/90 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
              <div class="py-1">
                <HeadlessMenuItem v-slot="{ active }">
                  <button type="button" :class="['block w-full', active ? 'text-violet-500 dark:text-violet-300 bg-violet-50 dark:bg-violet-500/5' : 'text-gray-700 dark:text-gray-100', 'flex items-center px-4 py-2 text-sm cursor-pointer']" @click="$colorMode.preference = 'dark'">
                    <Icon name="solar:moon-bold-duotone" class="mr-3" />
                    Dark
                  </button>
                </HeadlessMenuItem>
                <HeadlessMenuItem v-slot="{ active }">
                  <button type="button" :class="['block w-full', active ? 'text-violet-500 dark:text-violet-300 bg-violet-50 dark:bg-violet-500/5' : 'text-gray-700 dark:text-gray-100', 'flex items-center px-4 py-2 text-sm cursor-pointer']" @click="$colorMode.preference = 'light'">
                    <Icon name="solar:sun-2-line-duotone" class="mr-3" />
                    Light
                  </button>
                </HeadlessMenuItem>
                <HeadlessMenuItem v-slot="{ active }">
                  <button type="button" :class="['block w-full', active ? 'text-violet-500 dark:text-violet-300 bg-violet-50 dark:bg-violet-500/5' : 'text-gray-700 dark:text-gray-100', 'flex items-center px-4 py-2 text-sm cursor-pointer']" @click="$colorMode.preference = 'system'">
                    <Icon name="solar:laptop-line-duotone" class="mr-3" />
                    System
                  </button>
                </HeadlessMenuItem>
              </div>
            </HeadlessMenuItems>
          </transition>
        </HeadlessMenu>

        <!-- View Notifications -->
        <button v-if="userStore.authenticated" type="button" class="-m-2.5 mx-2 text-gray-400 dark:text-neutral-400 hover:text-gray-500 dark:hover:text-violet-400">
          <span class="sr-only">View notifications</span>
          <Icon name="solar:bell-bold-duotone" size="1.25em" aria-hidden="true" />
        </button>

        <!-- Select User (for demo only) -->
        <HeadlessMenu v-if="allUsers && allUsers.length > 0" as="div" class="relative">
          <HeadlessMenuButton class="-m-2.5 mx-2 text-gray-400 dark:text-neutral-400 hover:text-gray-500 dark:hover:text-violet-400">
            <span class="sr-only">Select user (for demo only)</span>
            <Icon name="solar:users-group-two-rounded-line-duotone" size="1.25em" aria-hidden="true" />
          </HeadlessMenuButton>
          <transition enter-active-class="transition ease-out duration-100" enter-from-class="transform opacity-0 scale-95" enter-to-class="transform opacity-100 scale-100" leave-active-class="transition ease-in duration-75" leave-from-class="transform opacity-100 scale-100" leave-to-class="transform opacity-0 scale-95">
            <HeadlessMenuItems class="absolute left-0 z-10 mt-2.5 min-w-max origin-top-left rounded-md bg-white py-2 shadow-lg ring-1 ring-gray-900/5 focus:outline-none">
              <HeadlessMenuItem v-if="userStore.pretendingToBe" v-slot="{ active }">
                <div
                  :class="[active ? 'bg-gray-50' : '', 'block px-3 py-1 text-sm leading-6 text-gray-900']"
                  @click="switchUser(null)">
                  Yourself
                </div>
              </HeadlessMenuItem>
              <HeadlessMenuItem v-for="item in allUsers" :key="item.id" v-slot="{ active }">
                <div
                  :class="[active ? 'bg-gray-50' : '', 'block px-3 py-1 text-sm leading-6 text-gray-900']"
                  @click="switchUser(item.id ?? null)">
                  <Icon
                    v-if="item.id === userStore.pretendingToBe"
                    name="uil:arrow-right" class="h-6 w-6 -ml-1" aria-hidden="true" />
                  {{ item.name }}
                </div>
              </HeadlessMenuItem>
            </HeadlessMenuItems>
          </transition>
        </HeadlessMenu>

        <!-- Separator -->
        <div class="hidden lg:block lg:h-6 lg:w-px lg:bg-gray-900/10 dark:lg:bg-white/20" aria-hidden="true" />

        <!-- Profile dropdown -->
        <HeadlessMenu v-if="userStore.authenticated" as="div" class="relative">
          <HeadlessMenuButton class="-m-1.5 flex items-center p-1.5">
            <span class="sr-only">Open user menu</span>
            <img class="h-8 w-6 rounded-full bg-gray-50" :src="userStore.avatar ?? undefined" alt="" >
            <span class="hidden lg:flex lg:items-center">
              <span class="ml-4 text-sm font-semibold leading-6 text-gray-900 dark:text-neutral-300" aria-hidden="true">{{ userStore.name }}</span>
              <Icon name="uil:angle-down" class="ml-2 h-5 w-5 text-gray-400 dark:text-neutral-400" aria-hidden="true" />
            </span>
          </HeadlessMenuButton>
          <transition enter-active-class="transition ease-out duration-100" enter-from-class="transform opacity-0 scale-95" enter-to-class="transform opacity-100 scale-100" leave-active-class="transition ease-in duration-75" leave-from-class="transform opacity-100 scale-100" leave-to-class="transform opacity-0 scale-95">
            <HeadlessMenuItems class="absolute right-0 z-10 mt-2.5 w-32 origin-top-right rounded-md bg-white py-2 shadow-lg ring-1 ring-gray-900/5 focus:outline-none">
              <HeadlessMenuItem v-for="item in userNavigation" :key="item.name" v-slot="{ active }">
                <Anchor :href="item.href" :class="[active ? 'bg-gray-50' : '', 'block px-3 py-1 text-sm leading-6 text-gray-900']">{{ item.name }}</Anchor>
              </HeadlessMenuItem>
              <HeadlessMenuItem v-slot="{ active }">
                <a
                  :class="[active ? 'bg-gray-50' : '', 'block w-full px-3 py-1 text-sm leading-6 text-gray-900 text-left']"
                  href="/oidc/logout/">
                  Sign out
                </a>
              </HeadlessMenuItem>
            </HeadlessMenuItems>
          </transition>
        </HeadlessMenu>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useSiteStore } from '@/stores/site'
import { useUserStore } from '@/stores/user'

const api = useApi()
const csrf = useCookie('csrftoken', { sameSite: 'strict' })
const buttonId = useId() // avoid a hydration error - see https://github.com/nuxt/ui/issues/1171

// STORES

const siteStore = useSiteStore()
const userStore = useUserStore()

// FUNCTIONS

function switchUser (rpcPersonId: number | null) {
  userStore.pretendToBe(rpcPersonId)
}
// DATA

const userNavigation = [
  { name: 'Your profile', href: '/' }
]

const { data: allUsers } = await useAsyncData(
  'allUsers',
  async () => {
    try {
      return await api.rpcPersonList()
    } catch {
      // nop
    }
  },
  {
    default: () => ([]),
    server: false,
    transform: (resp) => resp?.toSorted((a, b) => {
      if (!a.name && !b.name) {
        return 0
      }
      if (!a.name) {
        return -1
      }
      if (!b.name) {
        return 1
      }
      return a.name.localeCompare(b.name)
    })
  }
)

</script>
