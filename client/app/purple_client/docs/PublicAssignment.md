
# PublicAssignment

Assignment serializer for the public queue view

## Properties

Name | Type
------------ | -------------
`id` | number
`rfcToBe` | number
`role` | string
`state` | [StateEnum](StateEnum.md)

## Example

```typescript
import type { PublicAssignment } from ''

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "rfcToBe": null,
  "role": null,
  "state": null,
} satisfies PublicAssignment

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as PublicAssignment
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


