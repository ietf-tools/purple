import type { Assignment, Cluster, Label, QueueItem, SimpleCluster } from '~/purple_client'

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

export type RpcPeopleWorkload = Record<number, RpcPersonWorkload>

/**
 * Calculate the workload of people
 */
export const calculatePeopleWorkload = (clusters: Cluster[], queueItems: Pick<QueueItem, 'id' | 'name' | 'assignmentSet' | 'pages'>[]): RpcPeopleWorkload => {
  const peopleWorkload: Record<number, RpcPersonWorkload> = {}

  const addToPersonWorkload = (personId: number | null | undefined, clusterIds: number[], role: Assignment['role'], pageCount: number | undefined): void => {
    assertIsNumber(personId)

    console.log({ pageCount })
    assert(role.length !== 0)
    assert(typeof pageCount === 'number')

    const editorWorkload: RpcPersonWorkload = peopleWorkload[personId] ?? { personId, clusterIds: [], pageCountByRole: {} }
    if (clusterIds !== undefined) {
      clusterIds.forEach(clusterId => {
        if (!editorWorkload.clusterIds.includes(clusterId)) {
          editorWorkload.clusterIds.push(clusterId)
        }
      })
    }
    editorWorkload.pageCountByRole[role] = (editorWorkload.pageCountByRole[role] ?? 0) + pageCount

    peopleWorkload[personId] = editorWorkload
  }
  queueItems.forEach(doc => {
    const clustersWithDocument = clusters.filter(cluster => cluster.documents.some(clusterDocument =>
      clusterDocument.name === doc.name
    ))
    const clusterIds = clustersWithDocument.map(cluster => cluster.number)
    doc.assignmentSet?.forEach(assignment => {
      if (assignment.person !== undefined && assignment.person !== null) {
        addToPersonWorkload(assignment.person, clusterIds, assignment.role, doc.pages ?? 1)
      } else {
        console.warn("Doc name", doc.name, `(#${doc.id})`, "  has assignment without person ", assignment.person, typeof assignment.person, JSON.stringify(assignment))
      }
    })
  })

  return peopleWorkload
}
