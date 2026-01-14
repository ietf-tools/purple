<template>
  <div>
    <DocHeader :draft-name="draftName" :rfc-to-be="rfcToBe" />

    <DocTabs :current-tab="currentTab" :draft-name="draftName" />

    <div class="mx-auto max-w-7xl py-8">
      <template v-if="step.type === 'cancelled'">
        <div class="text-center">
          Cancelled...
          <BaseButton btn-type="default" @click="fetchAndVerifyMetadata" class="ml-2">
            try again
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
      <template v-else-if="step.type === 'diff'">
        <Heading :heading-level="2" class="px-8 py-4 text-gray-700 dark:text-gray-300">
          Metadata
          {{ SPACE }}
          <template v-if="!step.isMatch">does not match</template>
          <template v-else>matches</template>
        </Heading>
        <p class="ml-8 mb-4 text-sm text-black dark:text-white">
          Fetched git commit
          {{ SPACE }}
          <button class="inline-block rounded-md w-[9em] bg-gray-200 hover:bg-gray-300 focus:bg-gray-300 dark:bg-gray-700 dark:focus:bg-gray-600 dark:hover:bg-gray-600 font-mono p-0.5 truncate" @click="() => step.type === 'diff' && copyGitHashToClipboard(step.gitHash)">
            <Icon name="uil:clipboard-notes" size="1rem" class="align-middle mx-0.5" />{{ step.gitHash }}
          </button>
          {{ SPACE }}
          from
          {{ SPACE }}
          <a :href="step.gitRepoUrl" :class="ANCHOR_STYLE">{{ step.gitRepoUrl }}</a>
        </p>
        <BaseCard>
          <div class="w-full">
            <DiffTable :columns="step.columns" :rows="step.rows" />
          </div>
        </BaseCard>
        <div class="flex justify-between mt-8 pt-4 border-t border-gray-500 dark:border-gray-300">
          <template v-if="step.isMatch">
            <BaseButton btn-type="cancel" @click="cancel">
              Cancel
            </BaseButton>
            <BaseButton btn-type="default" @click="postRfc">
              Post this RFC
            </BaseButton>
          </template>
          <template v-else>
            <BaseButton btn-type="cancel" @click="cancel">
              Cancel
            </BaseButton>
            <BaseButton btn-type="default" @click="updateDatabaseToMatchDocument">
              Update database to match document
            </BaseButton>
          </template>
        </div>
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
import { type DocTabId } from '~/utils/doc'

const route = useRoute()
const api = useApi()

const currentTab: DocTabId = 'publication-preparation'

const draftName = computed(() => route.params.id?.toString() ?? '')

type Step =
  | { type: 'fetchAndVerifyAndMetadataButton' }
  | { type: 'loading' }
  | {
    type: 'diff'
    error?: string
    gitHash: string
    gitRepoUrl: string
    isMatch: boolean
    columns: { nameColumn: string, leftColumn: string, rightColumn: string }
    rows: { rowName: string, rowNameListDepth: number, leftValue?: string, rightValue?: string }[]
  }
  | { type: 'cancelled' }
  | { type: 'databaseUpdated', error?: string }
  | { type: 'rfcPosted', error?: string }

const step = ref<Step>({ type: 'loading' })

const { data: rfcToBe, error: rfcToBeError, status: rfcToBeStatus, refresh: rfcToBeRefresh } = await useAsyncData(
  () => `draft-${draftName.value}`,
  () => api.documentsRetrieve({ draftName: draftName.value }),
  {
    server: false,
    lazy: true,
    deep: true
  }
)

watch(rfcToBe, () => {
  if(!rfcToBe.value) {
    return
  }
  if (rfcToBe.value.disposition === 'published') {
    step.value = { type: 'rfcPosted' }
  } else {
    step.value = { type: 'fetchAndVerifyAndMetadataButton' }
  }
})

