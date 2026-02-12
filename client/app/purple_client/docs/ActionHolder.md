
# ActionHolder

Serialize an ActionHolder with person name

## Properties

Name | Type
------------ | -------------
`id` | number
`name` | string
`deadline` | Date
`sinceWhen` | Date
`completed` | Date
`comment` | string
`body` | string

## Example

```typescript
import type { ActionHolder } from ''

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "name": null,
  "deadline": null,
  "sinceWhen": null,
  "completed": null,
  "comment": null,
  "body": null,
} satisfies ActionHolder

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ActionHolder
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


