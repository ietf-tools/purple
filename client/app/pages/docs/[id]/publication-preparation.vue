<template>
  <div>
    <DocHeader :draft-name="draftName" :rfc-to-be="rfcToBe" />

    <DocTabs :current-tab="currentTab" :draft-name="draftName" />

    <div class="mx-auto max-w-7xl py-8">
      <template v-if="step.type === 'cancelled'">
        <div class="text-center font-bold mr-1">
          Cancelled
        </div>
        <div class="text-center">
          <BaseButton btn-type="default" @click="fetchAndVerifyMetadata" class="ml-2">
            Try again
          </BaseButton>
        </div>
      </template>
      <template v-else-if="step.type === 'fetchAndVerifyAndMetadataButton'">
        <div class="text-center">
          <BaseButton btn-type="default" @click="fetchAndVerifyMetadata">
            Fetch and verify metadata
          </BaseButton>
        </div>
      </template>
      <template v-else-if="step.type === 'loading'">
        <div class="text-center">
          <div class="mx-auto w-[3.5em] h-[3.5em] mb-3 bg-white rounded-md">
            <Icon name="ei:spinner-3" size="3.5em" class="animate-spin" />
          </div>
        </div>
      </template>
      <template v-else-if="step.type === 'error'">
        <div class="text-center mb-3 max-w-sm m-auto">
          <span class="font-bold mr-1">Error:</span> <span class="font-mono">{{ step.errorText }}</span>
        </div>
        <div :class="step.showDeleteAndRetryButton ? 'flex justify-between' : 'text-center'">
          <BaseButton v-if="step.showDeleteAndRetryButton" btn-type="outline"
            @click="deleteMetadataValidationAndRetry(step.showDeleteAndRetryButton.headSha)">
            Retry metadata validation
          </BaseButton>
          <BaseButton v-if="step.showResyncButton" btn-type="default" @click="fetchAndVerifyMetadata" class="ml-2">
            Try again
          </BaseButton>
        </div>
      </template>
      <template v-else-if="step.type === 'diff'">
        <Heading :heading-level="2"
          :class="['px-8 py-4', step.status === 'success' ? 'text-gray-700 dark:text-gray-300' : 'text-red-800 dark:text-red-300']">
          <span v-if="step.status === 'success'" class="font-bold">Metadata validation completed</span>
          <template v-else>
            <span class="font-bold mr-1">Metadata validation failed:</span>
            {{ step.status ?? '(unknown status)' }}
          </template>
        </Heading>
        <p v-if="step.isError" class="ml-8 mb-4 text-red-800 dark:text-red-300 font-bold">Validation error</p>
        <p class="ml-8 mb-4 text-sm text-sm text-black dark:text-white">
          Metadata
          {{ SPACE }}
          <span v-if="!step.isMatch" class="text-red-800 dark:text-red-300">does not match</span>
          {{ SPACE }}
          <span v-if="step.isMatch" class="text-green-800 dark:text-green-300">matches</span>
          {{ SPACE }}
          <span v-if="!step.isError">
            but it can be published.
          </span>
          {{ SPACE }}
          <span v-if="step.isError">
            and it <span class="font-bold">cannot be published</span>.
          </span>
        </p>
        <p v-if="step.headSha" class="ml-8 mb-4 text-sm text-black dark:text-white">
          Fetched git commit
          {{ SPACE }}
          <button
            class="inline-block rounded-md w-[9em] bg-gray-200 hover:bg-gray-300 focus:bg-gray-300 dark:bg-gray-700 dark:focus:bg-gray-600 dark:hover:bg-gray-600 font-mono p-0.5 truncate"
            @click="() => step.type === 'diff' && step.headSha ? copyGitHashToClipboard(step.headSha) : undefined">
            <Icon name="uil:clipboard-notes" size="1rem" class="align-middle mx-0.5" />{{ step.headSha }}
          </button>
          {{ SPACE }}
          from
          {{ SPACE }}
          <a :href="step.repository ? gitHubUrlBuilder(step.repository) : undefined" :class="ANCHOR_STYLE">{{
            step.repository
            }}</a>
        </p>
        <p v-else class="ml-8 mb-4 text-sm text-black dark:text-white">
          No git commit available in API response. Can't publish until this is verified.
        </p>
        <p v-if="step.detail && step.detail.length > 0"
          class="bg-yellow-200 text-yellow-900 dark:bg-yellow-700 text-sm dark:text-white p-2 mx-6 my-2">
          <Icon name="uil:info-circle" size="1rem" class="mr-2" />
          {{ step.detail }}
        </p>
        <BaseCard>
          <div class="w-full">
            <DiffTable v-if="step.metadataCompare" :columns="diffColumns" :rows="step.metadataCompare" />
            <p v-else class="text-center">(no diff available)</p>
          </div>
        </BaseCard>
        <template v-if="step.status === 'success'">
          <div v-if="step.headSha" class="flex justify-between mx-6 mt-10 mb-10">
            <div>
              <BaseButton btn-type="cancel" @click="cancel">
                Cancel
              </BaseButton>
            </div>
            <div>
              <template v-if="step.headSha">
                <BaseButton btn-type="secondary"
                  @click="() => step.type === 'diff' && step.headSha ? deleteMetadataValidationAndRetry(step.headSha) : console.error('internal error unhandled state (1)', step)">
                  Redo metadata validation
                </BaseButton>
              </template>
            </div>
            <div class="flex gap-2 justify-end">
              <BaseButton v-if="step.canAutofix" btn-type="default" @click="metadataValidationResultsSyncHandler">
                Update database to match document
              </BaseButton>
              <BaseButton v-if="!step.isError" btn-type="default" @click="publishRfc">
                Publish this RFC
              </BaseButton>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="flex justify-center mt-8 pt-4 border-t border-gray-300 dark:border-gray-300">
            <BaseButton btn-type="secondary"
              @click="() => step.type === 'diff' && step.headSha ? deleteMetadataValidationAndRetry(step.headSha) : console.error('internal error unhandled state (2)', step)">
              Redo metadata validation
            </BaseButton>
          </div>
        </template>
      </template>
      <template v-else-if="step.type === 'databaseUpdated'">
        <template v-if="step.error">
          <div class="text-center">
            <Heading :heading-level="3" class="px-8 py-4 text-gray-700 dark:text-gray-300">
              Unable to update database
            </Heading>
            <div class="mt-4 mb-8 text-sm"><span :class="[badgeColors.red, 'p-2']">Error: {{ step.error }}</span></div>
            <BaseButton btn-type="default" @click="fetchAndVerifyMetadata" class="ml-2">
              Fetch and verify metadata
            </BaseButton>
          </div>
        </template>
        <template v-else>
          <div class="text-center">
            <Heading :heading-level="3" class="px-8 py-4 text-gray-700 dark:text-gray-300">
              Database updated
            </Heading>
            <BaseButton btn-type="default" @click="fetchAndVerifyMetadata" class="ml-2">
              Fetch and verify metadata
            </BaseButton>
          </div>
        </template>
      </template>
      <template v-else-if="step.type === 'rfcPosted'">
        <template v-if="step.error">
          <div class="text-center">
            <Heading :heading-level="3" class="px-8 py-4 text-gray-700 dark:text-gray-300">
              Unable to post RFC
            </Heading>
            <div class="mt-4 mb-8 text-sm"><span :class="[badgeColors.red, 'p-2']">Error: {{ step.error }}</span></div>
            <BaseButton btn-type="default" @click="fetchAndVerifyMetadata" class="ml-2">
              Fetch and verify metadata
            </BaseButton>
          </div>
        </template>
        <template v-else>
          <div class="text-center">
            <Heading :heading-level="3" class="px-8 py-4 text-gray-700 dark:text-gray-300">
              RFC Posted
            </Heading>
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAsyncData } from '#app'
import BaseButton from '~/components/BaseButton.vue'
import type { MetadataValidationResults } from '~/purple_client'
import { type DocTabId } from '~/utils/doc'

