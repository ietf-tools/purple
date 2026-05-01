export const sortObject = <T extends Record<string, unknown>>(obj: T): T => {
    return Object.keys(obj).sort().reduce(function (result, _key) {
        const key: keyof T = _key
        result[key] = obj[key];
        return result;
    }, {} as T);
}

export const assignmentRoleOrder = [
  'enqueuer',
  'formatting',
  'ref_checker',
  'first_editor',
  'second_editor',
  'final_review_editor',
  'publisher',
] as const

/** Sort assignments by role order, interleaving 'blocked' entries chronologically by id. */
export function sortAssignmentsByRole<T extends { id?: number | null; role: string }>(assignments: T[]): T[] {
  const nonBlocked = assignments
    .filter((a) => a.role !== 'blocked')
    .sort((a, b) => {
      const roleDiff = assignmentRoleOrder.indexOf(a.role as typeof assignmentRoleOrder[number]) - assignmentRoleOrder.indexOf(b.role as typeof assignmentRoleOrder[number])
      if (roleDiff !== 0) return roleDiff
      return (a.id ?? 0) - (b.id ?? 0)
    })

  const blocked = assignments
    .filter((a) => a.role === 'blocked')
    .sort((a, b) => (a.id ?? 0) - (b.id ?? 0))

  const result: T[] = []
  let bi = 0
  for (const assignment of nonBlocked) {
    while (bi < blocked.length && (blocked[bi]!.id ?? 0) < (assignment.id ?? 0)) {
      result.push(blocked[bi++]!)
    }
    result.push(assignment)
  }
  while (bi < blocked.length) {
    result.push(blocked[bi++]!)
  }
  return result
}
