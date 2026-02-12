
# LabelRequest


## Properties

Name | Type
------------ | -------------
`slug` | string
`isException` | boolean
`isComplexity` | boolean
`color` | [ColorEnum](ColorEnum.md)
`used` | boolean

## Example

```typescript
import type { LabelRequest } from ''

// TODO: Update the object below with actual values
const example = {
  "slug": null,
  "isException": null,
  "isComplexity": null,
  "color": null,
  "used": null,
} satisfies LabelRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as LabelRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


