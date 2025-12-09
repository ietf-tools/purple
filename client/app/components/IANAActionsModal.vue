<template>
  <form class="py-2 px-4 bg-white text-black dark:bg-black dark:text-white h-full">
    <Heading :heading-level="2" class="pb-3 pt-5">IANA Actions</Heading>
    <IANAActions :heading-level="3" v-model="selectedIANAStatus" />
    <div class="border-t-2 border-gray-400 mt-5 pt-2 flex justify-end">
      <BaseButton btn-type="default" @click="handleSave">Save</BaseButton>
    </div>
  </form>
</template>

<script setup lang="ts">
import { overlayModalKey } from '~/providers/providerKeys';
import { IANAActionsEntries, parseIanaStatusSlug, type IANAActionsEnum } from '../utils/iana'
import type { RfcToBe } from '~/purple_client';

type Props = {
  name: string
  rfcToBe: RfcToBe,
  onSuccess: () => Promise<void>
}

const props = defineProps<Props>()

const defaultOption = IANAActionsEntries?.[0]?.[0]
if (!defaultOption) {
  throw Error('Expected default IANA option')
}

const selectedIANAStatus = ref<IANAActionsEnum | undefined>(parseIanaStatusSlug(props.rfcToBe.ianaStatus?.slug))

const overlayModalKeyInjection = inject(overlayModalKey)

if (!overlayModalKeyInjection) {
  throw Error('Expected injection of overlayModalKey')
}

const api = useApi()

const snackbar = useSnackbar()

const { closeOverlayModal } = overlayModalKeyInjection

const handleSave = async () => {
  try {
    const serverRfcToBe = await api.documentsPartialUpdate({
      draftName: props.name,
      patchedRfcToBeRequest: {
        ianaStatusSlug: selectedIANAStatus.value,
      }
    })
    if (serverRfcToBe.ianaStatus?.slug === selectedIANAStatus.value) {
      await props.onSuccess() // trigger data reload
      closeOverlayModal()
    } else {
      snackbar.add({ type: 'error', title: "Unable to save IANA status", text: "Server didn't say why" })
    }
  } catch (error) {
    snackbarForErrors({ snackbar, error, defaultTitle: "Unable to save IANA status" })
  }

}
</script>
