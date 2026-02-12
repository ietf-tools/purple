
# MetadataTableRow


## Properties

Name | Type
------------ | -------------
`rowName` | string
`rowNameListDepth` | number
`rowValue` | [MetadataTableRowValue](MetadataTableRowValue.md)

## Example

```typescript
import type { MetadataTableRow } from ''

// TODO: Update the object below with actual values
const example = {
  "rowName": null,
  "rowNameListDepth": null,
  "rowValue": null,
} satisfies MetadataTableRow

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as MetadataTableRow
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


