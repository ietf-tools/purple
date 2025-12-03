<template>
  <input v-model="rfcNumberInput" type="text" placeholder="Enter RFC number"
    class="px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
    @blur="updateRfcNumber" />
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

const formatRfcNumberForInput = (rfcNumber: RfcToBe['rfcNumber']): string => `${props.initialRfcNumber ?? ''}`

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

  const newValue = rfcNumberInput.value.trim()

  // Validate that input is a valid number or empty
  if (newValue.length === 0 || !/^\d+$/.test(newValue)) {
    snackbar.add({
      type: 'error',
      title: 'Invalid RFC number',
      text: `${JSON.stringify(newValue)} is not a valid RFC number`
    })
    return
  }

  const newRfcNumber = newValue ? parseInt(newValue, 10) : null

  if (newRfcNumber === initialRfcNumber) {
    console.info("No change to RFC number. Not updating.")
    return
  }

  if (newRfcNumber === null) {
    snackbar.add({
      type: 'error',
      title: "Can't update to invalid RFC number",
      text: `${JSON.stringify(newValue)} is not a valid RFC number`
    })
  }

  try {
    const newRfcToBe = await api.documentsPartialUpdate({
      draftName: name,
      patchedRfcToBeRequest: { rfcNumber: newRfcNumber }
    })

    if (newRfcToBe.rfcNumber === newRfcNumber) {
      snackbar.add({
        type: 'success',
        title: `${JSON.stringify(name)}'s RFC number now ${newRfcNumber}'`,
        text: ''
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
      defaultTitle: `Unable to update RFC number to ${JSON.stringify(newRfcNumber)} for "${JSON.stringify(name)}"`,
      error: e
    })
  }
}
</script>
