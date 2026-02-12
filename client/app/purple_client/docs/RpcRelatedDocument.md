
# RpcRelatedDocument

Serializer for related document for an RfcToBe

## Properties

Name | Type
------------ | -------------
`id` | number
`relationship` | string
`draftName` | string
`targetDraftName` | string

## Example

```typescript
import type { RpcRelatedDocument } from ''

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "relationship": null,
  "draftName": null,
  "targetDraftName": null,
} satisfies RpcRelatedDocument

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as RpcRelatedDocument
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


