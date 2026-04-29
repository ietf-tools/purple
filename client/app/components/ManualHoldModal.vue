<template>
  <form class="py-2 px-4 bg-white text-black dark:bg-black dark:text-white h-full" @submit.prevent="handleSave">
    <Heading :heading-level="2" class="pb-3 pt-5">Set Manual Hold</Heading>
    <div class="mb-4">
      <label class="block text-sm font-medium mb-1" for="manual-hold-comment">Comment (optional)</label>
      <textarea
        id="manual-hold-comment"
        v-model="comment"
        rows="4"
        class="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-neutral-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        placeholder="Reason for manual hold..."
      />
    </div>
    <div class="border-t-2 border-gray-400 mt-5 pt-2 flex justify-end gap-2">
      <BaseButton btn-type="cancel" @click="cancel()">Cancel</BaseButton>
      <BaseButton btn-type="default" type="submit" :disabled="isSaving">
        Set Hold
        <Icon v-show="isSaving" name="ei:spinner-3" size="1.2em" class="animate-spin ml-1" />
      </BaseButton>
    </div>
  </form>
</template>

<script setup lang="ts">
import { overlayModalMethodsKey } from '~/providers/providerKeys'

type Props = {
  onConfirm: (comment: string) => Promise<void>
}

const props = defineProps<Props>()

const { ok, cancel } = inject(overlayModalMethodsKey)!

const comment = ref('')
const isSaving = ref(false)

const handleSave = async () => {
  isSaving.value = true
  try {
    await props.onConfirm(comment.value)
    ok()
  } finally {
    isSaving.value = false
  }
}
</script>
