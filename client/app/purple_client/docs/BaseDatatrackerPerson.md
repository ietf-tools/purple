
# BaseDatatrackerPerson

Serialize a minimal DatatrackerPerson  This is the serializer to use if you may be working with non-persisted DatatrackerPerson instances.

## Properties

Name | Type
------------ | -------------
`personId` | number
`name` | string
`email` | string
`picture` | string
`datatrackerUrl` | string

## Example

```typescript
import type { BaseDatatrackerPerson } from ''

// TODO: Update the object below with actual values
const example = {
  "personId": null,
  "name": null,
  "email": null,
  "picture": null,
  "datatrackerUrl": null,
} satisfies BaseDatatrackerPerson

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as BaseDatatrackerPerson
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


