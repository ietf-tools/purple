<template>
  <div class="border-5 border-gray-700 text-gray-500">
    <h2 class="font-bold">Authors (drag to reorder)</h2>
    <ul ref="parent" class="block">
      <li class="flex items-center  justify-between pl-4 pr-1 py-1 mt-1 border rounded-md border-gray-400" v-for="(author, index) in authors" :index="index" :key="author.id">
         <span class="cursor-ns-resize">{{ author.titlepageName }}</span>
         <button type="button" @click="handleRemoveAuthor(index)" class="border-1 cursor-not-allowed border-gray-500 rounded px-2 py-1 hover:bg-gray-200 focus:bg-gray-200">&times;</button>
      </li>
    </ul>
    <EditAuthorsAdd v-model:authors="authors" />
  </div>
</template>

<script setup lang="ts">
import { useDragAndDrop } from "fluid-dnd/vue";
import type { RfcAuthor } from '~/purple_client';

type Props = {};

const props = defineProps<Props>();

const authors = defineModel<RfcAuthor[]>('authors', { required: true })

const handleRemoveAuthor = (index: number) => {
  authors.value.splice(index, 1)
}

const [ parent ] = useDragAndDrop(authors);

</script>
