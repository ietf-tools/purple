<!--
History feed component
Based on https://tailwindui.com/components/application-ui/lists/feeds#component-81e5ec57a92ddcadaa913e7bb68336fe
-->
<template>
  <ul role="list" class="space-y-6">
    <li
      class="bg-red-700 text-red-100 p-2 flex flex-row rounded-md"
      role="alert"
    >
      <h1
        aria-atomic="true"
        aria-live="polite"
        class="flex flex-col justify-center flex-1"
      >
        {{ props.error?.message }}
      </h1>
      <button
        @click="props.reloadComments()"
        class="border ml-3 border-gray-200 px-2 py-1"
      >
        Try again
      </button>
    </li>
    <li v-if="props.isLoading">
      <Icon name="ei:spinner-3" size="3.5em" class="animate-spin" />
    </li>
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
        :src="comment.avatar"
        alt=""
        class="relative mt-3 h-6 w-6 flex-none rounded-full bg-gray-50"
      />
      <div class="flex-auto rounded-md p-3 ring-1 ring-inset ring-gray-200">
        <div class="flex justify-between gap-x-4">
          <div class="py-0.5 text-xs leading-5 text-gray-500">
            <span
              class="font-medium text-gray-900"
              :title="`User #${comment.by.rpcperson}`"
            >
              {{ comment.by.plain_name }}
            </span>
            commented
          </div>
          <time
            :datetime="comment.time"
            class="flex-none py-0.5 text-xs leading-5 text-gray-500"
          >
            {{ comment.ago }}
          </time>
        </div>
        <p class="text-sm leading-6 text-gray-500">
          {{ comment.comment }}
        </p>
      </div>
    </li>
  </ul>
</template>

<script setup lang="ts">
import { DateTime } from 'luxon'
import type { NuxtError } from '#app'

// TODO: replace with proper types when this is merged https://github.com/ietf-tools/purple/pull/337
type Comment = {
  id: number
  comment: string
  by: {
    plain_name: string
    rpcperson: number
  }
  time: string
  last_edit?: {
    plain_name: string
    edit_time: string
  }
}

type Props = {
  id: string
  isLoading: boolean
  error?: NuxtError
  comments?: Comment[]
  reloadComments: () => void
}

const props = defineProps<Props>()

const cookedComments = computed(() => {
  return (
    props.comments?.map((comment) => ({
      ...comment,
      ago: DateTime.fromISO(comment.time).toRelative()
    })) ?? []
  )
})
</script>
