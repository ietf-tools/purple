import type { ResolvedQueueItem } from '../components/AssignmentsTypes'

export const AUTH_PATH = '/auth'

export const testIsAuthRoute = (path: string) => path.startsWith(AUTH_PATH)

export const documentPathBuilder = (document: Pick<ResolvedQueueItem, 'name'>) =>
  `/docs/${document.name}/`

export const QUEUE_QUEUE_PATH = '/queue/queue'
export const QUEUE_SUBMISSIONS_PATH = '/queue/submissions'

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

export const teamMemberLink = (personId: number | undefined | null) =>
  personId ? `/team/${personId}` : undefined

export const draftAssignmentsHref = (
  draftName: string | undefined | null,
  hashState: 'edit-authors' | 'edit-document-shepherd' | 'edit-stream-manger'
) => {
  if (!draftName) {
    return undefined
  }
  return `/docs/${draftName}/assignments#${hashState}`
}

export const gitHubUrlBuilder = (repository: string): string => `https://github.com/${repository}`

const RFC_EDITOR_MAIL_LIST = 'rfc-editor'

/**
 * Mail archive search for messages on the rfc-editor list whose subject names the
 * draft. The `subject=` parameter is a loose match that returns any message sharing
 * a word with the draft name; a `subject:(...)` operator in `q` requires every word.
 */
export const mailArchiveSearchUrl = (draftName: string): string => {
  const params = new URLSearchParams({
    email_list: RFC_EDITOR_MAIL_LIST,
    q: `subject:(${draftName})`
  })
  return `https://mailarchive.ietf.org/arch/search/?${params}`
}
