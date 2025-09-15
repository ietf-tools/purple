import { DateTime } from "luxon";
import type { RfcToBe } from "~/purple_client";
import { uniqBy } from 'lodash-es'
import type { ResolvedPerson, ResolvedQueueItem } from "~/components/AssignmentsTypes";
import { assert, assertIsNumber } from "./typescript";

export type CookedDraft = Omit<RfcToBe, 'externalDeadline'> & {
  externalDeadline: DateTime<false> | DateTime<true> | null
}

type CookedQueueItemProps = {
  document: ResolvedQueueItem
  selected?: boolean
  editors?: ResolvedPerson[]
  editorAssignedDocuments?: Record<string, ResolvedQueueItem[] | undefined>
  currentTime: Ref<DateTime<true> | DateTime<false>>
}

export const cookQueueItem = ({ document, editors, editorAssignedDocuments, currentTime }: CookedQueueItemProps) => {
  const teamPagesPerHour = 1.0
  const assignmentsPersons = document?.assignments?.map(
    assignment => editors?.find(editor => editor.id === assignment.person?.id)
  ).filter(editor => !!editor) ?? []
  const assignmentsPersonIds = uniqBy(assignmentsPersons, editor => editor.id)
    .map(editor => editor.id)
    .filter(id => typeof id === 'number')

  return ({
    ...document,
    externalDeadline: document.externalDeadline && DateTime.fromJSDate(document.externalDeadline),
    assignments: document.assignments,
    assignmentsPersons,
    assignmentsPersonIds,
    editors: editors
      ?.map(editor => {
        const { id, hoursPerWeek } = editor
        assert(typeof id === 'number', `expected number was typeof=${typeof id}`)
        assertIsNumber(hoursPerWeek)
        const { pages } = document
        assertIsNumber(pages)

        const assignedDocuments = editorAssignedDocuments?.[id]
        const completeBy = currentTime.value.plus({ days: 7 * pages / teamPagesPerHour / hoursPerWeek })

        return {
          ...editor,
          id,
          assignedDocuments,
          completeBy,
        }
      })
      .sort((a, b) => a.completeBy.toMillis() - b.completeBy.toMillis())
  })
}


export type CookedQueueItem = ReturnType<typeof cookQueueItem>
