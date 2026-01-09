<template>
  <div class="p-6">
    <h1 class="text-xl font-bold mb-4">Subseries List</h1>
    <nav class="mb-6 flex flex-wrap gap-4">
      <template v-for="type in subseriesTypes" :key="type.slug">
        <a :href="`#subseries-type-${type.slug}`" class="px-3 py-1 rounded bg-gray-100 hover:bg-gray-200 text-sm font-medium text-gray-700">
          {{ type.name }} <span class="text-xs text-gray-500">({{ type.slug }})</span>
        </a>
      </template>
    </nav>
    <template v-for="(group, idx) in groupedSubseries" :key="group.type">
      <h2 :id="`subseries-type-${group.type}`" class="text-lg font-semibold mt-8 mb-2">Type: {{ group.type.toUpperCase() }}</h2>
      <table class="min-w-full border border-gray-300 rounded mb-8">
        <thead class="bg-gray-100">
          <tr>
            <th class="px-3 py-2 text-left" style="width: 160px;">Display Name</th>
            <th class="px-3 py-2 text-left" style="width: 300px;">RFCs</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in group.items" :key="item.slug" class="border-t align-top">
            <td class="px-3 py-2 font-semibold" style="width: 160px;">{{ item.displayName }}</td>
            <td class="px-3 py-2 text-xs" style="width: 300px;">
              <template v-if="item.documents && item.documents.length">
                <span>
                  <template v-for="(doc, i) in item.documents" :key="doc.name + '-' + doc.rfcNumber">
                    <template v-if="doc.name.startsWith('draft-')">
                      <NuxtLink :to="`/docs/${doc.name}`" class="text-blue-600 hover:underline">
                        {{ doc.rfcNumber }}
                      </NuxtLink>
                    </template>
                    <template v-else>
                      {{ doc.rfcNumber }}
                    </template>
                    <span v-if="i < item.documents.length - 1">, </span>
                  </template>
                </span>
              </template>
              <span v-else class="text-gray-400 italic">No documents</span>
            </td>
          </tr>
        </tbody>
      </table>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useApi } from '~/composables/useApi'

const api = useApi()
const subseriesList = ref<any[]>([])
const subseriesTypes = ref<any[]>([])

onMounted(async () => {
  try {
    const [listResponse, typesResponse] = await Promise.all([
      api.subseriesList(),
      api.subseriesTypesList()
    ])
    subseriesList.value = listResponse
    subseriesTypes.value = typesResponse
  } catch (e) {
    subseriesList.value = []
    subseriesTypes.value = []
  }
})

const groupedSubseries = computed(() => {
  const groups: Record<string, { type: string, items: any[] }> = {}
  for (const item of subseriesList.value) {
    const type = item.type || 'Unknown'
    if (!groups[type]) {
      groups[type] = { type, items: [] }
    }
    groups[type].items.push(item)
  }
  return Object.values(groups)
})
</script>
