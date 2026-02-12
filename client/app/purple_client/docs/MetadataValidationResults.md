
# MetadataValidationResults


## Properties

Name | Type
------------ | -------------
`rfcToBe` | number
`repository` | string
`headSha` | string
`canAutofix` | boolean
`isMatch` | boolean
`metadataCompare` | [Array&lt;MetadataTableRow&gt;](MetadataTableRow.md)
`status` | string
`detail` | string
`isError` | boolean
`receivedAt` | Date

## Example

```typescript
import type { MetadataValidationResults } from ''

// TODO: Update the object below with actual values
const example = {
  "rfcToBe": null,
  "repository": null,
  "headSha": null,
  "canAutofix": null,
  "isMatch": null,
  "metadataCompare": null,
  "status": null,
  "detail": null,
  "isError": null,
  "receivedAt": null,
} satisfies MetadataValidationResults

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as MetadataValidationResults
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


