import EmailModal from "~/components/EmailModal.vue"
import type { OverlayModal } from "~/providers/providerKeys"
import type { MailTemplate, RfcToBe } from "~/purple_client"

type OpenEmailModalProps = {
  overlayModal: OverlayModal
  draftName: string
  rfcToBeId: NonNullable<RfcToBe["id"]>
  api: ReturnType<typeof useApi>
  mailTemplateSort?: (a: MailTemplate, b: MailTemplate) => number
}

export const openEmailModal = async ({ overlayModal, api, draftName, rfcToBeId, mailTemplateSort }: OpenEmailModalProps) => {
  const { openOverlayModal } = overlayModal

  try {
    const mailTemplates = await api.mailtemplateList({
      rfctobeId: rfcToBeId,
    })

    const mailTemplatesSorted = mailTemplateSort ? mailTemplates.sort(mailTemplateSort) : mailTemplates

    console.log({ mailTemplatesSorted })

    await openOverlayModal({
      component: EmailModal,
      componentProps: {
        draftName,
        mailTemplates: mailTemplatesSorted,
        onSuccess: () => {
          // nothing
        }
      },
      mode: 'overlay',
    }).catch(e => {
      if (e === undefined) {
        // ignore... it's just signalling that the modal has closed
      } else {
        console.error(e)
        throw e
      }
    })
  } catch (e) {
    console.error(e)
  }
}
