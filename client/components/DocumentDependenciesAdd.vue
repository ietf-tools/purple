<template>
  <div>
    <DialogRoot v-model:open="isOpenDependencyModal">
      <DialogPortal>
        <DialogOverlay class="bg-black/50 fixed inset-0 z-50" />
        <DialogContent
          class="fixed top-[50%] left-[50%] max-h-[85vh] w-[90vw] max-w-[450px] translate-x-[-50%] translate-y-[-50%] rounded-md bg-white p-5 shadow-xl focus:outline-none z-[100]">
          <DialogTitle class="text-md font-bold mb-4">
            New Document Reference
          </DialogTitle>

          <DialogFieldText v-model="relationship" label="Relationship" id="relationship" />
          <DialogFieldText v-model="targetDraftName" label="Target draftName" id="targetDraftName" />

          <div class="mt-[25px] flex justify-end">
            <BaseButton
              btn-type="default"
              @click="addDependencyItem"
              class="text-sm hover:bg-green5 inline-flex h-[35px] items-center justify-center rounded-lg px-[15px] font-semibold leading-none focus:shadow-[0_0_0_2px] focus:outline-none"
            >
              Add
            </BaseButton>
          </div>
          <DialogClose
            class="text-gray-700 absolute top-3 right-3 inline-flex p-2 appearance-none items-center justify-center rounded-full hover:bg-gray-200"
            aria-label="Close"
          >
            <Icon name="uil:times" class="h-6 w-6" aria-hidden="true"/>
          </DialogClose>
        </DialogContent>
      </DialogPortal>
    </DialogRoot>
  </div>
</template>

<script setup lang="ts">
import {
  DialogClose,
  DialogContent,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle,
} from "reka-ui"
import type { DocumentsReferencesCreateRequest, RpcRelatedDocument } from "~/purple_client"
import { snackbarForErrors } from "~/utilities/snackbar"

const relatedDocuments = defineModel<RpcRelatedDocument[]>('relatedDocuments', { required: true, default: [] })

const isOpenDependencyModal = defineModel<boolean>('isOpenDependencyModal', { required: true })

type Props = {
  draftName: string
}

const props = defineProps<Props>()

const relationship = ref<string>("")
const targetDraftName = ref<string>("")

const snackbar = useSnackbar()

const api = useApi()

const addDependencyItem = async () => {
  const createArg: DocumentsReferencesCreateRequest = {
    draftName: props.draftName,
    rpcRelatedDocument: {
      relationship: relationship.value,
      targetDraftName: targetDraftName.value
    }
  }
  try {
    const newRpcRelatedDocument = await api.documentsReferencesCreate(createArg)
    relatedDocuments.value.push(newRpcRelatedDocument)
    // reset form
    relationship.value = ''
    targetDraftName.value = ''
  } catch (e: unknown) {
    snackbarForErrors({
      snackbar,
      defaultTitle: `Unable to add document reference`,
      error: e
    })
  }
}

</script>
