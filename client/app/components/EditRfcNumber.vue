<template>
  <div class="flex gap-1">
    <input v-model="rfcNumberInput" type="number" class="px-2f py-1 w-[6em] font-mono text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 input-number-no-spinners" />
    <BaseButton @click="updateRfcNumber" btn-type="outline" size="xs">Save</BaseButton>
  </div>
</template>

<script setup lang="ts">
import type { RfcToBe } from '~/purple_client';

type Props = {
  name: RfcToBe["name"]
  initialRfcNumber: RfcToBe["rfcNumber"]
  onSuccess: () => void
}

const props = defineProps<Props>()

const api = useApi()

const snackbar = useSnackbar()

const formatRfcNumberForInput = (rfcNumber: RfcToBe['rfcNumber']): string => `${rfcNumber ?? ''}`

const rfcNumberInput = ref(formatRfcNumberForInput(props.initialRfcNumber))

watch(() => props.initialRfcNumber, () => {
  rfcNumberInput.value = formatRfcNumberForInput(props.initialRfcNumber)
}, { immediate: true })

const updateRfcNumber = async () => {
  const { name, initialRfcNumber } = props
  if (!name) {
    snackbar.add({
      type: 'error',
      title: "RFC lacks draft name so can't edit RFC number",
      text: ``
    })
    return
  }

  const newValue = rfcNumberInput.value.toString().trim()

  // Validate that input is a valid number or empty
  if (newValue.length > 1 && !/^\d+$/.test(newValue)) {
    snackbar.add({
      type: 'error',
      title: 'Invalid RFC number',
      text: `${JSON.stringify(newValue)} is not a valid RFC number`
    })
    return
  }

  const newRfcNumber = newValue ? parseInt(newValue, 10) : null

  if (newRfcNumber === initialRfcNumber) {
      snackbar.add({
      type: 'info',
      title: 'No change to RFC number.',
      text: `Not saving.`
    })
    return
  }

  try {
    const newRfcToBe = await api.documentsPartialUpdate({
      draftName: name,
      patchedRfcToBeRequest: { rfcNumber: newRfcNumber }
    })

    // The server can respond with undefined so we need to coerce undefined to null to compare it
    const serverRfcNumber = newRfcToBe.rfcNumber ?? null

    if (serverRfcNumber === newRfcNumber) {
      snackbar.add({
        type: 'success',
        title: serverRfcNumber === null ? `RFC number removed` : `RFC number now ${newRfcNumber}`,
        text: `${JSON.stringify(name)} updated`
      })
      props.onSuccess()
    } else {
      snackbar.add({
        type: 'error',
        title: `Failed to update RFC number to "${newRfcNumber}"`,
        text: "The server didn't say why"
      })
    }

  } catch (e: unknown) {
    snackbarForErrors({
      snackbar,
      defaultTitle: `Failed to update RFC number to ${newRfcNumber}`,
      error: e
    })
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
