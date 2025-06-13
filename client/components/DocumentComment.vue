<!--
History feed component
Based on https://tailwindui.com/components/application-ui/lists/feeds#component-81e5ec57a92ddcadaa913e7bb68336fe
-->
<template>
  <div
    :class="[
      props.isLastComment ? 'h-6' : '-bottom-6',
      'absolute left-0 top-0 flex w-6 justify-center'
    ]"
  >
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
          :title="comment.by.rpcperson ? `${comment.by.name} (user #${comment.by.rpcperson})` : undefined"
        >
          {{ comment.by.name }}
        </span>
        commented
        <time
          v-if="comment.time"
          :datetime="comment.time.toISOString()"
          class="text-gray-500"
        >
          {{ comment.ago }}
        </time>
        <span v-if="comment.lastEdit && comment.lastEdit.by">
          (last edited
          <span>
            by
            <span
              v-if="comment.lastEdit.by.personId !== comment.by?.rpcperson"
              class="font-medium text-gray-900"
              :title="comment.lastEdit.by.personId ? `${comment.lastEdit.by.name} (user #${comment.lastEdit.by.personId})` : undefined"
            >
              {{ comment.lastEdit.by.name }} {{ ' ' }}
            </span>
          </span>
          <time
            v-if="comment.lastEdit.date"
            :datetime="comment.lastEdit.date.toISOString()"
            class="text-gray-500"
          >
            {{ comment.lastEditAgo }}
          </time>)
        </span>
      </div>
      <div class="flex-none py-0.5 text-xs leading-5">
        <button type="button" aria-label="Edit" class="border-0 ml-2" v-show="!isEditing" @click="handleEdit">
          <Icon name="circum:edit" class="w-5 h-5 no-underline text-gray-600 hover:text-indigo-900 cursor-pointer" />
        </button>
      </div>
    </div>
    <p v-if="!isEditing" class="text-sm leading-6 text-gray-500">
      {{ comment.comment }}
    </p>
    <div v-else>
      <textarea
        v-model="editComment"
        rows="3"
        name="comment"
        class="block w-full resize-none border-1 bg-transparent  text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6"
        placeholder="Edit comment..."
      />
      <div class="flex justify-between pt-1">
        <BaseButton btn-type="cancel" @click="isEditing = false" :disabled="isUpdating">Cancel</BaseButton>
        <BaseButton btn-type="default" @click="handleUpdateComment" :disabled="isUpdating">
          <Icon v-show="isUpdating" name="ei:spinner-3" size="1.5em" class="animate-spin" />
          Update comment
        </BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PaginatedDocumentCommentList } from '~/purple_client'
import { snackbarForErrors } from '~/utilities/snackbar'

type Props = {
  draftName: string
  rfcToBeId: number
  comment: PaginatedDocumentCommentList["results"][number] & {
    // added by parent component
    ago?: string | null
    lastEditAgo?: string | null
  }
  isLastComment: boolean,
  reloadComments: () => Promise<void>
}

const props = defineProps<Props>()

const isEditing = ref(false)
const isUpdating = ref(false)

const editComment = ref(props.comment.comment)

watch(props.comment, (newValue, oldValue) => {
  if(newValue.comment !== oldValue.comment) {
    // then a new comment has been saved and we're receiving the props,
    // so clobber the editComment ref with the current value
    editComment.value = newValue.comment
  }
})

const handleEdit = () => {
  isEditing.value = true
}

const snackbar = useSnackbar()

const api = useApi()

const handleUpdateComment = async () => {
  isUpdating.value = true
  try {
    await api.documentsCommentsUpdate({
      draftName: props.draftName,
      id: props.comment.id!,
      documentComment: {
        comment: editComment.value
      }
    })
    isEditing.value = false
    snackbar.add({
      type: 'success',
      title: 'Comment updated successfully',
      text: ''
    })
    await props.reloadComments()
  } catch(error: unknown) {
    snackbarForErrors({ snackbar, error, defaultTitle: "Problem updating comment" })
  }
  isUpdating.value = false
}

</script>
