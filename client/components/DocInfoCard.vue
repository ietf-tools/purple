<template>
  <BaseCard>
    <template #header>
      <CardHeader title="Document Info" />
    </template>
    <div v-if="draft">
      <DescriptionList>
        <DescriptionListItem term="Title" :details="draft.title" />
        <DescriptionListItem term="Authors">
          <DescriptionListDetails>
            <div class="mx-4 text-sm font-medium">
              <div v-if="draft.authors.length === 0">None</div>
              <div v-else>
                <div
                  v-for="author of draft.authors"
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
          :details="draft.pages?.toString()"
        />
        <DescriptionListItem
          term="Document Shepherd"
          details="Dolly Shepherd (mocked)"
        />
        <DescriptionListItem term="Stream">
          <DescriptionListDetails>
            {{ draft.stream }}
            <span v-if="draft.submittedStream !== draft.stream">
              (submitted as {{ draft.submittedStream }})
            </span>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem
          term="Stream Manager"
          details="Ari Drecker (mocked)"
        />
        <DescriptionListItem
          term="Submitted Format"
          :details="draft.submittedFormat"
        />
        <DescriptionListItem term="Submitted Boilerplate">
          <DescriptionListDetails
            >{{ draft.intendedBoilerplate }}
            <span
              v-if="draft.submittedBoilerplate !== draft.intendedBoilerplate"
            >
              (submitted as {{ draft.submittedBoilerplate }})
            </span>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Standard Level">
          <DescriptionListDetails>
            {{ draft.intendedStdLevel }}
            <span v-if="draft.submittedStdLevel !== draft.intendedStdLevel">
              (submitted as {{ draft.submittedStdLevel }})
            </span>
          </DescriptionListDetails>
        </DescriptionListItem>
        <DescriptionListItem term="Disposition" :details="draft.disposition" />
      </DescriptionList>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import type { RfcToBe } from '~/purple_client'

type Props = {
  draft: RfcToBe | null
}

defineProps<Props>()
</script>
