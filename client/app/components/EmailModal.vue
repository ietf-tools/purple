<template>
  <div class="h-full flex flex-col bg-white text-black dark:bg-black dark:text-white">
    <div class="flex flex-row bg-gray-200 dark:bg-gray-800 justify-between border-b border-gray-300">
      <div>
        <h1 class="text-xl font-bold pt-4 px-4 py-3 inline-block">
          New Email
        </h1>
        <p class="inline-block text-sm ml-4 mr-2">templates: </p>
        <ul class="inline-block">
          <li class="inline">
            <BaseButton v-for="emailTemplate in props.emailTemplates" @click="applyEmailTemplate(emailTemplate)" size="xs">
              {{ emailTemplate.name }}
            </BaseButton>
          </li>
        </ul>
      </div>
      <BaseButton btnType="cancel" class="m-2 flex items-center" @click="closeOverlayModal">
        <Icon name="uil:times" class="h-5 w-5" aria-hidden="true" />
      </BaseButton>
    </div>
    <div class="flex-1 flex flex-col gap-5 overflow-y-scroll px-4 pt-4 pb-7">

      <EmailFieldEmails v-model="toEmails" label="To" />
      <EmailFieldEmails v-model="ccEmails" label="CC" />
      <EmailFieldText v-model="subject" label="Subject" field-id="subject" :is-multiline="false" fieldClass="flex-1" />
      <EmailFieldText v-model="body" label="Body" field-id="body" :is-multiline="true" class="flex-1"
        fieldClass="flex-1" />
    </div>
    <div class="flex flex-row border-t-2 bg-gray-200 dark:bg-gray-800 border-gray-300 justify-end px-8 py-4 w-full">
      <BaseButton @click="confirmSend">Send</BaseButton>
    </div>
  </div>
</template>
<script setup lang="ts">
import { BaseButton } from '#components'
import { overlayModalKey } from '~/providers/providerKeys';

type Props = {
  defaultToEmails: string[]
  defaultCCEmails: string[]
  defaultSubject: string
  defaultBody: string
  emailTemplates: EmailTemplate[]
  onSuccess: () => void
}
const props = defineProps<Props>()

const api = useApi()

const overlayModalKeyInjection = inject(overlayModalKey)

const toEmails = ref<string[]>([...props.defaultToEmails])
const ccEmails = ref<string[]>([...props.defaultCCEmails])
const subject = ref<string>(props.defaultSubject ?? '')
const body = ref<string>(props.defaultBody ?? '')

if (!overlayModalKeyInjection) {
  throw Error('Expected injection of overlayModalKey')
}

const { closeOverlayModal } = overlayModalKeyInjection

const confirmSend = () => {
  const shouldSend = confirm("Really send email?")
  if (!shouldSend) {
    return
  }


}

const applyEmailTemplate = (emailTemplate: EmailTemplate) => {
  if (subject.value.trim().length > 0 || body.value.trim().length > 0) {
    const shouldOverwrite = confirm(`Email subject/body are not blank. Overwrite with template '${emailTemplate.name}'?`)
    if (!shouldOverwrite) {
      return
    }
  }
  subject.value = emailTemplate.subject
  body.value = emailTemplate.body
}

</script>
