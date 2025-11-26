export const IANAActionOptions = {
  "iana-no-actions": 'This document has no IANA actions',
  'iana-waiting-on': 'IANA has not completed actions in draft',
  'iana-completed': 'IANA has completed actions in draft',
  'iana-registry-changes-needed': 'Changes to registries are required due to RFC edits',
  'iana-reconciled-changes': 'IANA has reconciled changes between draft and RFC'
} as const

export type IANAActionsEnum = keyof typeof IANAActionOptions

export const IANAActionsEntries = Object.entries(IANAActionOptions) as [IANAActionsEnum, string][]
