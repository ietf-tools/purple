import { IanaStatusSlugEnum } from '../purple_client/models/IanaStatusSlugEnum'

export type IANAActionsEnum = IanaStatusSlugEnum

export const IANAActionsEntries = Object.entries(IanaStatusSlugEnum) as [IANAActionsEnum, string][]


export const parseIanaStatusSlug = (slug: string | undefined): IanaStatusSlugEnum | undefined => {
  if (slug && Object.values(IanaStatusSlugEnum).includes(slug as IanaStatusSlugEnum)) {
    return slug as IanaStatusSlugEnum
  }
  return undefined
}
