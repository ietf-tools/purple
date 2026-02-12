<template>
  <BaseCard>
    <template #header>
      <CardHeader :title="`Document Info${props.isReadOnly ? ' (read only)' : ''}`" />
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
              <div v-if="!props.isReadOnly">
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
              <span class="flex-1">{{ rfcToBe.shepherd?.name || '(none)' }}</span>
            </div>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="IESG Contact" :spacing="spacing">
          <DescriptionListDetails>
            <div class="flex flex-row items-center h-full mx-0 text-sm font-medium">
              <span class="flex-1">{{ rfcToBe.iesgContact?.name || '(none)' }}</span>
            </div>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Group" :spacing="spacing">
          <DescriptionListDetails>
            <PatchRfcToBeField fieldName="group" :is-read-only="props.isReadOnly"
              :ui-mode="{ type: 'textbox', rows: 1, placeholder: 'Group Acronym', initialValue: rfcToBe.group }"
              :draft-name="rfcToBe.name ?? ''" :on-success="props.refresh">
              <div class="font-mono">
                {{ rfcToBe.group || '(none)' }}
              </div>
            </PatchRfcToBeField>
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
        <DescriptionListItem term="Additional Emails" :spacing="spacing">
          <DescriptionListDetails>
            <div v-if="!isEditingAdditionalEmails"
              class="w-full flex flex-row items-center h-full mx-0 text-sm font-medium">
              <div v-if="additionalEmails && additionalEmails.length > 0" class="w-full">
                <div v-for="email in additionalEmails" :key="email.id">
                  {{ email.email }}
                </div>
              </div>
              <div v-else class="flex-1 text-gray-500">(none)</div>
              <div v-if="!props.isReadOnly">
                <button @click="isEditingAdditionalEmails = true" :class="[classForBtnType.outline, 'px-2 py-1']">
                  <Icon name="uil:pen" />
                </button>
              </div>
            </div>
            <div v-else class="w-full flex flex-col gap-2">
              <div v-if="additionalEmails && additionalEmails.length > 0" class="space-y-1">
                <div v-for="email in additionalEmails" :key="email.id"
                  class="flex items-center justify-between text-sm">
                  <span>{{ email.email }}</span>
                  <button v-if="email.id" @click="removeEmail(email.id)" class="text-red-600 hover:text-red-800 px-2 py-1">
                    <Icon name="uil:trash" />
                  </button>
                </div>
              </div>
              <div v-else class="text-sm text-gray-500">(none)</div>
              <div class="flex gap-2">
                <input v-model="newEmail" type="email" placeholder="email@example.com"
                  class="flex-1 px-3 py-1 text-sm border rounded" ref="newEmailInput" @keyup.enter="addEmail" />
                <button @click="addEmail" :disabled="!newEmail"
                  class="px-3 py-1 text-sm bg-blue-600 text-white rounded disabled:bg-gray-300">
                  Add
                </button>
              </div>
              <div class="flex justify-end">
                <button @click="isEditingAdditionalEmails = false"
                  class="text-xs text-gray-500 hover:text-gray-700 underline">
                  Done
                </button>
              </div>
            </div>
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
        <DescriptionListItem term="Obsoletes" :spacing="spacing">
          <DescriptionListDetails>
            <div v-if="obsoletes && obsoletes.length > 0" class="text-sm font-medium">
              <span v-for="(doc, idx) in obsoletes" :key="doc.id">
                <NuxtLink :to="`/docs/${doc.targetDraftName}`" class="text-blue-600 hover:underline">
                  RFC {{ doc.targetRfcNumber }}
                </NuxtLink><span v-if="idx < obsoletes.length - 1">, </span>
              </span>
            </div>
            <div v-else class="text-sm text-gray-500">(none)</div>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Updates" :spacing="spacing">
          <DescriptionListDetails>
            <div v-if="updates && updates.length > 0" class="text-sm font-medium">
              <span v-for="(doc, idx) in updates" :key="doc.id">
                <NuxtLink :to="`/docs/${doc.targetDraftName}`" class="text-blue-600 hover:underline">
                  RFC {{ doc.targetRfcNumber }}
                </NuxtLink><span v-if="idx < updates.length - 1">, </span>
              </span>
            </div>
            <div v-else class="text-sm text-gray-500">(none)</div>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Obsoleted By" :spacing="spacing">
          <DescriptionListDetails>
            <div v-if="obsoletedBy && obsoletedBy.length > 0" class="text-sm font-medium">
              <span v-for="(doc, idx) in obsoletedBy" :key="doc.id">
                <NuxtLink :to="`/docs/${doc.draftName}`" class="text-blue-600 hover:underline">
                  RFC {{ doc.sourceRfcNumber }}
                </NuxtLink><span v-if="idx < obsoletedBy.length - 1">, </span>
              </span>
            </div>
            <div v-else class="text-sm text-gray-500">(none)</div>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Updated By" :spacing="spacing">
          <DescriptionListDetails>
            <div v-if="updatedBy && updatedBy.length > 0" class="text-sm font-medium">
              <span v-for="(doc, idx) in updatedBy" :key="doc.id">
                <NuxtLink :to="`/docs/${doc.draftName}`" class="text-blue-600 hover:underline">
                  RFC {{ doc.sourceRfcNumber }}
                </NuxtLink><span v-if="idx < updatedBy.length - 1">, </span>
              </span>
            </div>
            <div v-else class="text-sm text-gray-500">(none)</div>
          </DescriptionListDetails>
        </DescriptionListItem>
      </DescriptionList>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { type RfcToBe, ResponseError } from '~/purple_client'
