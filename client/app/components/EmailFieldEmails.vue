<template>
  <div class="flex flex-row items-start">
    <div class="w-[6em] inline font-bold pt-4">{{ props.label }}:</div>
    <div class="flex-1 w-10 bg-gray-100">
      <TagsInputRoot v-model="value" add-on-blur add-on-paste
        class="flex gap-2 items-center border border-gray-300 p-2 rounded-md w-full flex-wrap">
        <div class="flex flex-wrap gap-2">
          <TagsInputItem v-for="item in value" :key="item" :value="item"
            class="flex gap-0.5 bg-gray-200 border border-gray-400 items-center justify-center shadow-sm shadow-gray-400/50 focus-within:shadow-red-400 focus-within:border-red-300 rounded-md px-2 py-1">
            <TagsInputItemText class="text-sm pl-1 max-w-[10em] text-ellipsis overflow-hidden" :title="item"
              @click="handleEmailClick(item)" />
            <TagsInputItemDelete tabindex
              class="flex items-center p-1 bg-transparent focus:bg-red-300 hover:bg-red-300 hover:text-black rounded-full text-black">
              <Icon name="uil:times" class="h-4 w-4" />
            </TagsInputItemDelete>
          </TagsInputItem>
        </div>
        <TagsInputInput placeholder="user@example.com [enter]"
          class="text-sm font-mono flex-1 focus:outline-none rounded bg-transparent placeholder:text-gray-600 px-3 bg-white" />
      </TagsInputRoot>
    </div>
  </div>
</template>
<script setup lang="ts">
import { copyToClipboard } from '../utils/clipboard'
import { TagsInputInput, TagsInputItem, TagsInputItemDelete, TagsInputItemText, TagsInputRoot } from 'reka-ui'

type Props = {
  label: string
}

const snackbar = useSnackbar()

const props = defineProps<Props>()

const value = defineModel<string[]>({ required: true })

const handleEmailClick = async (email: string) => {
  await copyToClipboard(email)
  snackbar.add({
    type: 'info',
    title: `Copied to clipboard`,
    text: email
  })
}

</script>
