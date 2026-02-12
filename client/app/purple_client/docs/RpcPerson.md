
# RpcPerson

Serialize an RpcPerson  To avoid datatracker API calls, use the `name_map` parameter to pass a dict mapping datatracker Person ID to name (designed for use with the `get_persons()` API endpoint).

## Properties

Name | Type
------------ | -------------
`id` | number
`name` | string
`hoursPerWeek` | number
`capabilities` | [Array&lt;Capability&gt;](Capability.md)
`roles` | [Array&lt;RpcRole&gt;](RpcRole.md)
`isActive` | boolean
`email` | string
`picture` | string
`datatrackerUrl` | string

## Example

```typescript
import type { RpcPerson } from ''

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "name": null,
  "hoursPerWeek": null,
  "capabilities": null,
  "roles": null,
  "isActive": null,
  "email": null,
  "picture": null,
  "datatrackerUrl": null,
} satisfies RpcPerson

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as RpcPerson
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


