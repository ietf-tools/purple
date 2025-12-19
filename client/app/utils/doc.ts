import type { Tab } from './tab'

export const docTabsFactory = (draftName: string) => {
  const sanitisedDraftName = encodeURIComponent(draftName)
  return [
    {
      id: 'index',
      name: 'Info',
      to: `/docs/${sanitisedDraftName}`,
      icon: 'fluent:document-one-page-sparkle-16-regular'
    },
    {
      id: 'assignments',
      name: 'Assignments',
      to: `/docs/${sanitisedDraftName}/assignments`,
      icon: 'fluent:layer-diagonal-person-16-regular'
    },
    {
      id: 'final-reviews',
      name: 'Final Reviews',
      to: `/docs/${sanitisedDraftName}/final-reviews`,
      icon: 'fluent:emoji-hand-16-regular'
    },
    {
      id: 'history',
      name: 'History',
      to: `/docs/${sanitisedDraftName}/history`,
      icon: 'fluent:history-28-filled'
    },
  ] as const satisfies Tab[]
}

export type DocTabId = (ReturnType<typeof docTabsFactory>)[number]['id']
