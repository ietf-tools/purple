<template>
  <div class="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 dark:border-neutral-700 bg-white dark:bg-neutral-900 px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8" :id="STICKY_DOM_ID">
    <button type="button" class="-m-2.5 p-2.5 text-gray-700 lg:hidden" @click="siteStore.sidebarIsOpen = true">
      <span class="sr-only">Open sidebar</span>
      <Icon name="uil:bars" class="h-6 w-6" aria-hidden="true" />
    </button>

    <!-- Separator -->
    <div class="h-6 w-px bg-gray-900/10 lg:hidden" aria-hidden="true" />

    <div class="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
      <form class="relative flex flex-1" action="#" method="GET" @submit.prevent>
        <label for="search-field" class="sr-only">Search</label>
        <Icon name="uil:search" class="pointer-events-none absolute inset-y-0 left-0 h-full w-5 text-gray-400" aria-hidden="true" />
        <input id="search-field" v-model="navSearch" class="block h-full w-full border-0 py-0 pl-8 pr-0 bg-white dark:bg-neutral-900 text-gray-900 dark:text-neutral-200 placeholder:text-gray-400 dark:placeholder:text-neutral-400 focus:ring-0 sm:text-sm"
          placeholder="Search docs by draft name, RFC number or author" type="search" name="search" autocomplete="off" @focus="showResults = true" @blur="onSearchBlur" >
        <div
          v-if="showResults && navSearch.length >= 4"
          class="absolute left-0 top-full z-50 mt-1 w-full min-w-[280px] max-h-[60vh] overflow-y-auto rounded-lg border bg-white dark:bg-neutral-800 shadow-xl"
        >
          <div v-if="searchLoading" class="flex items-center justify-center gap-2 py-4 text-sm text-gray-500 dark:text-neutral-400">
            <Icon name="ei:spinner-3" class="animate-spin" size="1.2em" />
            Searching...
          </div>
          <div v-else-if="!searchResults?.results?.length" class="py-4 text-center text-sm text-gray-500 dark:text-neutral-400">(no matches)</div>
          <ul v-else class="divide-y divide-gray-100 dark:divide-neutral-700">
            <li v-for="doc in searchResults.results" :key="doc.id">
              <button
                type="button"
                class="flex w-full items-baseline gap-2 px-4 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-neutral-700"
                @mousedown.prevent="navigateTo(`/docs/${doc.name}`); navSearch = ''; showResults = false"
              >
                <span class="font-semibold text-gray-900 dark:text-neutral-100">{{ doc.name }}</span>
                <span v-if="doc.rfcNumber" class="text-xs text-gray-500 dark:text-neutral-400">RFC {{ doc.rfcNumber }}</span>
                <span v-if="doc.title" class="truncate text-xs text-gray-400 dark:text-neutral-500">{{ doc.title }}</span>
                <span v-if="doc.disposition" :class="dispositionClass(doc.disposition)" class="ml-auto shrink-0 rounded-full px-2 py-0.5 text-xs font-medium">{{ doc.disposition }}</span>
              </button>
            </li>
          </ul>
        </div>
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

        <!-- Separator -->
        <div class="hidden lg:block lg:h-6 lg:w-px lg:bg-gray-900/10 dark:lg:bg-white/20" aria-hidden="true" />

        <!-- Profile dropdown -->
        <HeadlessMenu v-if="userStore.authenticated" as="div" class="relative">
          <HeadlessMenuButton class="-m-1.5 flex items-center p-1.5">
            <span class="sr-only">Open user menu</span>
            <img class="h-8 max-w-16 rounded-full bg-gray-50" :src="userStore.avatar ?? undefined" alt="" >
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
import { refDebounced } from '@vueuse/core'
import { useSiteStore } from '@/stores/site'
import { useUserStore } from '@/stores/user'
import { STICKY_DOM_ID } from '~/utils/scroll'

const buttonId = useId() // avoid a hydration error - see https://github.com/nuxt/ui/issues/1171

// STORES

const siteStore = useSiteStore()
const userStore = useUserStore()

// DATA

const userNavigation = [
  { name: 'Your profile', href: '/' }
]

// SEARCH

const api = useApi()
type DocumentsSearchResponse = Awaited<ReturnType<typeof api.documentsSearch>>

const navSearch = ref('')
const showResults = ref(false)
const searchLoading = ref(false)
const searchResults = ref<DocumentsSearchResponse>()

const debouncedSearch = refDebounced(navSearch, 250)

let previousAbortController: AbortController | undefined

watch(debouncedSearch, async (q) => {
  if (previousAbortController) {
    previousAbortController.abort()
  }
  if (q.length < 4) {
    searchResults.value = undefined
    return
  }
  previousAbortController = new AbortController()
  searchLoading.value = true
  try {
    searchResults.value = await api.documentsSearch(
      { q },
      { signal: previousAbortController.signal }
    )
  } catch {
    // aborted or network error — ignore
  } finally {
    searchLoading.value = false
  }
})

const onSearchBlur = () => {
  // small delay so a click on a result fires before we hide the list
  setTimeout(() => { showResults.value = false }, 150)
}

const dispositionClass = (disposition: string) => {
  switch (disposition) {
    case 'created':     return 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300'
    case 'in_progress': return 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300'
    case 'published':   return 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300'
    case 'withdrawn':   return 'bg-red-100 text-red-600 dark:bg-red-900/40 dark:text-red-300'
    default:            return 'bg-gray-100 text-gray-500 dark:bg-neutral-700 dark:text-neutral-400'
  }
}

</script>
