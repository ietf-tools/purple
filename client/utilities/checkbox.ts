export const CHECKBOX_INDETERMINATE = 'indeterminate' as const

export type CheckboxTristate = boolean | typeof CHECKBOX_INDETERMINATE
