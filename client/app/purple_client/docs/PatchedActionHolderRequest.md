
# PatchedActionHolderRequest

Serialize an ActionHolder with person name

## Properties

Name | Type
------------ | -------------
`deadline` | Date
`completed` | Date
`comment` | string
`body` | string

## Example

```typescript
import type { PatchedActionHolderRequest } from ''

// TODO: Update the object below with actual values
const example = {
  "deadline": null,
  "completed": null,
  "comment": null,
  "body": null,
} satisfies PatchedActionHolderRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as PatchedActionHolderRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


