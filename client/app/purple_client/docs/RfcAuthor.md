
# RfcAuthor


## Properties

Name | Type
------------ | -------------
`id` | number
`name` | string
`email` | string
`titlepageName` | string
`isEditor` | boolean
`picture` | string
`datatrackerUrl` | string
`affiliation` | string

## Example

```typescript
import type { RfcAuthor } from ''

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "name": null,
  "email": null,
  "titlepageName": null,
  "isEditor": null,
  "picture": null,
  "datatrackerUrl": null,
  "affiliation": null,
} satisfies RfcAuthor

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as RfcAuthor
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


