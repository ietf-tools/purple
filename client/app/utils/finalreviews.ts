import { Anchor, Icon, BaseBadge } from '#components'
import type {
  ActionHolder,
  Assignment,
  Cluster,
  RpcPerson,
  RfcToBeBlockingReason
} from '~/purple_client'

// A manual hold's reason is the free text given when setting it, cut to
// maxReasonLength where a view has no room for all of it.
export const formatBlockingReason = (
  br: RfcToBeBlockingReason,
  maxReasonLength?: number
): string | undefined => {
  if (br.reason?.slug !== 'manual_hold' || !br.comment) {
    return br.reason?.name
  }
  const reason =
    maxReasonLength && br.comment.length > maxReasonLength
      ? `${br.comment.substring(0, maxReasonLength)}...`
      : br.comment
  return `${br.reason.name}: ${reason}`
}

export const formatBlockingReasonList = (
  blockingReasons: RfcToBeBlockingReason[],
  actionholders?: ActionHolder[],
  maxReasonLength?: number
): string[] =>
  blockingReasons
    .map((br) => {
      if (br.reason?.slug === 'actionholder_active' && actionholders?.length) {
        const names = actionholders
          .map((ah) => ah.body || ah.person?.name)
          .filter(Boolean)
          .join(', ')
        return `${br.reason.name}: ${names}`
      }
      return formatBlockingReason(br, maxReasonLength)
    })
    .filter((reason): reason is string => Boolean(reason))

export const blockingReasonsList = (
  blockingReasons: RfcToBeBlockingReason[],
  actionholders?: ActionHolder[]
) => {
  const reasons = formatBlockingReasonList(blockingReasons, actionholders)
  const shortReasons = formatBlockingReasonList(blockingReasons, actionholders, 40)
  return h(
    'ul',
    { class: 'text-xs text-gray-500 dark:text-neutral-400 w-64' },
    shortReasons.map((shortReason, index) =>
      h(
        'li',
        {
          class: 'flex gap-1',
          title: shortReason === reasons[index] ? undefined : reasons[index]
        },
        [h('span', { 'aria-hidden': 'true' }, '•'), h('span', shortReason)]
      )
    )
  )
}

export const columnFormatterCluster = (clusterNumber?: Cluster['number']) => {
  if (!clusterNumber) {
    return '-'
  }
  return h('span', [
    h(
      Anchor,
      {
        href: `/clusters/${clusterNumber}`,
        class: 'inline-flex items-center gap-1 text-blue-600'
      },
      () => [h(Icon, { name: 'pajamas:group', class: 'h-5 w-5' }), clusterNumber]
    )
  ])
}

type ColumnFormatterAssignmentsProps = {
  assignments?: Assignment[]
  rfcToBeId?: number
  people: RpcPerson[]
  queueItemsIsPending: boolean
  blockingReasons?: RfcToBeBlockingReason[]
  actionholders?: ActionHolder[]
  rowForDebug: unknown
}

export const columnFormatterAssignments = ({
  assignments,
  rfcToBeId,
  people,
  queueItemsIsPending,
  blockingReasons,
  actionholders,
  rowForDebug
}: ColumnFormatterAssignmentsProps) => {
  if (!assignments) {
    return 'No assignments'
  }

  if (rfcToBeId === undefined) {
    throw Error(
      `Internal error: expected queueItem to have id but was ${JSON.stringify(rowForDebug)}`
    )
  }

  const sortedAssignments = [...assignments].sort((a, b) => {
    const nameA = people.find((p) => p.id === a.person)?.name ?? ''
    const nameB = people.find((p) => p.id === b.person)?.name ?? ''
    return nameA.localeCompare(nameB, 'en')
  })

  const listItems = sortedAssignments.map((assignment) => {
    const rpcPerson = people.find((p) => p.id === assignment.person)
    const name = rpcPerson ? rpcPerson.name : queueItemsIsPending ? '...' : '(unknown person)'

    const roleBadgeChildren: VNode[] = [h(BaseBadge, { label: assignment.role })]
    if (assignment.role === 'blocked' && blockingReasons && blockingReasons.length > 0) {
      roleBadgeChildren.push(blockingReasonsList(blockingReasons, actionholders))
    }

    return h('li', { class: 'flex items-baseline gap-2' }, [
      h(
        Anchor,
        {
          href: rpcPerson ? `/team/${rpcPerson.id}` : undefined,
          class: [ANCHOR_STYLE, 'text-sm w-36 shrink-0']
        },
        () => name
      ),
      ...roleBadgeChildren
    ])
  })

  return h('ul', { class: 'flex flex-col gap-y-2' }, listItems)
}