const fetchAndVerifyMetadata = async () => {
  step.value = { type: 'loading' }
  // TODO: api for fetch and verifying metadata, with optional error
  await sleep(1000)
  step.value = {
    type: 'diff',
    isMatch: false,
    gitHash: 'b26bf8af130955c5c67cfea96f9532680b963628',
    gitRepoUrl: 'http://github.com/ietf-tools/rfc10000',
    columns: { nameColumn: "Name", leftColumn: "Database", rightColumn: "Document" },
    rows: [
      { rowName: "title", rowNameListDepth: 0, leftValue: "Datagram Congestion Control Protocol (DCCP) Extensions for Multipath Operation with Multiple Addresses", rightValue: "Datagram Congestion Control Protocol (DCCP) Extensions for Multipath Operation with Multiple Addresses" },
      {
        rowName: "abstract", rowNameListDepth: 0, leftValue: `Datagram Congestion Control Protocol (DCCP) communications, as defined in RFC 4340, are inherently restricted to a single path per connection, despite the availability of multiple network paths between peers. The ability to utilize multiple paths simultaneously for a DCCP session can enhance network resource utilization, improve throughput, and increase resilience to network failures, ultimately enhancing the user experience.

  Use cases for Multipath DCCP (MP-DCCP) include mobile devices (e.g., handsets and vehicles) and residential home gateways that maintain simultaneous disconnections to distinct network types such as cellular and Wireless Local Area Networks (WLANs) or cellular and fixed access networks. Compared to existing multipath transport protocols, such as Multipath TCP (MPTCP), MP-DCCP is particularly suited for latency-sensitive applications with varying requirements for reliability and in-order delivery.

  This document specifies a set of protocol extensions to DCCP that enable multipath operations. These extensions maintain the same service model as DCCP while introducing mechanisms to establish and utilize multiple concurrent DCCP flows across different network paths.`, rightValue: `Datagram Congestion Control Protocol (DCCP) communications, as defined in RFC 4340, are inherently restricted to a single path per connection, despite the availability of multiple network paths between peers. The ability to utilize multiple paths simultaneously for a DCCP session can enhance network resource utilization, improve throughput, and increase resilience to network failures, ultimately enhancing the user experience.

  Use cases for Multipath DCCP (MP-DCCP) include mobile devices (e.g., handsets and vehicles) and residential home gateways that maintain simultaneous connections to distinct network types such as cellular and Wireless Local Area Networks (WLANs) or cellular and fixed access networks. Compared to existing multipath transport protocols, such as Multipath TCP (MPTCP), MP-DCCP is particularly suited for latency-sensitive applications with varying requirements for reliability and in-order delivery.

  This document specifies a set of protocol extensions to DCCP that enable multipath operations. These extensions maintain the same service model as DCCP while introducing mechanisms to establish and utilize multiple concurrent DCCP flows across different network paths.` },
      { rowName: "authors:", rowNameListDepth: 0 },
      { rowName: "", rowNameListDepth: 1, leftValue: "John", rightValue: "John" },
      { rowName: "", rowNameListDepth: 1, leftValue: "Jane", rightValue: "Jane" },
      { rowName: "", rowNameListDepth: 1, leftValue: "Jake", rightValue: "Jack" },
      { rowName: "RFC Number", rowNameListDepth: 0, leftValue: "9999", rightValue: "9999" },
      { rowName: "submittedStdLevel", rowNameListDepth: 0, leftValue: "draft", rightValue: "draft" },
    ]
  }
}

const postRfc = async () => {
  step.value = { type: 'loading' }
  // TODO: api to post RFC, with optional error
  await sleep(1000)
  step.value = {
    type: 'rfcPosted'
    // error: 'a problem occurred'
  }
}

const updateDatabaseToMatchDocument = async () => {
  step.value = { type: 'loading' }
  // TODO: api to update database to match document, with optional error
  await sleep(1000)
  step.value = {
    type: 'databaseUpdated',
    // error: 'a problem occurred'
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
