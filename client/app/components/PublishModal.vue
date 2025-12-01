<template>
  <div class="h-full flex flex-col bg-white text-black dark:bg-black dark:text-white">
    <div class="flex flex-row justify-between border-b border-gray-300">
      <h1 class="text-xl font-bold pt-4 px-4 py-3">
        Publish
        <span class="text-2xl mx-1 font-mono whitespace-nowrap">
          <span class="font-bold">RFC</span> {{ props.rfcToBe.rfcNumber }}
        </span>?
        <span class="text-sm text-gray-700 dark:text-gray-300">
          <br />
          (<span class="font-mono">{{ props.rfcToBe.name }}</span>)
        </span>
      </h1>

      <BaseButton btnType="cancel" class="m-2 flex items-center" @click="closeOverlayModal">
        <Icon name="uil:times" class="h-5 w-5" aria-hidden="true" />
      </BaseButton>
    </div>
    <div class="flex-1 overflow-y-scroll px-4 pt-4 pb-7 grid grid-cols-2 gap-4">
      <div>
        <BaseCard>
          <template #header>
            <CardHeader :title="`Complexity Indicators (${complexityItems.length})`" />
          </template>
          <ul class="list-disc flex flex-col gap-1 ml-4">
            <li v-for="complexityItem in complexityItems" class="pl-1 text-sm">
              <RpcLabel :label="complexityItem" />
            </li>
          </ul>
          <p v-if="complexityItems.length === 0" class="italic">(none)</p>
        </BaseCard>

        <BaseCard>
          <template #header>
            <CardHeader title="Final Checks" />
          </template>
          <ul>
            <li v-for="finalCheckItem of finalChecksItems">
              <RpcCheckbox :label="finalCheckItem.label" :id="finalCheckItem.id" :checked="finalCheckItem.isChecked" />
            </li>
          </ul>
        </BaseCard>

        <BaseCard>
          <template #header>
            <CardHeader title="Cleared Exceptions" />
          </template>
          <ul>
            <li v-for="clearedExceptionsItem of clearedExceptionsItems">
              <RpcCheckbox :label="clearedExceptionsItem.label" :id="clearedExceptionsItem.id"
                :checked="clearedExceptionsItem.isChecked" />
            </li>
          </ul>
        </BaseCard>

        <BaseCard>
          <template #header>
            <CardHeader title="Comments" />
          </template>
          <ul>
            Do we need this? Comments are on the underlying page
          </ul>
        </BaseCard>
      </div>
      <DocInfoCard is-read-only :rfc-to-be="props.rfcToBe" :draft-name="props.rfcToBe.name ?? ''"
        @refresh="props.onSuccess" />
    </div>
    <div class="border-t-1 border-gray-800 flex justify-end items-center">
      <BaseButton btnType="default" class="m-2 flex items-center" @click="handlePublish">
        Publish (mocked)
      </BaseButton>
    </div>
  </div>
</template>
<script setup lang="ts">
import { BaseButton } from '#components'
import { overlayModalKey } from '~/providers/providerKeys';
import type { Label, RfcToBe } from '~/purple_client';

type Props = {
  rfcToBe: RfcToBe
  labels: Label[]
  onSuccess: () => void
}

const props = defineProps<Props>()

const overlayModalKeyInjection = inject(overlayModalKey)

if (!overlayModalKeyInjection) {
  throw Error('Expected injection of overlayModalKey')
}

const complexityItems = computed(() => {
  return props.labels.filter(label => {
    const { id } = label
    if (typeof id !== 'number') {
      throw Error('Expected label id to be a number')
    }
    return props.rfcToBe.labels.includes(id) && label.isComplexity
  })
})

const finalChecksItems = computed(() => [
  { isChecked: false, label: "Version control", id: 'version-controls' },
  { isChecked: false, label: "XML comments removed", id: 'xml-comments-removed' },
  { isChecked: false, label: "Journal comments addressed", id: 'journal-comments-addressed' },
  { isChecked: false, label: "IANA nits resolved", id: 'iana-nits-resolved' },
  { isChecked: false, label: "Current date", id: 'current-date' },
  { isChecked: false, label: "References checked", id: 'references-checked' },
  { isChecked: false, label: "Spelling checked", id: 'spelling-checked' },
  { isChecked: false, label: "Dupes checked", id: 'dupes-checked' },
  { isChecked: false, label: "non-ASCII checked", id: 'non-ascii-checked' },
  { isChecked: false, label: "BCP 14 tags checked", id: 'bcp14-tags-checked' },
  { isChecked: false, label: "Articles checked", id: 'articles-checked' },
  { isChecked: false, label: "Metadata correct", id: 'metadata-correct' },
])

const clearedExceptionsItems = computed(() => [
  { isChecked: false, label: "Version mismatch", id: 'version-mismatch' },
  { isChecked: false, label: "Font issues", id: 'font-issues' },
  { isChecked: false, label: "Conversion to V3 XML failed", id: 'conversion-to-v3-xml-failed' },
])

const { closeOverlayModal } = overlayModalKeyInjection

const handlePublish = () => {
  alert("this doesn't work yet")
  closeOverlayModal()
}
</script>
