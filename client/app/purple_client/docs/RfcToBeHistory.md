
# RfcToBeHistory

Serialize a HistoricalRecord

## Properties

Name | Type
------------ | -------------
`id` | number
`time` | Date
`by` | [DatatrackerPerson](DatatrackerPerson.md)
`desc` | string

## Example

```typescript
import type { RfcToBeHistory } from ''

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "time": null,
  "by": null,
  "desc": null,
} satisfies RfcToBeHistory

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as RfcToBeHistory
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


