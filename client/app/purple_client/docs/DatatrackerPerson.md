
# DatatrackerPerson

Serializer a DatatrackerPerson, including all the bells and whistles

## Properties

Name | Type
------------ | -------------
`personId` | number
`name` | string
`email` | string
`picture` | string
`datatrackerUrl` | string
`rpcperson` | number

## Example

```typescript
import type { DatatrackerPerson } from ''

// TODO: Update the object below with actual values
const example = {
  "personId": null,
  "name": null,
  "email": null,
  "picture": null,
  "datatrackerUrl": null,
  "rpcperson": null,
} satisfies DatatrackerPerson

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as DatatrackerPerson
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


