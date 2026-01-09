<template>
  <div class="flex gap-1 items-center">
    <select v-model="selectedSlug" class="px-2 py-1 w-[6em] min-w-[6em] max-w-[6em] text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-black dark:bg-black dark:text-white">
      <option v-for="sub in subseriesOptions" :key="sub.slug" :value="sub.slug">
        {{ sub.slug.toUpperCase() }}
      </option>
    </select>
    <input v-model="subseriesNumber" type="number" min="0" class="px-2 py-1 w-[5em] text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-black dark:bg-black dark:text-white" placeholder="Number" />
    <BaseButton @click="updateSubseries" btn-type="outline" size="xs">Save</BaseButton>
    <button
      v-if="props.initialSubseries && props.initialSubseries.id"
      @click="deleteSubseries"
      class="w-5 h-5 flex items-center justify-center text-[10px] border border-red-400 rounded text-red-400 bg-white dark:bg-black hover:bg-red-50 dark:hover:bg-red-900"
      title="Delete subseries"
    >&#10006;</button>
  </div>
</template>

<script setup lang="ts">
const deleteSubseries = async () => {
  if (!(props.initialSubseries && props.initialSubseries.id)) return
  try {
    await api.subseriesMembersDestroy({ id: props.initialSubseries.id })
    snackbar.add({ type: 'success', title: 'Subseries deleted', text: 'Subseries deleted' })
    props.onSuccess()
  } catch (e) {
    snackbar.add({ type: 'error', title: 'Failed to delete subseries', text: String(e) })
  }
}
import { ref, onMounted, watch } from 'vue'
import type { RfcToBe, SubseriesMember } from '~/purple_client'

const props = defineProps<{
  id: RfcToBe["id"]
  initialSubseries: SubseriesMember | null
  onSuccess: () => void
}>()

const api = useApi()
const snackbar = useSnackbar()

const subseriesOptions = ref<Array<{ slug: string, name: string }>>([])
const selectedSlug = ref('')
const subseriesNumber = ref('')

if (props.initialSubseries) {
  selectedSlug.value = props.initialSubseries.slug ?? ''
  subseriesNumber.value = props.initialSubseries.number?.toString() ?? ''
}

onMounted(async () => {
  try {
    const response = await api.subseriesTypesList()
    subseriesOptions.value = response.map((item: any) => ({ slug: item.slug, name: item.name }))
    if (props.initialSubseries && props.initialSubseries.slug) {
      const found = subseriesOptions.value.find(opt => opt.slug === props.initialSubseries!.type)
      if (found) selectedSlug.value = found.slug
    }
  } catch (e) {
    snackbar.add({ type: 'error', title: 'Failed to load subseries types', text: String(e) })
  }
})

watch(() => props.initialSubseries, () => {
  if (props.initialSubseries) {
    if (props.initialSubseries.slug) {
      const found = subseriesOptions.value.find(opt => opt.slug === props.initialSubseries!.type)
      selectedSlug.value = found ? found.slug : props.initialSubseries.slug
    } else {
      selectedSlug.value = ''
    }
    subseriesNumber.value = props.initialSubseries.number?.toString() ?? ''
  } else {
    selectedSlug.value = ''
    subseriesNumber.value = ''
  }
}, { immediate: true })

const updateSubseries = async () => {
  try {
    let payload: any = {
      type: selectedSlug.value,
      number: subseriesNumber.value ? Number(subseriesNumber.value) : undefined
    }
    if (props.initialSubseries && props.initialSubseries.id) {
      await api.subseriesMembersPartialUpdate({
        id: props.initialSubseries.id,
        patchedSubseriesMemberRequest: payload
      })
      snackbar.add({ type: 'success', title: `Subseries updated`, text: `Subseries updated` })
    } else {
      payload = { ...payload, rfcToBe: Number(props.id) }
      await api.subseriesMembersCreate({
        subseriesMemberRequest: payload
      })
      snackbar.add({ type: 'success', title: `Subseries added`, text: `Subseries added` })
      selectedSlug.value = ''
      subseriesNumber.value = ''
    }
    props.onSuccess()
  } catch (e: unknown) {
    snackbar.add({ type: 'error', title: `Failed to update subseries`, text: String(e) })
  }
}
</script>

<style>
.input-number-no-spinners,
.input-number-no-spinners::-webkit-inner-spin-button,
.input-number-no-spinners::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
</style>
