export interface DocumentCardType {
  id: string
  name: string
  externalDeadline: string
  needsAssignment?: {
    name: string
  }
  assignments: string[]
  pages: number
}
