import { DateTime } from 'luxon'
import type { Row } from '@tanstack/vue-table'

export type Tab = {
  id: string
  name: string
  to: string
  icon: string
  iconAnimate?: boolean
}

export const tabs: Tab[] = [
  {
    id: 'submissions',
    name: 'Submissions',
    to: '/queue/submissions',
    icon: 'uil:bolt-alt'
  },
  {
    id: 'enqueuing',
    name: 'Enqueuing',
    to: '/queue/enqueuing',
    icon: 'ic:outline-queue'
  },
  {
    id: 'queue',
    name: 'Queue',
    to: '/queue/queue',
    icon: 'uil:clock'
  },
  {
    id: 'published',
    name: 'Recently Published',
    to: '/queue/published',
    icon: 'uil:check-circle'
  }
] as const

export type TabId = (typeof tabs)[number]["id"]

export const sortDate = (dateA: Date | undefined | null, dateB: Date | undefined | null): number => {
  if(!dateA && !dateB) {
    return 0
  } else if(dateA && !dateB) {
    return 1
  }  else if(!dateA && dateB) {
    return -1
  }
  if(!dateA || !dateB) {
    // This is to help TS narrow types. This code path shouldn't happen
    // because the preceding code should already remove these as a possibility
    throw Error("Internal error. This shouldn't happen")
  }
  return dateA.getTime() - dateB.getTime()
}
