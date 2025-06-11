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
        <span class="mr-1"> Problem loading comments: </span>
        <span v-if="props.error?.statusCode" class="mx-1">
          (HTTP {{ props.error?.statusCode }})
        </span>
        {{ props.error?.message }}
      </h1>
      <button
        @click="props.reloadComments"
        class="border ml-3 border-gray-200 px-2 py-1"
      >
        Try again
      </button>
    </div>
    <div v-if="props.isLoading">
      <Icon name="ei:spinner-3" size="3.5em" class="animate-spin" />
    </div>
    <div v-if="props.comments?.count === 0" class="flex flex-row">
      <p class="italic">(no comments yet)</p>
      <button
        @click="props.reloadComments"
        class="border ml-3 border-gray-200 px-2 py-1"
      >
        (check again)
      </button>
    </div>
    <ul role="list" class="space-y-6">
      <li
        v-for="(comment, commentIndex) in cookedComments"
        :key="comment.id"
        class="relative flex gap-x-4"
      >
        <div
          :class="[
            commentIndex === cookedComments.length - 1 ? 'h-6' : '-bottom-6',
            'absolute left-0 top-0 flex w-6 justify-center'
          ]"
        >
          <div class="w-px bg-gray-200" />
        </div>
        <img
          v-if="comment.by?.avatar"
          :src="comment.by.avatar"
          alt=""
          class="relative mt-3 h-6 w-6 flex-none rounded-full bg-gray-50"
        />
        <div class="flex-auto rounded-md p-3 ring-1 ring-inset ring-gray-200">
          <div class="flex justify-between gap-x-4">
            <div v-if="comment.by" class="py-0.5 text-xs leading-5 text-gray-500">
              <span
                class="font-medium text-gray-900"
                :title="`User #${comment.by.rpcperson}`"
              >
                {{ comment.by.name }}
              </span>
              commented
            </div>
            <time
              v-if="comment.time"
              :datetime="comment.time.toISOString()"
              class="flex-none py-0.5 text-xs leading-5 text-gray-500"
            >
              {{ comment.ago }}
            </time>
          </div>
          <p v-if="comment.comment" class="text-sm leading-6 text-gray-500">
            {{ comment.comment }}
          </p>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { DateTime } from 'luxon'
import type { NuxtError } from '#app'
import type { PaginatedDocumentCommentList } from '~/purple_client'

type Props = {
  isLoading: boolean
  error?: NuxtError | null
  comments?: PaginatedDocumentCommentList | null
  reloadComments: () => void
}

const props = defineProps<Props>()

const cookedComments = computed(() => {
  return (
    props.comments?.results?.map((comment) => ({
      ...comment,
      ago: comment.time ? DateTime.fromJSDate(comment.time).toRelative() : undefined
    })) ?? []
  )
})
</script>
