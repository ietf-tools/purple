
# CreateRpcRelatedDocumentRequest

Serializer for creating a related document for an RfcToBe

## Properties

Name | Type
------------ | -------------
`relationship` | string
`source` | number
`targetDraftName` | string

## Example

```typescript
import type { CreateRpcRelatedDocumentRequest } from ''

// TODO: Update the object below with actual values
const example = {
  "relationship": null,
  "source": null,
  "targetDraftName": null,
} satisfies CreateRpcRelatedDocumentRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as CreateRpcRelatedDocumentRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


