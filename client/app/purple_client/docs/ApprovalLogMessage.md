
# ApprovalLogMessage


## Properties

Name | Type
------------ | -------------
`id` | number
`by` | [DatatrackerPerson](DatatrackerPerson.md)
`rfcToBe` | [MinimalRfcToBe](MinimalRfcToBe.md)
`logMessage` | string
`time` | Date

## Example

```typescript
import type { ApprovalLogMessage } from ''

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "by": null,
  "rfcToBe": null,
  "logMessage": null,
  "time": null,
} satisfies ApprovalLogMessage

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ApprovalLogMessage
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


