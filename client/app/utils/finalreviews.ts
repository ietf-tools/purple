import { Anchor, Icon, BaseBadge } from '#components'
import type { Assignment, Cluster, RpcPerson, RfcToBeBlockingReason } from '~/purple_client'

export const columnFormatterCluster = (clusterNumber?: Cluster["number"]) => {
  if (!clusterNumber) {
    return '-'
  }
  return h('span', [
    h(Anchor, {
      href: `/clusters/${clusterNumber}`,
      class: "inline-flex items-center gap-1 text-blue-600"
    }, () => [
      h(Icon, { name: "pajamas:group", class: "h-5 w-5" }),
      clusterNumber
    ])
  ])
}

type ColumnFormatterAssignmentsProps = {
  assignments?: Assignment[],
  rfcToBeId?: number,
  people: RpcPerson[],
  queueItemsIsPending: boolean,
  blockingReasons?: RfcToBeBlockingReason[],
  rowForDebug: unknown,
}

export const columnFormatterAssignments = ({ assignments, rfcToBeId, people, queueItemsIsPending, blockingReasons, rowForDebug }: ColumnFormatterAssignmentsProps) => {
  if (!assignments) {
    return 'No assignments'
  }

  if (rfcToBeId === undefined) {
    throw Error(`Internal error: expected queueItem to have id but was ${JSON.stringify(rowForDebug)}`)
  }

  const sortedAssignments = [...assignments].sort((a, b) => {
    const nameA = people.find(p => p.id === a.person)?.name ?? ''
    const nameB = people.find(p => p.id === b.person)?.name ?? ''
    return nameA.localeCompare(nameB, 'en')
  })

  const listItems = sortedAssignments.map(assignment => {
    const rpcPerson = people.find(p => p.id === assignment.person)
    const name = rpcPerson ? rpcPerson.name : queueItemsIsPending ? '...' : '(unknown person)'

    const roleBadgeChildren: VNode[] = [h(BaseBadge, { label: assignment.role, class: 'ml-2' })]
    if (assignment.role === 'blocked' && blockingReasons && blockingReasons.length > 0) {
      const reasons = blockingReasons.map(br => br.reason?.name).filter(Boolean).join(', ')
      roleBadgeChildren.push(h('span', { class: 'text-xs text-gray-500 dark:text-neutral-400 ml-1' }, reasons))
    }

    return h('li', { class: 'flex items-baseline gap-1' }, [
      h(Anchor, {
        href: rpcPerson ? `/team/${rpcPerson.id}` : undefined,
        class: [ANCHOR_STYLE, 'text-sm']
      }, () => name),
      ...roleBadgeChildren,
    ])
  })

  return h('ul', { class: 'flex flex-col gap-y-2' }, listItems)
}