import EditSubseries from './EditSubseries.vue'
import { useDatatrackerLinks } from '~/composables/useDatatrackerLinks'
import { draftAssignmentsHref } from '~/utils/url'
import { classForBtnType } from '~/utils/button'
import type { SelectOption } from '~/utils/html'
import { dispositionValues } from '~/utils/document_relations-utils'

const datatrackerLinks = useDatatrackerLinks()
const snackbar = useSnackbar()

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

const { data: additionalEmails, refresh: refreshEmails } = await useAsyncData(
  () => `additional-emails-${props.draftName}`,
  () => props.draftName ? api.documentsAdditionalEmailsList({ draftName: props.draftName }) : Promise.resolve([]),
  { server: false, lazy: true, default: () => [] }
)

const isEditingAdditionalEmails = ref(false)
const newEmailInput = ref<HTMLInputElement | null>(null)

watch(isEditingAdditionalEmails, async (newValue) => {
  if (newValue) {
    await nextTick()
    newEmailInput.value?.focus()
  }
})

const newEmail = ref('')

const addEmail = async () => {
  if (!newEmail.value || !props.draftName) return
  try {
    await api.documentsAdditionalEmailsCreate({
      draftName: props.draftName,
      additionalEmailRequest: { email: newEmail.value }
    })
    newEmail.value = ''
    await refreshEmails()
    await props.refresh?.()
  } catch (error) {
    let msg = 'Failed to add email.'
    if (error instanceof ResponseError) {
      const data = await error.response.json()
      if (data?.email) {
        msg = data.email[0]
      }
    }
    snackbar.add({
      type: 'error',
      text: msg
    })
    console.error('Failed to add email:', error)
  }
}

const removeEmail = async (id: number) => {
  if (!props.draftName) return
  try {
    await api.documentsAdditionalEmailsDestroy({ draftName: props.draftName, id })
    await refreshEmails()
    await props.refresh?.()
  } catch (error) {
    console.error('Failed to remove email:', error)
  }
}

const { data: obsoletes } = await useAsyncData(
  () => `obsoletes-${props.draftName}`,
  () => props.draftName ? api.documentsReferencesList({ draftName: props.draftName, relationshipSlug: 'obs' }) : Promise.resolve([]),
  { server: false, lazy: true, default: () => [] }
)

const { data: updates } = await useAsyncData(
  () => `updates-${props.draftName}`,
  () => props.draftName ? api.documentsReferencesList({ draftName: props.draftName, relationshipSlug: 'updates' }) : Promise.resolve([]),
  { server: false, lazy: true, default: () => [] }
)

const { data: obsoletedBy } = await useAsyncData(
  () => `obsoletedBy-${props.draftName}`,
  () => props.draftName ? api.documentsReferencesObsoletedByList({ draftName: props.draftName }) : Promise.resolve([]),
  { server: false, lazy: true, default: () => [] }
)

const { data: updatedBy } = await useAsyncData(
  () => `updatedBy-${props.draftName}`,
  () => props.draftName ? api.documentsReferencesUpdatedByList({ draftName: props.draftName }) : Promise.resolve([]),
  { server: false, lazy: true, default: () => [] }
)

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
