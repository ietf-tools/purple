<template>
  <div class="flex flex-row justify-between items-center">
    <span>
      IANA Action: <span class="font-bold">{{ IANAActionOptions[props.ianaAction] }}</span>
    </span>
    <BaseButton btn-type="default" @click="openModal">Edit</BaseButton>
  </div>
</template>

<script setup lang="ts">
import { overlayModalKey } from '~/providers/providerKeys';
import { type IANAActionsEnum, IANAActionOptions } from '../utils/iana'
import IANAActionsModal from './IANAActionsModal.vue'

type Props = {
  name: string
  ianaAction: IANAActionsEnum
  onSuccess: () => Promise<void>
}

const props = defineProps<Props>()

const overlayModalKeyInjection = inject(overlayModalKey)

if (!overlayModalKeyInjection) {
  throw Error('Expected injection of overlayModalKey')
}

const { openOverlayModal } = overlayModalKeyInjection

const openModal = () => {
 openOverlayModal({
    component: IANAActionsModal,
    componentProps: {
      name: props.name,
      ianaAction: props.ianaAction,
      onSuccess: props.onSuccess
    },
    mode: 'side',
  }).catch(e => {
    if (e === undefined) {
      // ignore... it's just signalling that the modal has closed
    } else {
      console.error(e)
      throw e
    }
  })
}
</script>
