
# ClusterMember


## Properties

Name | Type
------------ | -------------
`name` | string
`rfcNumber` | number
`disposition` | string
`references` | [Array&lt;RpcRelatedDocument&gt;](RpcRelatedDocument.md)
`isReceived` | boolean
`order` | number

## Example

```typescript
import type { ClusterMember } from ''

// TODO: Update the object below with actual values
const example = {
  "name": null,
  "rfcNumber": null,
  "disposition": null,
  "references": null,
  "isReceived": null,
  "order": null,
} satisfies ClusterMember

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ClusterMember
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


