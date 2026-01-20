<template>
  <BaseCard>
    <template #header>
      <CardHeader title="Document Info" />
    </template>
    <div v-if="rfcToBe">
      <DescriptionList>
        <DescriptionListItem term="Title" :spacing="spacing">
          <DescriptionListDetails>
            <PatchRfcToBeField
              key="title"
              :is-read-only="props.isReadOnly"
              :ui-mode="{ type: 'textbox', placeholder: 'title', rows: 5 }"
              :draft-name="rfcToBe.name!"
              :initial-value="rfcToBe.title"
              :on-success="() => props.refresh?.()"
            >
              {{ rfcToBe.title }}
            </PatchRfcToBeField>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Authors" :spacing="spacing">
          <DescriptionListDetails>
            <div class="flex flex-row items-center h-full mx-0 text-sm font-medium">
              <div v-if="rfcToBe.authors.length === 0">None</div>
              <div v-else>
                <div v-for="author of rfcToBe.authors" :key="author.id" class="py-1">
                  <a :href="author.email ? datatrackerPersonLink(author.email) : undefined" :class="ANCHOR_STYLE">
                    <span :class="ANCHOR_STYLE">{{ author.titlepageName }}</span>
                    <span :class="PERSON_ID_STYLE" v-if="author.email">{{ SPACE }}{{ ` (${author.email})` }}</span>
                    <span v-if="author.isEditor">(editor)</span>
                  </a>
                  <div class="text-xs text-gray-500" v-if="author.affiliation">
                    {{ author.affiliation }}
                  </div>
                </div>
              </div>
              <div>
                <Anchor :href="draftAssignmentsHref(props.rfcToBe?.name, 'edit-authors')" :class="[classForBtnType.outline, 'px-2 py-1']"><Icon name="uil:pen" /></Anchor>
              </div>
            </div>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Submitted Pages" :spacing="spacing">
          <DescriptionListDetails>
            <PatchRfcToBeField
              key="pages"
              :is-read-only="props.isReadOnly"
              :ui-mode="{ type: 'textbox', placeholder: 'title', isNumber: true, rows: 1 }"
              :draft-name="rfcToBe.name ?? ''"
              :initial-value="rfcToBe.draft?.pages?.toString()"
              :on-success="() => props.refresh?.()"
            >
              {{ rfcToBe.draft?.pages?.toString() }}
            </PatchRfcToBeField>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Document Shepherd" :spacing="spacing">
          <DescriptionListDetails>
            <div class="flex flex-row items-center h-full mx-0 text-sm font-medium">
              <span class="flex-1">Dolly Shepherd (mocked)</span>
              <span v-if="!props.isReadOnly">
                <Anchor :href="draftAssignmentsHref(props.rfcToBe?.name, 'edit-document-shepherd')" :class="[classForBtnType.outline, 'px-2 py-1']"><Icon name="uil:pen" /></Anchor>
              </span>
            </div>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Stream" :spacing="spacing">
          <DescriptionListDetails>
            <PatchRfcToBeField
              key="intendedStream"
              :is-read-only="props.isReadOnly"
              :ui-mode="{ type: 'select', options: loadStreams }"
              :draft-name="rfcToBe.name ?? ''"
              :initial-value="rfcToBe.intendedStream"
              :on-success="() => props.refresh?.()"
            >
              <span class="flex-1">
                {{ rfcToBe.intendedStream }}
                <span v-if="rfcToBe.submittedStream !== rfcToBe.intendedStream">
                  (submitted as {{ rfcToBe.submittedStream }})
                </span>
              </span>
            </PatchRfcToBeField>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Stream Manager" :spacing="spacing">
          <DescriptionListDetails>
            <div class="flex flex-row items-center h-full mx-0 text-sm font-medium">
              <span class="flex-1">Ari Drecker (mocked)</span>
              <span v-if="!props.isReadOnly">
                <Anchor :href="draftAssignmentsHref(props.rfcToBe?.name, 'edit-stream-manger')" :class="[classForBtnType.outline, 'px-2 py-1']"><Icon name="uil:pen" /></Anchor>
              </span>
            </div>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Submitted Format" :spacing="spacing">
          <DescriptionListDetails>
            <PatchRfcToBeField
              key="submittedFormat"
              :is-read-only="props.isReadOnly"
              :ui-mode="{ type: 'select', options: loadFormats }"
              :draft-name="rfcToBe.name ?? ''"
              :initial-value="rfcToBe.submittedFormat"
              :on-success="() => props.refresh?.()"
            >
              {{ rfcToBe.submittedFormat }}
            </PatchRfcToBeField>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Submitted Boilerplate" :spacing="spacing">
          <DescriptionListDetails>
            <PatchRfcToBeField
              key="intendedBoilerplate"
              :is-read-only="props.isReadOnly"
              :ui-mode="{ type: 'select', options: loadBoilerplates }"
              :draft-name="rfcToBe.name ?? ''"
              :initial-value="rfcToBe.submittedFormat"
              :on-success="() => props.refresh?.()"
            >
              {{ rfcToBe.intendedBoilerplate }}
              <span v-if="rfcToBe.submittedBoilerplate !== rfcToBe.intendedBoilerplate">
                (submitted as {{ rfcToBe.submittedBoilerplate }})
              </span>
            </PatchRfcToBeField>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Standard Level" :spacing="spacing">
          <DescriptionListDetails>
            <PatchRfcToBeField
              key="intendedStdLevel"
              :is-read-only="props.isReadOnly"
              :ui-mode="{ type: 'select', options: loadStandardLevels }"
              :draft-name="rfcToBe.name ?? ''"
              :initial-value="rfcToBe.intendedStdLevel"
              :on-success="() => props.refresh?.()"
            >
              {{ rfcToBe.intendedStdLevel }}
              <span v-if="rfcToBe.submittedStdLevel !== rfcToBe.intendedStdLevel">
                (submitted as {{ rfcToBe.submittedStdLevel }})
              </span>
            </PatchRfcToBeField>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Subseries" :spacing="spacing">
          <DescriptionListDetails>
            <div v-if="!props.isReadOnly && rfcToBe.disposition !== 'published'">
              <template v-if="rfcToBe.subseries && rfcToBe.subseries.length > 0">
                <div v-for="(sub, idx) in rfcToBe.subseries" :key="idx">
                  <EditSubseries
                    :id="rfcToBe.id"
                    :initial-subseries="sub"
                    :on-success="() => props.refresh?.()"
                  >
                    {{ sub.displayName }}<span v-if="idx < rfcToBe.subseries.length - 1">, </span>
                  </EditSubseries>
                </div>
              </template>
              <template v-else>
                <EditSubseries
                  :id="rfcToBe.id"
                  :initial-subseries="null"
                  :on-success="() => props.refresh?.()"
                >
                  (none)
                </EditSubseries>
              </template>
            </div>
            <div v-else>
              <span v-if="rfcToBe.subseries && rfcToBe.subseries.length > 0">
                <span v-for="(sub, idx) in rfcToBe.subseries" :key="idx">
                  {{ sub.displayName }}<span v-if="idx < rfcToBe.subseries.length - 1">, </span>
                </span>
              </span>
              <span v-else>
                (none)
              </span>
            </div>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Disposition" :spacing="spacing">
          <DescriptionListDetails>
            <PatchRfcToBeField
              key="disposition"
              :is-read-only="props.isReadOnly"
              :ui-mode="{ type: 'select', options: dispositionOptions }"
              :draft-name="rfcToBe.name ?? ''"
              :initial-value="rfcToBe.disposition"
              :on-success="() => props.refresh?.()"
            >
              {{ rfcToBe.disposition }}
            </PatchRfcToBeField>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="RFC Number" :spacing="spacing">
          <DescriptionListDetails>
            <PatchRfcToBeField
              key="rfcNumber"
              :is-read-only="props.isReadOnly"
              :ui-mode="{ type: 'textbox', isNumber: true, rows: 1, placeholder: 'RFC #' }"
              :draft-name="rfcToBe.name ?? ''"
              :initial-value="rfcToBe.rfcNumber?.toString()"
              :on-success="() => props.refresh?.()"
            >
              <div class="font-mono">
                {{ rfcToBe.rfcNumber || '(none)' }}
              </div>
            </PatchRfcToBeField>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Consensus" :spacing="spacing">
          <DescriptionListDetails>
            <PatchRfcToBeField
              key="consensus"
              :is-read-only="props.isReadOnly"
              :ui-mode="{ type: 'checkbox', label: 'Consensus' }"
              :draft-name="rfcToBe.name ?? ''"
              :initial-value="rfcToBe.consensus"
              :on-success="() => props.refresh?.()"
            >
              <span v-if="rfcToBe.consensus === true" class="text-green-600">
                Yes
              </span>
              <span v-else-if="rfcToBe.consensus === false" class="text-red-600">
                No
              </span>
              <span v-else class="text-gray-500">
                Unknown
              </span>
            </PatchRfcToBeField>
          </DescriptionListDetails>
        </DescriptionListItem>
      </DescriptionList>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { type RfcToBe } from '~/purple_client'
