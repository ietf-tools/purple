
# IanaStatus

Serialize IANA status with slug and display text

## Properties

Name | Type
------------ | -------------
`slug` | string
`name` | string
`desc` | string
`used` | boolean

## Example

```typescript
import type { IanaStatus } from ''

// TODO: Update the object below with actual values
const example = {
  "slug": null,
  "name": null,
  "desc": null,
  "used": null,
} satisfies IanaStatus

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as IanaStatus
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


