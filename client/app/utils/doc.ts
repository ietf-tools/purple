import type { Tab } from './tab'

export const docTabsFactory = (draftName: string) => {
  const sanitisedDraftName = encodeURIComponent(draftName)
  return [
    {
      id: 'index',
      name: 'Info',
      to: `/docs/${sanitisedDraftName}`,
      icon: 'uil:bolt-alt'
    },
    {
      id: 'people',
      name: 'People',
      to: `/docs/${sanitisedDraftName}/people`,
      icon: 'ic:outline-queue'
    },
    {
      id: 'public',
      name: 'Public',
      to: `/docs/${sanitisedDraftName}/public`,
      icon: 'ic:outline-queue'
    },
    {
      id: 'history',
      name: 'History',
      to: `/docs/${sanitisedDraftName}/history`,
      icon: 'ic:outline-queue'
    },
  ] as const satisfies Tab[]
}

export type DocTabId = (ReturnType<typeof docTabsFactory>)[number]['id']
