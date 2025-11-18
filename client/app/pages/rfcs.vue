<template>
  <div class="container mx-auto p-6">
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
        Unusable RFC Numbers
      </h1>
      <p class="mt-2 text-gray-600 dark:text-gray-400">
        RFC numbers that have been reserved or are otherwise unavailable for assignment.
      </p>
    </div>

    <div v-if="pending" class="flex justify-center py-8">
      <div class="text-gray-500">Loading unusable RFC numbers...</div>
    </div>

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-md p-4">
      <div class="text-red-800">
        <h3 class="font-medium">Error loading unusable RFC numbers</h3>
        <p class="mt-1 text-sm">{{ error }}</p>
      </div>
    </div>

    <div v-else class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
      <div v-if="unusableRfcs.length === 0" class="p-6 text-center text-gray-500">
        No unusable RFC numbers found.
      </div>

      <ul v-else class="divide-y divide-gray-200 dark:divide-gray-700">
        <li
          v-for="unusableRfc in unusableRfcs"
          :key="unusableRfc.number"
          class="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-700"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="flex items-start gap-4 min-w-0 flex-1">
              <div class="flex-shrink-0">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
                  RFC {{ unusableRfc.number }}
                </span>
              </div>
              <div class="min-w-0 flex-1 max-w-2xl">
                <div class="text-sm font-medium text-gray-900 dark:text-white">
                  {{ unusableRfc.comment || 'No comment provided' }}
                </div>
              </div>
            </div>
            <div class="flex-shrink-0 text-sm text-gray-500 dark:text-gray-400">
              Reserved on {{ formatDate(unusableRfc.createdAt) }}
            </div>
          </div>
        </li>
      </ul>

      <div v-if="unusableRfcs.length > 0" class="bg-gray-50 dark:bg-gray-700 px-6 py-3">
        <div class="text-sm text-gray-600 dark:text-gray-300">
          Total: {{ unusableRfcs.length }} unusable RFC number{{ unusableRfcs.length !== 1 ? 's' : '' }}
        </div>
      </div>
    </div>

    <!-- Refresh button -->
    <div class="mt-6 flex justify-end">
      <button
        @click="refresh"
        :disabled="pending"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
      >
        <Icon name="heroicons:arrow-path" class="h-4 w-4 mr-2" />
        Refresh
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { UnusableRfcNumber } from '~/purple_client'

const api = useApi()

const {
  data: unusableRfcs,
  pending,
  error,
  refresh,
} = await useAsyncData(
  'unusable-rfc-numbers',
  () => api.unusableRfcNumbersList(),
  {
    server: false,
    lazy: true,
    default: () => [] as UnusableRfcNumber[],
  }
)

const formatDate = (dateString: string | undefined) => {
  if (!dateString) return 'Unknown'
  return new Date(dateString).toLocaleDateString()
}

// Set page metadata
useHead({
  title: 'Unusable RFC Numbers',
  meta: [
    { name: 'description', content: 'List of RFC numbers that are reserved or unavailable for assignment' }
  ]
})
</script>
