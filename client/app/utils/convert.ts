import type { QueueItem, RfcToBe } from "~/purple_client";

type _MissingKeys = keyof Omit<Record<keyof RfcToBe, boolean>, keyof QueueItem>

/**
 * There is no 1:1 conversion between QueueItem and RfcToBe so this should only be used
 * when the missing props don't matter. A list of missing props can be viewed by devs
 * with the `_MissingKeys` type above, and the return value of ''
 */
export const queueItemToRfcToBe = (queueItem: QueueItem): RfcToBe => {
  const {
    id,
    name,
    disposition,
    externalDeadline,
    internalGoal,
    labels,
    cluster,
    assignmentSet,
    actionholderSet,
    pendingActivities,
    rfcNumber,
    ianaStatus,
  } = queueItem

  return {
    id,
    name,
    disposition,
    externalDeadline,
    internalGoal,
    labels: labels?.map(label => label.id).filter(id => typeof id === 'number') ?? [],
    cluster,
    authors: [],
    assignmentSet,
    actionholderSet,
    pendingActivities,
    rfcNumber,
    publishedAt: null,
    consensus: undefined,
    subseries: undefined,
    ianaStatus,
    submittedFormat: '',
    submittedBoilerplate: '',
    submittedStdLevel: '',
    submittedStream: '',
    intendedBoilerplate: '',
    intendedStdLevel: '',
    intendedStream: ''
  }
}
