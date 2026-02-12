
# Draft


## Properties

Name | Type
------------ | -------------
`name` | string
`rev` | string
`title` | string
`pages` | number

## Example

```typescript
import type { Draft } from ''

// TODO: Update the object below with actual values
const example = {
  "name": null,
  "rev": null,
  "title": null,
  "pages": null,
} satisfies Draft

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as Draft
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


