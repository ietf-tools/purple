<template>
  <BaseCard>
    <template #header>
      <CardHeader title="Document Info" />
    </template>
    <div v-if="rfcToBe">
      <DescriptionList>
        <DescriptionListItem term="Title" :details="rfcToBe.title" :spacing="spacing" />
        <DescriptionListItem term="Authors" :spacing="spacing">
          <DescriptionListDetails>
            <div class="mx-0 text-sm font-medium">
              <div v-if="rfcToBe.authors.length === 0">None</div>
              <div v-else>
                <div v-for="author of rfcToBe.authors" :key="author.id" class="py-1">
                  <a :href="author.email ? datatrackerLinks.personByEmail(author.email) : undefined" :class="ANCHOR_STYLE">
                    <span :class="ANCHOR_STYLE">{{ author.titlepageName }}</span>
                    <span :class="PERSON_ID_STYLE" v-if="author.email">{{ SPACE }}{{ ` (${author.email})` }}</span>
                    <span v-if="author.isEditor">(editor)</span>
                  </a>
                  <div class="text-xs text-gray-500" v-if="author.affiliation">
                    {{ author.affiliation }}
                  </div>
                </div>
              </div>
            </div>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Submitted Pages" :details="rfcToBe.draft?.pages?.toString()" :spacing="spacing" />
        <DescriptionListItem term="Document Shepherd" details="Dolly Shepherd (mocked)" :spacing="spacing" />
        <DescriptionListItem term="Stream" :spacing="spacing">
          <DescriptionListDetails>
            {{ rfcToBe.intendedStream }}
            <span v-if="rfcToBe.submittedStream !== rfcToBe.intendedStream">
              (submitted as {{ rfcToBe.submittedStream }})
            </span>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Stream Manager" details="Ari Drecker (mocked)" :spacing="spacing" />
        <DescriptionListItem term="Submitted Format" :details="rfcToBe.submittedFormat" :spacing="spacing" />
        <DescriptionListItem term="Submitted Boilerplate" :spacing="spacing">
          <DescriptionListDetails>{{ rfcToBe.intendedBoilerplate }}
            <span v-if="rfcToBe.submittedBoilerplate !== rfcToBe.intendedBoilerplate">
              (submitted as {{ rfcToBe.submittedBoilerplate }})
            </span>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Standard Level" :spacing="spacing">
          <DescriptionListDetails>
            {{ rfcToBe.intendedStdLevel }}
            <span v-if="rfcToBe.submittedStdLevel !== rfcToBe.intendedStdLevel">
              (submitted as {{ rfcToBe.submittedStdLevel }})
            </span>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Subseries" :spacing="spacing">
          <DescriptionListDetails>
            <div>
              <div v-if="!props.isReadOnly && rfcToBe.disposition !== 'published'">
                <template v-if="rfcToBe.subseries && rfcToBe.subseries.length > 0">
                  <div v-for="(sub, idx) in rfcToBe.subseries" :key="idx">
                    <EditSubseries
                      :id="rfcToBe.id"
                      :initial-subseries="sub"
                      :on-success="() => props.refresh?.()"
                    />
                  </div>
                </template>
                <template v-else>
                  <EditSubseries
                    :id="rfcToBe.id"
                    :initial-subseries="null"
                    :on-success="() => props.refresh?.()"
                  />
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
            </div>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Disposition" :details="rfcToBe.disposition" :spacing="spacing" />
        <DescriptionListItem term="RFC Number" :spacing="spacing">
          <DescriptionListDetails>
            <div v-if="!props.isReadOnly &&
              // published RFCs can't be edited
              rfcToBe.disposition !== 'published'" class="flex items-center gap-2">
              <EditRfcNumber :name="rfcToBe.name" :initial-rfc-number="rfcToBe.rfcNumber"
                :on-success="() => props.refresh?.()" />
            </div>
            <div v-else class="font-mono">
              {{ rfcToBe.rfcNumber || '(none)' }}
            </div>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Consensus" :spacing="spacing">
          <DescriptionListDetails>
            <span v-if="rfcToBe.consensus === true" class="text-green-600">
              Yes
            </span>
            <span v-else-if="rfcToBe.consensus === false" class="text-red-600">
              No
            </span>
            <span v-else class="text-gray-500">
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
import EditSubseries from './EditSubseries.vue'
import { useDatatrackerLinks } from '~/composables/useDatatrackerLinks'

const datatrackerLinks = useDatatrackerLinks()

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

const spacing = computed(() => props.isReadOnly ? 'small' : 'large')
</script>
