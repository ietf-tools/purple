export const deepSortObject = <T>(value: T): T => {
  if (!value || typeof value !== "object") {
    return value;
  }

  if (Array.isArray(value)) {
    return value.map(deepSortObject) as T;
  }

  if (value instanceof Map) {
    return new Map(
      [...value.entries()]
        .sort(([a], [b]) => String(a).localeCompare(String(b)))
        .map(([k, v]) => [k, deepSortObject(v)])
    ) as T;
  }

  if (value instanceof Set) {
    return new Set([...value].sort((a, b) => String(a).localeCompare(String(b)))) as T;
  }

  const plainObject = value as Record<string, unknown>;
  const sortedKeys = Object.keys(plainObject).sort((a, b) =>
    a.localeCompare(b, undefined, { sensitivity: "base" })
  );

  const result: Record<string, unknown> = {};
  for (const key of sortedKeys) {
    result[key] = deepSortObject(plainObject[key]);
  }
  return result as T;
}
