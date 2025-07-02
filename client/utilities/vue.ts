/**
 * Vue's `class=""` attribute can take strings, arrays, objects, arrays of objects, etc
 * but the typing is just `any`. Use this instead for `class` props.
 *
 * Named VueStyleClass to distinguish from the word "class" used in the context of
 * `class` object-template-like programming.
 **/
export type VueStyleClass =
  | string
  | (string | boolean | undefined)[]
  | Record<string, boolean | undefined>
