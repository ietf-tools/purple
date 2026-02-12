
# NestedAssignment

Assignment serializer with nested RfcToBe details

## Properties

Name | Type
------------ | -------------
`id` | number
`rfcToBe` | [RfcToBe](RfcToBe.md)
`person` | number
`role` | string
`state` | [StateEnum](StateEnum.md)
`comment` | string
`timeSpent` | string

## Example

```typescript
import type { NestedAssignment } from ''

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "rfcToBe": null,
  "person": null,
  "role": null,
  "state": null,
  "comment": null,
  "timeSpent": null,
} satisfies NestedAssignment

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as NestedAssignment
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


