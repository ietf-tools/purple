<template>
  <BaseCard>
    <template #header>
      <CardHeader title="Document Info" />
    </template>
    <div v-if="rfcToBe">
      <DescriptionList>
        <DescriptionListItem term="Title" :details="rfcToBe.title" />
        <DescriptionListItem term="Authors">
          <DescriptionListDetails>
            <div class="mx-0 text-sm font-medium">
              <div v-if="rfcToBe.authors.length === 0">None</div>
              <div v-else>
                <div
                  v-for="author of rfcToBe.authors"
                  :key="author.id"
                  class="py-1"
                >
                  <a :href="author.email ? datatrackerPersonLink(author.email) : undefined" :class="ANCHOR_STYLE">
                    <span class="font-bold">{{ author.titlepageName }}</span>
                    <span class="font-normal" v-if="author.id">{{ SPACE }}{{ ` #${author.id}` }}</span>
                    <span v-if="author.isEditor">(editor)</span>
                  </a>
                </div>
              </div>
            </div>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem
          term="Submitted Pages"
          :details="rfcToBe.draft?.pages?.toString()"
        />
        <DescriptionListItem
          term="Document Shepherd"
          details="Dolly Shepherd (mocked)"
        />
        <DescriptionListItem term="Stream">
          <DescriptionListDetails>
            {{ rfcToBe.intendedStream }}
            <span v-if="rfcToBe.submittedStream !== rfcToBe.intendedStream">
              (submitted as {{ rfcToBe.submittedStream }})
            </span>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem
          term="Stream Manager"
          details="Ari Drecker (mocked)"
        />
        <DescriptionListItem
          term="Submitted Format"
          :details="rfcToBe.submittedFormat"
        />
        <DescriptionListItem term="Submitted Boilerplate">
          <DescriptionListDetails
            >{{ rfcToBe.intendedBoilerplate }}
            <span
              v-if="rfcToBe.submittedBoilerplate !== rfcToBe.intendedBoilerplate"
            >
              (submitted as {{ rfcToBe.submittedBoilerplate }})
            </span>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Standard Level">
          <DescriptionListDetails>
            {{ rfcToBe.intendedStdLevel }}
            <span v-if="rfcToBe.submittedStdLevel !== rfcToBe.intendedStdLevel">
              (submitted as {{ rfcToBe.submittedStdLevel }})
            </span>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Disposition" :details="rfcToBe.disposition" />
        <DescriptionListItem term="RFC Number">
          <DescriptionListDetails>
            <div class="flex items-center gap-2">
              <input
                v-model="rfcNumberInput"
                type="text"
                placeholder="Enter RFC number"
                class="px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                :disabled="isUpdating"
                @blur="updateRfcNumber"
              />
              <span v-if="isUpdating" class="text-sm text-gray-500">Updating...</span>
            </div>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Consensus">
          <DescriptionListDetails>
            <span
              v-if="rfcToBe.consensus === true"
              class="text-green-600"
            >
              Yes
            </span>
            <span
              v-else-if="rfcToBe.consensus === false"
              class="text-red-600"
            >
              No
            </span>
            <span
              v-else
              class="text-gray-500"
            >
              Unknown
            </span>
          </DescriptionListDetails>
        </DescriptionListItem>
      </DescriptionList>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import type { RfcToBe } from '~/purple_client'

type Props = {
  rfcToBe: RfcToBe | null | undefined
  draftName: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  update: [rfcToBe: RfcToBe]
  refresh: []
}>()

const api = useApi()
const snackbar = useSnackbar()
const rfcNumberInput = ref('')
const isUpdating = ref(false)

watch(() => props.rfcToBe?.rfcNumber, (newValue) => {
  rfcNumberInput.value = newValue?.toString() || ''
}, { immediate: true })

const updateRfcNumber = async () => {
  if (isUpdating.value) return

  const newValue = rfcNumberInput.value.trim()

  // Validate that input is a valid number or empty
  if (newValue && !/^\d+$/.test(newValue)) {
    snackbar.add({
      type: 'error',
      title: 'Invalid RFC number',
      text: 'RFC number must be a valid number'
    })
    rfcNumberInput.value = props.rfcToBe?.rfcNumber?.toString() || ''
    return
  }

  const rfcNumber = newValue ? parseInt(newValue) : null

  if (rfcNumber === props.rfcToBe?.rfcNumber) return

  try {
    isUpdating.value = true

    await api.documentsPartialUpdate({
      draftName: props.draftName,
      patchedRfcToBeRequest: { rfcNumber: rfcNumber }
    })

    snackbar.add({
      type: 'success',
      title: `Updated RFC number for "${props.draftName}"`,
      text: ''
    })

  } catch (e: unknown) {
    snackbarForErrors({
      snackbar,
      defaultTitle: `Unable to update RFC number for "${props.draftName}"`,
      error: e
    })

    rfcNumberInput.value = props.rfcToBe?.rfcNumber?.toString() || ''
  } finally {
    isUpdating.value = false
    // Refresh the parent component
    emit('refresh')
  }
}
</script>
