import { IanaStatusSlugEnum } from '../purple_client/models/IanaStatusSlugEnum'

export type IANAActionsEnum = IanaStatusSlugEnum

export const IANAActionsEntries = Object.entries(IanaStatusSlugEnum) as [IANAActionsEnum, string][]

export const parseIanaStatusSlug = (slug: string | undefined): IanaStatusSlugEnum | undefined => {
  switch (slug) {
    case "no_actions":
      return "no_actions"
    case "not_completed":
      return "not_completed"
    case "changes_required":
      return "changes_required"
    case "reconciled":
      return "reconciled";
  }
  return undefined
}
