
# ClusterRequest

Serialize a Cluster instance  Uses a nested representation for `documents` rather than the ModelSerializer\'s handling of relations so we can work with the through model. Specifically, we want to respect the `order_by` setting of the `ClusterMember` class.

## Properties

Name | Type
------------ | -------------
`number` | number
`draftNames` | Array&lt;string&gt;

## Example

```typescript
import type { ClusterRequest } from ''

// TODO: Update the object below with actual values
const example = {
  "number": null,
  "draftNames": null,
} satisfies ClusterRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ClusterRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


