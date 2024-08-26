export interface DocumentCardType {
  id: string
  name: string
  external_deadline: string
  needsAssignment?: {
    name: string
  }
  assignments: string[]
  pages: number
}