import EditSubseries from './EditSubseries.vue'

type Props = {
  rfcToBe: RfcToBe | null | undefined
  draftName: string
  isReadOnly?: boolean
  refresh?: () => void
}

const props = defineProps<Props>()
const emit = defineEmits<{
  update: [rfcToBe: RfcToBe]
  refresh: []
}>()

const api = useApi()

const loadStreams = async (): Promise<SelectOption[]> => {
  const streamNames = await api.streamNamesList()
  return streamNames
    .filter(streamName => streamName.used)
    .map(streamName => {
      return {
        value: streamName.slug,
        label: streamName.name
      }
    })
}

const loadFormats = async (): Promise<SelectOption[]> => {
  const formatNames = await api.sourceFormatNamesList()
  return formatNames
    .filter(formatName => formatName.used)
    .map(formatName => {
      return {
        value: formatName.slug,
        label: formatName.name
      }
    })
}

const loadBoilerplates = async (): Promise<SelectOption[]> => {
  const boilerplates = await api.tlpBoilerplateChoiceNamesList()
  return boilerplates
    .filter(boilerplate => boilerplate.used)
    .map(boilerplate => {
      return {
        value: boilerplate.slug,
        label: boilerplate.name
      }
    })
}

const loadStandardLevels = async (): Promise<SelectOption[]> => {
  const standardLevels = await api.stdLevelNamesList()
  return standardLevels
    .filter(standardLevel => standardLevel.used)
    .map(standardLevel => {
      return {
        value: standardLevel.slug,
        label: standardLevel.name
      }
    })
}

const dispositionOptions = computed((): SelectOption[] => {
  return dispositionValues
    .filter(dispositionValue => typeof dispositionValue === 'string')
    .map(dispositionValue => {
      return {
        value: dispositionValue,
        label: dispositionValue
      }
    })
})

const spacing = computed(() => props.isReadOnly ? 'small' : 'large')
</script>
