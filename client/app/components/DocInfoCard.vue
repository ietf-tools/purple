<template>
  <BaseCard>
    <template #header>
      <CardHeader title="Document Info" />
    </template>
    <div v-if="rfcToBe">
      <DescriptionList>
        <DescriptionListItem term="Title" :spacing="spacing">
          <DescriptionListDetails>
            <PatchRfcToBeField fieldName="title" :is-read-only="props.isReadOnly"
              :ui-mode="{ type: 'textbox', placeholder: 'title', rows: 5, initialValue: rfcToBe.title }"
              :draft-name="rfcToBe.name!" :on-success="props.refresh">
              {{ rfcToBe.title }}
            </PatchRfcToBeField>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Authors" :spacing="spacing">
          <DescriptionListDetails>
            <div class="w-full flex flex-row items-center h-full mx-0 text-sm font-medium">
              <div v-if="rfcToBe.authors.length === 0">None</div>
              <div v-else class="w-full">
                <div v-for="author of rfcToBe.authors" :key="author.id" class="py-1">
                  <a :href="author.email ? datatrackerLinks.personByEmail(author.email) : undefined"
                    :class="ANCHOR_STYLE">
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
                <Anchor :href="draftAssignmentsHref(props.rfcToBe?.name, 'edit-authors')"
                  :class="[classForBtnType.outline, 'px-2 py-1']">
                  <Icon name="uil:pen" />
                </Anchor>
              </div>
            </div>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Submitted Pages" :spacing="spacing">
          <DescriptionListDetails>
            <PatchRfcToBeField fieldName="pages" :is-read-only="props.isReadOnly"
              :ui-mode="{ type: 'textbox', placeholder: 'title', isNumber: true, rows: 1, initialValue: rfcToBe.draft?.pages?.toString() }"
              :draft-name="rfcToBe.name ?? ''" :on-success="props.refresh">
              {{ rfcToBe.draft?.pages?.toString() }}
            </PatchRfcToBeField>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Document Shepherd" :spacing="spacing">
          <DescriptionListDetails>
            <div class="flex flex-row items-center h-full mx-0 text-sm font-medium">
              <span class="flex-1">Dolly Shepherd (mocked)</span>
              <span v-if="!props.isReadOnly">
                <TooltipProvider>
                  <TooltipRoot>
                    <TooltipTrigger class="hover:bg-stone-50 inline-flex focus:shadow-black">
                      <span :class="[classForBtnType.outline, 'px-2 py-1 text-xs opacity-50']">
                        <Icon name="fe:disabled" />
                      </span>
                    </TooltipTrigger>
                    <TooltipPortal>
                      <TooltipContent
                        class="data-[state=delayed-open]:data-[side=top]:animate-slideDownAndFade data-[state=delayed-open]:data-[side=right]:animate-slideLeftAndFade data-[state=delayed-open]:data-[side=left]:animate-slideRightAndFade data-[state=delayed-open]:data-[side=bottom]:animate-slideUpAndFade text-grass11 select-none rounded-md bg-white px-[15px] py-[10px] text-sm leading-none shadow-sm border will-change-[transform,opacity]"
                        :side-offset="5">
                        Edit on Datatracker
                        <TooltipArrow class="fill-white stroke-gray-200" :width="12" :height="6" />
                      </TooltipContent>
                    </TooltipPortal>
                  </TooltipRoot>
                </TooltipProvider>
              </span>
            </div>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Stream" :spacing="spacing">
          <DescriptionListDetails>
            <PatchRfcToBeField fieldName="stream" :is-read-only="props.isReadOnly"
              :ui-mode="{ type: 'select', options: loadStreams, initialValue: rfcToBe.stream }"
              :draft-name="rfcToBe.name ?? ''" :on-success="props.refresh">
              <span class="flex-1">
                {{ rfcToBe.stream }}
                <span v-if="rfcToBe.publicationStream && rfcToBe.publicationStream !== rfcToBe.stream">
                  (published as {{ rfcToBe.publicationStream }})
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
                <Anchor :href="draftAssignmentsHref(props.rfcToBe?.name, 'edit-stream-manger')"
                  :class="[classForBtnType.outline, 'px-2 py-1']">
                  <Icon name="uil:pen" />
                </Anchor>
              </span>
            </div>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Submitted Format" :spacing="spacing">
          <DescriptionListDetails>
            <PatchRfcToBeField fieldName="submittedFormat" :is-read-only="props.isReadOnly"
              :ui-mode="{ type: 'select', options: loadFormats, initialValue: rfcToBe.submittedFormat }"
              :draft-name="rfcToBe.name ?? ''" :on-success="props.refresh">
              {{ rfcToBe.submittedFormat }}
            </PatchRfcToBeField>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Boilerplate" :spacing="spacing">
          <DescriptionListDetails>
            <PatchRfcToBeField fieldName="boilerplate" :is-read-only="props.isReadOnly"
              :ui-mode="{ type: 'select', options: loadBoilerplates, initialValue: rfcToBe.submittedFormat }"
              :draft-name="rfcToBe.name ?? ''" :on-success="props.refresh">
              {{ rfcToBe.boilerplate }}
            </PatchRfcToBeField>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Standard Level" :spacing="spacing">
          <DescriptionListDetails>
            <PatchRfcToBeField fieldName="stdLevel" :is-read-only="props.isReadOnly"
              :ui-mode="{ type: 'select', options: loadStandardLevels, initialValue: rfcToBe.stdLevel }"
              :draft-name="rfcToBe.name ?? ''" :on-success="props.refresh">
              {{ rfcToBe.stdLevel }}
              <span v-if="rfcToBe.publicationStdLevel && rfcToBe.publicationStdLevel !== rfcToBe.stdLevel">
                (submitted as {{ rfcToBe.publicationStdLevel }})
              </span>
            </PatchRfcToBeField>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Subseries" :spacing="spacing">
          <DescriptionListDetails>
            <div v-if="!props.isReadOnly && rfcToBe.disposition !== 'published'">
              <template v-if="rfcToBe.subseries && rfcToBe.subseries.length > 0">
                <div v-for="(sub, idx) in rfcToBe.subseries" :key="idx">
                  <EditSubseries :id="rfcToBe.id" :initial-subseries="sub" :on-success="() => props.refresh?.()">
                    {{ sub.displayName }}<span v-if="idx < rfcToBe.subseries.length - 1">, </span>
                  </EditSubseries>
                </div>
              </template>
              <template v-else>
                <EditSubseries :id="rfcToBe.id" :initial-subseries="null" :on-success="() => props.refresh?.()">
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
            <PatchRfcToBeField fieldName="disposition" :is-read-only="props.isReadOnly"
              :ui-mode="{ type: 'select', options: dispositionOptions, initialValue: rfcToBe.disposition }"
              :draft-name="rfcToBe.name ?? ''" :on-success="props.refresh">
              {{ rfcToBe.disposition }}
            </PatchRfcToBeField>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="RFC Number" :spacing="spacing">
          <DescriptionListDetails>
            <PatchRfcToBeField fieldName="rfcNumber" :is-read-only="props.isReadOnly"
              :ui-mode="{ type: 'textbox', isNumber: true, rows: 1, placeholder: 'RFC #', initialValue: rfcToBe.rfcNumber?.toString() }"
              :draft-name="rfcToBe.name ?? ''" :on-success="props.refresh">
              <div class="font-mono">
                {{ rfcToBe.rfcNumber || '(none)' }}
              </div>
            </PatchRfcToBeField>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Consensus" :spacing="spacing">
          <DescriptionListDetails>
            <PatchRfcToBeField fieldName="consensus" :is-read-only="props.isReadOnly"
              :ui-mode="{ type: 'checkbox', label: 'consensus?', initialValue: rfcToBe.consensus ?? false }"
              :draft-name="rfcToBe.name ?? ''" :on-success="props.refresh">
              <div class="w-full flex justify-between">
                <div>
                  <span v-if="rfcToBe.consensus === true" class="text-green-600">
                    Yes
                  </span>
                  <span v-else-if="rfcToBe.consensus === false" class="text-red-600">
                    No
                  </span>
                  <span v-else>
                    Unknown
                  </span>
                </div>
              </div>
            </PatchRfcToBeField>
          </DescriptionListDetails>
        </DescriptionListItem>
      </DescriptionList>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { TooltipArrow, TooltipContent, TooltipPortal, TooltipProvider, TooltipRoot, TooltipTrigger } from 'reka-ui'
import { type RfcToBe } from '~/purple_client'
import EditSubseries from './EditSubseries.vue'
import { useDatatrackerLinks } from '~/composables/useDatatrackerLinks'
import { draftAssignmentsHref } from '~/utils/url'
import { classForBtnType } from '~/utils/button'
import type { SelectOption } from '~/utils/html'
import { dispositionValues } from '~/utils/document_relations-utils'

const datatrackerLinks = useDatatrackerLinks()

type Props = {
  rfcToBe: RfcToBe | null | undefined
  draftName: string
  isReadOnly?: boolean
  refresh?: () => Promise<void>
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
