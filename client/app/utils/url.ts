import type { RpcPerson } from '~/purple_client'
import type { ResolvedQueueItem } from '../components/AssignmentsTypes'

export const AUTH_PATH = '/auth'

export const testIsAuthRoute = (path: string) => path.startsWith(AUTH_PATH)

export const documentPathBuilder = (document: Pick<ResolvedQueueItem, 'name'>) => `/docs/${document.name}/`

export const QUEUE_QUEUE_PATH = '/queue/queue'

const httpRegex = /^https?:\/\//
export const isExternalLink = (href?: string): boolean => {
  if (
    href === undefined
    // although this scenario isn't an external link we shouldn't treat it as a Vue Router link so we'll call it external
  ) {
    return true
  }
  return httpRegex.test(href ?? '')
}

export const isInternalLink = (href?: string): boolean => !isExternalLink(href)

export const isHashLink = (href?: string): boolean => !!href?.startsWith('#')

const mailtoRegex = /^mailto:/
export const isMailToLink = (href?: string): boolean => {
  return mailtoRegex.test(href ?? '')
}

const oidcRegex = /^\/oidc/
export const isOidcLink = (href?: string): boolean => {
  return oidcRegex.test(href ?? '')
}

export const datatrackerPersonLink = (email: string) => `https://datatracker.ietf.org/person/${encodeURIComponent(email)}`

export const teamMemberLink = (personId: number | undefined | null) => personId ? `/team/${personId}` : undefined

export const draftAssignmentsHref = (draftName: string | undefined | null, hashState: 'edit-authors' | 'edit-document-shepherd' | 'edit-stream-manger') => {
  if (!draftName) {
    return undefined
  }
  return `/docs/${draftName}/assignments#${hashState}`
}
