
# Profile


## Properties

Name | Type
------------ | -------------
`authenticated` | boolean
`id` | number
`name` | string
`avatar` | string
`rpcPersonId` | number
`isManager` | boolean

## Example

```typescript
import type { Profile } from ''

// TODO: Update the object below with actual values
const example = {
  "authenticated": null,
  "id": null,
  "name": null,
  "avatar": null,
  "rpcPersonId": null,
  "isManager": null,
} satisfies Profile

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as Profile
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


