export const TRISTATE_MIXED = 'mixed' as const

export type TristateValue = boolean | typeof TRISTATE_MIXED
