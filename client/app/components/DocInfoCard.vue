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
            <div class="mx-4 text-sm font-medium">
              <div v-if="rfcToBe.authors.length === 0">None</div>
              <div v-else>
                <div
                  v-for="author of rfcToBe.authors"
                  :key="author.id"
                  class="py-1 grid grid-cols-2"
                >
                  <div>
                    {{ author.titlepageName }}
                    <span v-if="author.isEditor">(editor)</span>
                  </div>
                </div>
              </div>
            </div>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem
          term="Submitted Pages"
          :details="rfcToBe.draft.pages?.toString()"
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
        <DescriptionListItem term="Consensus">
          <DescriptionListDetails>
            <span
              v-if="rfcToBe.consensus === true"
              class="text-green-600 font-medium"
            >
              YES
            </span>
            <span
              v-else-if="rfcToBe.consensus === false"
              class="text-red-600 font-medium"
            >
              NO
            </span>
            <span
              v-else
              class="text-gray-500 font-medium"
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
}

defineProps<Props>()
</script>
