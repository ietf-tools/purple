export type Tab = {
  id: string
  name: string
  to: string
  icon: string
  iconAnimate?: boolean
}

export const tabs = [
  {
    id: 'submissions',
    name: 'Submissions',
    to: '/queue2/submissions',
    icon: 'uil:bolt-alt'
  },
  {
    id: 'enqueuing',
    name: 'Enqueuing',
    to: '/queue2/enqueuing',
    icon: 'ic:outline-queue'
  },
  {
    id: 'queue',
    name: 'Queue',
    to: '/queue2/queue',
    icon: 'uil:clock'
  },
  {
    id: 'published',
    name: 'Recently Published',
    to: '/queue2/published',
    icon: 'uil:check-circle'
  }
] as const satisfies Tab[]

export type TabId = (typeof tabs)[number]["id"]

