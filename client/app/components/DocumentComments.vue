<!--
History feed component
Based on https://tailwindui.com/components/application-ui/lists/feeds#component-81e5ec57a92ddcadaa913e7bb68336fe
-->
<template>
  <div>
    <div
      v-if="props.error"
      class="bg-red-700 text-red-100 p-2 flex flex-row rounded-md"
      role="alert"
    >
      <h1
        aria-atomic="true"
        aria-live="polite"
        class="flex items-center flex-1 px-2"
      >
        <span>
          <span class="mr-1"> Problem loading comments: </span>
          <span v-if="props.error?.statusCode" class="mx-1">
            (HTTP {{ props.error?.statusCode }})
          </span>
          {{ props.error?.message }}
        </span>
      </h1>
      <button
        @click="props.reloadComments"
        class="border ml-3 border-gray-200 px-2 py-1"
      >
        Try again
      </button>
    </div>
    <div v-if="props.isLoading" class="text-center">
      <Icon name="ei:spinner-3" size="3.5em" class="animate-spin mb-3" />
    </div>
    <div v-if="props.commentList?.count === 0" class="text-center text-sm mt-4 mb-2">
      <p class="italic text-gray-500">no comments</p>

    </div>
    <ul role="list" class="space-y-6">
      <li
        v-for="(comment, commentIndex) in cookedComments"
        :key="comment.id"
        class="relative flex gap-x-4"
      >
        <DocumentComment
          :draft-name="props.draftName"
          :rfc-to-be-id="props.rfcToBeId"
          :comment="comment"
          :is-last-comment="commentIndex === cookedComments.length"
          :reload-comments="reloadComments"
        />
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { DateTime } from 'luxon'
import type { NuxtError } from '#app'
import type { PaginatedDocumentCommentList } from '~/purple_client'

type Props = {
  draftName: string
  rfcToBeId: number
  isLoading: boolean
  error?: NuxtError | null
  commentList?: PaginatedDocumentCommentList | null | undefined
  reloadComments: () => Promise<void>
}

const props = defineProps<Props>()

const cookedComments = computed(() => {
  return (
    props.commentList?.results?.map((comment) => ({
      ...comment,
      ago: comment.time ? DateTime.fromJSDate(comment.time).toRelative() : undefined,
      lastEditAgo: comment.lastEdit?.time ? DateTime.fromJSDate(comment.lastEdit.time).toRelative() : undefined
    })) ?? []
  )
})
</script>
