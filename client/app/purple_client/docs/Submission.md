
# Submission

Serialize a submission

## Properties

Name | Type
------------ | -------------
`id` | number
`name` | string
`rev` | string
`stream` | [Name](Name.md)
`title` | string
`pages` | number
`sourceFormat` | [Name](Name.md)
`authors` | [Array&lt;SubmissionAuthor&gt;](SubmissionAuthor.md)
`shepherd` | string
`stdLevel` | [Name](Name.md)
`datatrackerUrl` | string
`consensus` | boolean

## Example

```typescript
import type { Submission } from ''

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "name": null,
  "rev": null,
  "stream": null,
  "title": null,
  "pages": null,
  "sourceFormat": null,
  "authors": null,
  "shepherd": null,
  "stdLevel": null,
  "datatrackerUrl": null,
  "consensus": null,
} satisfies Submission

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as Submission
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


