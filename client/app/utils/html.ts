/**
 * https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a#target
 */
export const TARGET_NEW_WINDOW = '_blank'

/**
 * The `noopener` prevents linked sites (theirs) having control over originating sites (ours)
 * via JavaScript https://mathiasbynens.github.io/rel-noopener/
 *
 * it's intentional to not have `noreferrer` here
 **/
export const EXTERNAL_LINK_REL = 'noopener'

export const ANCHOR_STYLE = 'text-violet-600 dark:text-violet-500 font-semibold no-underline hover:underline focus:underline'

export const PERSON_ID_STYLE = 'font-normal text-gray-600 dark:text-gray-200 ml-1'

export type HeadingLevel = 1 | 2 | 3 | 4 | 5 | 6

export type SelectOption = { value: string, label: string }
