import { Anchor, Icon, BaseBadge } from '#components'
import { groupBy } from 'lodash-es'
import type { Assignment, Cluster, RpcPerson } from '~/purple_client'

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
  rowForDebug: unknown,
}

export const columnFormatterAssignments = ({ assignments, rfcToBeId, people, queueItemsIsPending, rowForDebug }: ColumnFormatterAssignmentsProps) => {
  if (!assignments) {
    return 'No assignments'
  }

  if (rfcToBeId === undefined) {
    throw Error(`Internal error: expected queueItem to have id but was ${JSON.stringify(rowForDebug)}`)
  }

  const listItems: VNode[] = []

  const assignmentsByRoles = groupBy(
    assignments,
    (assignment) => assignment.role
  )

  const orderedRoles = Object.keys(assignmentsByRoles)
    .sort((a, b) => a.localeCompare(b, 'en'))

  for (const role of orderedRoles) {
    const assignmentsOfRole = assignmentsByRoles[role] ?? []

    const redundantAssignmentsOfSamePersonToSameRole = assignmentsOfRole.filter((assignment, _index, arr) => {
      const { person } = assignment
      if (person === undefined || person == null) {
        return false
      }
      const firstAssignmentOfPersonToRole = arr.find(arrAssignment => assignment.person && arrAssignment.person && arrAssignment.person === assignment.person)
      if (!firstAssignmentOfPersonToRole) {
        console.log(`Couldn't find first assignment for person #${assignment.person} in`, arr)
        throw Error(`Internal error. Should be able to find first assignment for person #${assignment.person}. See console`)
      }
      // the first assignment of person in the list of assignments should always match the current assignment of person
      // because there shouldn't be duplicate/redundant assignments
      // but if the id is different then it is a redundant assignment,
      // so we'll prompt the user to delete them
      return assignment.id !== firstAssignmentOfPersonToRole.id
    })

    listItems.push(h('li', { class: 'flex gap-3' }, [
      h('span',
        h(BaseBadge, { label: role, class: 'mr-1' })),
      h('ul', { class: 'flex flex-col gap-2' }, [
        ...assignmentsOfRole.map(assignment => {
          const rpcPerson = people.find((p) => p.id === assignment.person)
          return h(Anchor, {
            href: rpcPerson ? `/team/${rpcPerson.id}` : undefined,
            class: [ANCHOR_STYLE, 'text-sm nowrap']
          }, () => [
            rpcPerson ? rpcPerson.name : queueItemsIsPending ? `...` : '(unknown person)',
          ])
        }).reduce((acc, item, index, arr) => {
          // add commas between items
          const listItemChildren = []
          listItemChildren.push(item)
          if (index < arr.length - 1) {
            listItemChildren.push(', ')
          } else {
            listItemChildren.push(' ')
          }
          const listItem = h('li', listItemChildren)
          acc.push(listItem)
          return acc
        }, [] as (VNode | string)[])]),
    ]))
  }

  return h('ul', { class: 'flex flex-col gap-x-1 gap-y-3' }, listItems)
}
