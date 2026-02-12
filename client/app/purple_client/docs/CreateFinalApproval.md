
# CreateFinalApproval

Serializer for creating FinalApproval instances

## Properties

Name | Type
------------ | -------------
`id` | number
`rfcToBe` | [MinimalRfcToBe](MinimalRfcToBe.md)
`requested` | Date
`approver` | [BaseDatatrackerPerson](BaseDatatrackerPerson.md)
`approved` | Date
`overridingApprover` | [BaseDatatrackerPerson](BaseDatatrackerPerson.md)
`comment` | string

## Example

```typescript
import type { CreateFinalApproval } from ''

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "rfcToBe": null,
  "requested": null,
  "approver": null,
  "approved": null,
  "overridingApprover": null,
  "comment": null,
} satisfies CreateFinalApproval

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as CreateFinalApproval
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


