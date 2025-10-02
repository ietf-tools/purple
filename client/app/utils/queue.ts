import type { Assignment, Label, RpcRole, SimpleCluster } from '~/purple_client'

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

export type TabId = (typeof tabs)[number]['id']

export const sortDate = (
  dateA: Date | undefined | null,
  dateB: Date | undefined | null
): number => {
  if (!dateA && !dateB) {
    return 0
  } else if (!dateB) {
    return 1
  } else if (!dateA) {
    return -1
  }
  return dateA.getTime() - dateB.getTime()
}

export const sortLabels = (
  labelsA: Label[] | undefined | null,
  labelsB: Label[] | undefined | null
): number => {
  if (!labelsA && !labelsB) {
    return 0
  } else if (!labelsB) {
    return 1
  } else if (!labelsA) {
    return -1
  }

  const slugsA = labelsA.map((label) => label.slug).join(',')
  const slugsB = labelsB.map((label) => label.slug).join(',')

  return slugsA.localeCompare(slugsB)
}

export const sortCluster = (
  clusterA: SimpleCluster | undefined | null,
  clusterB: SimpleCluster | undefined | null
): number => {
  if (!clusterA && !clusterB) {
    return 0
  } else if (!clusterB) {
    return 1
  } else if (!clusterA) {
    return -1
  }

  return clusterA.number - clusterB.number
}

export type AssignmentMessageProps =
  | {
      type: 'assign'
      role: Assignment['role']
      rfcToBeId: number
    }
  | {
      type: 'change'
      assignments: Assignment[]
      role: Assignment['role']
      rfcToBeId: number
    }

export type RpcPersonWorkload = {
  personId: number
  clusterIds: number[]
  pageCountByRole: Record<string, number>
}
