<template>
  <form class="py-2 px-4 bg-white text-black dark:bg-black dark:text-white h-full">
    <Heading :heading-level="2" class="pb-3 pt-5">IANA Actions</Heading>
    <IANAActions :heading-level="3" v-model="ianaChoice" />
    <div class="border-t-2 border-gray-400 mt-5 pt-2 flex justify-end">
      <BaseButton btn-type="default" @click="handleSave">Save</BaseButton>
    </div>
  </form>
</template>

<script setup lang="ts">
import { overlayModalKey } from '~/providers/providerKeys';
import { IANAActionsEntries, type IANAActionsEnum } from '../utils/iana'

type Props = {
  name: string
  ianaAction: IANAActionsEnum
  onSuccess: () => Promise<void>
}

const props = defineProps<Props>()

const defaultOption = IANAActionsEntries?.[0]?.[0]
if (!defaultOption) {
  throw Error('Expected default IANA option')
}

const ianaChoice = ref<IANAActionsEnum>(props.ianaAction)

const overlayModalKeyInjection = inject(overlayModalKey)

if (!overlayModalKeyInjection) {
  throw Error('Expected injection of overlayModalKey')
}

const { closeOverlayModal } = overlayModalKeyInjection

const handleSave = async () => {
  alert(`TODO: save ${ianaChoice.value} to ${props.name}`)
  await props.onSuccess() // trigger data reload
  closeOverlayModal()
}
</script>