const route = useRoute()
const api = useApi()

const currentTab: DocTabId = 'publication-preparation'

const draftName = computed(() => route.params.id?.toString() ?? '')

const diffColumns = { nameColumn: "Name", leftColumn: "Database", rightColumn: "Document" }

type Step =
  | { type: 'fetchAndVerifyAndMetadataButton' }
  | { type: 'loading' }
  | { type: 'error', errorText: string, showResyncButton?: boolean, showDeleteAndRetryButton?: { headSha: string } }
  | {
    type: 'diff'
    error?: string
  } & MetadataValidationResults
  | { type: 'cancelled' }
  | { type: 'databaseUpdated', error?: string }
  | { type: 'rfcPosted', error?: string, }

const step = ref<Step>({ type: 'loading' })

const { data: rfcToBe, error: rfcToBeError, status: rfcToBeStatus, refresh: rfcToBeRefresh } = await useAsyncData(
  () => `draft-${draftName.value}`,
  () => api.documentsRetrieve({ draftName: draftName.value }),
  {
    server: false,
    lazy: true,
  }
)

watch([rfcToBe, rfcToBeError], () => {
  if (!rfcToBe.value) {
    if (rfcToBeError.value) {
      console.error('Unable to load RFC. Server error:', rfcToBeError.value)
      step.value = {
        type: 'error',
        errorText: `Unable to load RFC ${draftName.value}. Server error: ${rfcToBeError.value.message}`
      }
    }
    return
  }
  if (rfcToBe.value.disposition === 'published') {
    step.value = { type: 'rfcPosted' }
  } else {
    step.value = { type: 'fetchAndVerifyAndMetadataButton' }
  }
})

const MAXIMUM_ATTEMPTS_DURATION_MS = 10 * 1000
const WAIT_BETWEEN_REQUESTS_MS = 1000

