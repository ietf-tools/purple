<template>
  <div class="h-full flex flex-col bg-white text-black dark:bg-black dark:text-white">
    <div class="flex flex-row bg-gray-200 dark:bg-gray-800 justify-between border-b border-gray-300 dark:border-gray-500">
      <div class="flex flex-row items-end pt-1 pb-2">
        <h1 class="text-xl font-bold pt-4 px-4 inline-block">
          New Email
        </h1>
        <div class="flex flex-row items-center">
          <p class="inline-block text-sm ml-4 mr-2 font-bold text-xs text-gray-700 dark:text-gray-300">templates: </p>
          <ul class="flex flex-row flex-wrap gap-2">
            <li v-for="mailTemplate in props.mailTemplates">
              <BaseButton @click="applyEmailTemplate(mailTemplate)" size="xs"
                :aria-selected="mailTemplate.template.msgtype === msgType" :class="{
                  'border-2 border-black dark:border-white shadow-xl': mailTemplate.template.msgtype === msgType,
                  'opacity-70': mailTemplate.template.msgtype !== msgType
                }">
                {{ mailTemplate.label }}
              </BaseButton>
            </li>
          </ul>
        </div>
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
    <div class="flex flex-row border-t-2 bg-gray-200 dark:bg-gray-800 border-gray-300 dark:border-gray-500 justify-end px-8 py-4 w-full">
      <BaseButton @click="confirmSend">Send</BaseButton>
    </div>
  </div>
</template>
<script setup lang="ts">
import { BaseButton } from '#components'
import { overlayModalKey } from '~/providers/providerKeys';
import type { MailTemplate } from '~/purple_client';

type Props = {
  draftName: string
  mailTemplates: MailTemplate[]
  onSuccess: () => Promise<void>
}
const props = defineProps<Props>()

const api = useApi()

const overlayModalKeyInjection = inject(overlayModalKey)

const firstMailTemplate = props.mailTemplates[0]

if (!firstMailTemplate) {
  throw Error('Expected at least one mail template but there were none')
}

const snackbar = useSnackbar()

const toEmails = ref<string[]>(firstMailTemplate.template.to.split(','))
const ccEmails = ref<string[]>(firstMailTemplate.template.cc?.split(',') ?? [])
const subject = ref<string>(firstMailTemplate.template.subject ?? '')
const body = ref<string>(firstMailTemplate.template.body ?? '')
const msgType = ref<MailTemplate['template']['msgtype']>(firstMailTemplate.template.msgtype)

if (!overlayModalKeyInjection) {
  throw Error('Expected injection of overlayModalKey')
}

const { closeOverlayModal } = overlayModalKeyInjection

const confirmSend = async () => {
  const shouldSend = confirm("Really send email?")
  if (!shouldSend) {
    return
  }
  const mailSendResponse = await api.documentMailSend({
    draftName: props.draftName,
    mailMessageRequest: {
      msgtype: msgType.value,
      to: toEmails.value.join(','),
      subject: subject.value,
      body: body.value,
      cc: ccEmails.value.join(',')
    }
  })
  if (mailSendResponse.type === 'success') {
    await props.onSuccess()
    snackbar.add({
      type: 'success',
      title: 'Email sent',
      text: 'Email sent'
    })
    closeOverlayModal()
  } else {
    snackbar.add({
      type: 'error',
      title: `Email wasn't sent`,
      text: mailSendResponse.message
    })
  }
}

const applyEmailTemplate = (mailTemplate: MailTemplate) => {
  if (subject.value.trim().length > 0 || body.value.trim().length > 0) {
    const shouldOverwrite = confirm(`Email subject/body are not blank. Overwrite with template '${mailTemplate.label}'?`)
    if (!shouldOverwrite) {
      return
    }
  }
  toEmails.value = mailTemplate.template.to.split(',')
  ccEmails.value = mailTemplate.template.cc?.split(',') ?? []
  subject.value = mailTemplate.template.subject
  body.value = mailTemplate.template.body
  msgType.value = mailTemplate.template.msgtype
}

</script>
