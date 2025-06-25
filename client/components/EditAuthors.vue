<template>
  <div>
    <ul ref="parent" class="border-1 border-gray-500 min-h-[100vh]">
      <li class="number" v-for="(author, index) in props.authors"  :index="index" :key="author.id">
        {{ author.id }}
      </li>
    </ul>
    <fieldset>
      <legend>Add author</legend>
    </fieldset>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useDragAndDrop } from "fluid-dnd/vue";
import type { RfcAuthor } from '~/purple_client';

type Props = {
  authors: RfcAuthor[]
}

const props = defineProps<Props>()
const list = ref([1, 2, 3]);
const [ parent ] = useDragAndDrop(list);

</script>
