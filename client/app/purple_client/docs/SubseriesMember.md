
# SubseriesMember

Serialize a SubseriesMember

## Properties

Name | Type
------------ | -------------
`id` | number
`rfcToBe` | number
`type` | string
`number` | number
`displayName` | string
`slug` | string

## Example

```typescript
import type { SubseriesMember } from ''

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "rfcToBe": null,
  "type": null,
  "number": null,
  "displayName": null,
  "slug": null,
} satisfies SubseriesMember

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SubseriesMember
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


