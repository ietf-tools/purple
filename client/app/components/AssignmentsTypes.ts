import type { Assignment, QueueItem, RpcPerson, RpcRole } from '~~/purple_client'

export type ResolvedAssignment = Omit<Assignment, 'person'> & {
  person?: RpcPerson
}

export type ResolvedQueueItem = QueueItem & {
  assignments?: ResolvedAssignment[]
  needsAssignment: RpcRole | null | undefined
}

export type ResolvedPerson = RpcPerson & {
  assignments?: Assignment[]
}
