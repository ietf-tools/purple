
# SubseriesMemberRequest

Serialize a SubseriesMember

## Properties

Name | Type
------------ | -------------
`rfcToBe` | number
`type` | string
`number` | number

## Example

```typescript
import type { SubseriesMemberRequest } from ''

// TODO: Update the object below with actual values
const example = {
  "rfcToBe": null,
  "type": null,
  "number": null,
} satisfies SubseriesMemberRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SubseriesMemberRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


