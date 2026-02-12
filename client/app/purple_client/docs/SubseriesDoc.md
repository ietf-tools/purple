
# SubseriesDoc


## Properties

Name | Type
------------ | -------------
`type` | string
`number` | number
`documents` | [Array&lt;MinimalRfcToBe&gt;](MinimalRfcToBe.md)
`rfcCount` | number
`slug` | string
`displayName` | string

## Example

```typescript
import type { SubseriesDoc } from ''

// TODO: Update the object below with actual values
const example = {
  "type": null,
  "number": null,
  "documents": null,
  "rfcCount": null,
  "slug": null,
  "displayName": null,
} satisfies SubseriesDoc

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SubseriesDoc
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