const fetchAndVerifyMetadata = async () => {
  let resultsCreate: MetadataValidationResults | undefined = undefined

  step.value = { type: 'loading' }

  const startTimeMs = Date.now()
  let hasTimedOut = false
  const endTimeMs = startTimeMs + MAXIMUM_ATTEMPTS_DURATION_MS
  let attemptCount = 0

  try {
    do {
      attemptCount++
      resultsCreate = await api.metadataValidationResultsCreate({ draftName: draftName.value })
      hasTimedOut = Date.now() > endTimeMs
      console.log({ hasTimedOut, attemptCount, resultsCreate })
      await sleep(WAIT_BETWEEN_REQUESTS_MS)
    } while (!hasTimedOut && resultsCreate.status === 'pending')
  } catch (error) {
    console.error("Couldn't start/poll for metadata sync results.", { error, resultsCreate })
    step.value = {
      type: 'error',
      errorText: `Couldn't start/poll for metadata sync results. Error: ${error}`,
      showDeleteAndRetryButton: resultsCreate?.headSha ? { headSha: resultsCreate.headSha } : undefined,
      showResyncButton: true
    }
    if (!resultsCreate) {
      return
    }
  }

  console.log("Finished", { hasTimedOut, resultsCreate })

  if (resultsCreate.status === 'failed') {
    const { headSha } = resultsCreate
    if (!headSha) {
      console.error("Git hash (head sha) not found", resultsCreate)
      snackbar.add({ type: 'error', title: 'git hash (head sha) was expected but none was provided', text: 'See dev console for more' })
      return
    }
    step.value = {
      type: 'error',
      errorText: `Failed to validate metadata. Request status was still ${JSON.stringify(resultsCreate.status)}.`,
      showDeleteAndRetryButton: { headSha },
      showResyncButton: true
    }
  } else if (resultsCreate.status !== 'success') {
    step.value = {
      type: 'error',
      errorText: `Failed to validate metadata. Request status was still ${JSON.stringify(resultsCreate.status)}.`,
      showResyncButton: true
    }
    return
  }

  step.value = {
    type: 'diff',
    ...resultsCreate
  }
}

const deleteMetadataValidationAndRetry = async (headSha?: string) => {
  if (!headSha) {
    console.trace()
    console.error("no git hash (head sha) found at step", step.value)
    snackbar.add({ type: 'error', title: 'internal error, expected git hash (head sha) param', text: 'See dev console for more' })
    return
  }
  step.value = { type: 'loading' }
  try {
    await api.documentsMetadataValidationResultsDestroy({
      draftName: draftName.value,
      headSha
    })
    fetchAndVerifyMetadata()
  } catch (error: unknown) {
    snackbarForErrors({ snackbar, error, defaultTitle: "Couldn't delete validation results" })
    step.value = {
      type: 'error',
      errorText: "Couldn't delete validation results",
      showDeleteAndRetryButton: { headSha },
      showResyncButton: true
    }
  }
}

const publishRfc = async () => {
  const currentStep = step.value
  if (currentStep.type !== 'diff') {
    throw Error(`Can't publish from step ${currentStep.type}`)
  }
  const { headSha } = currentStep
  if (!headSha) {
    console.error("Can't publish without git hash (head sha)", currentStep)
    snackbar.add({ type: 'error', title: "Can't publish without git hash (head sha) but none were provided", text: '' })
    return
  }
  step.value = { type: 'loading' }
  try {
    // API will not return anything when successful
    // when it's unsuccessful it will return HTTP 500
    // which the js api client THROWs an error on
    void await api.documentsPublish({
      draftName: draftName.value,
      publishRfcRequest: {
        headSha,
      }
    })
    // if it got this far it was successful
    step.value = {
      type: 'rfcPosted'
    }
  } catch (e: unknown) {
    step.value = {
      type: 'rfcPosted',
      error: `Problem publishing: ${e}`
    }
  }
}

const metadataValidationResultsSyncHandler = async () => {
  const currentStep = step.value
  if (currentStep.type !== 'diff') {
    throw Error(`Can't publish from step ${currentStep.type}`)
  }
  const { headSha } = currentStep
  if (!headSha) {
    console.error("Can't publish without git hash (head sha) but none were in 'step'", currentStep)
    snackbar.add({ type: 'error', title: "Can't publish without git hash (head sha) but none were provided", text: 'See dev console for more' })
    return
  }
  step.value = { type: 'loading' }

  const metadataValidationResults = await api.metadataValidationResultsSync({
    draftName: draftName.value,
    syncMetadataRequestRequest: {
      headSha,
    }
  })

  step.value = {
    type: 'diff',
    ...metadataValidationResults,
  }
}

const cancel = () => {
  step.value = { type: "cancelled" }
}

const snackbar = useSnackbar()

const copyGitHashToClipboard = async (gitHash: string) => {
  const isCopied = await copyToClipboard(gitHash)
  if (isCopied) {
    snackbar.add({
      type: 'success',
      text: 'Git hash copied to clipboard'
    })
  } else {
    snackbar.add({
      type: 'error',
      text: "Couldn't copy git hash to clipboard. Permissions error?"
    })
  }
}
</script>
