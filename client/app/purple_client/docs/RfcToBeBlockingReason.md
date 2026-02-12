
# RfcToBeBlockingReason

Serialize RfcToBeBlockingReason with reason details

## Properties

Name | Type
------------ | -------------
`reason` | [BlockingReason](BlockingReason.md)
`sinceWhen` | Date
`resolved` | Date

## Example

```typescript
import type { RfcToBeBlockingReason } from ''

// TODO: Update the object below with actual values
const example = {
  "reason": null,
  "sinceWhen": null,
  "resolved": null,
} satisfies RfcToBeBlockingReason

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as RfcToBeBlockingReason
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


