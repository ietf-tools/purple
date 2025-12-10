<template>
  <div class="flex flex-row justify-between items-center">
    <span>
      IANA Action: <span class="font-bold">{{ props.rfcToBe.ianaStatus?.desc ?? '(none)' }}</span>
    </span>
    <BaseButton btn-type="default" @click="openModal">Edit</BaseButton>
  </div>
</template>

<script setup lang="ts">
import { overlayModalKey } from '~/providers/providerKeys';
import IANAActionsModal from './IANAActionsModal.vue'
import type { RfcToBe } from '~/purple_client';

type Props = {
  name: string
  rfcToBe: RfcToBe
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
      rfcToBe: props.rfcToBe,
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
