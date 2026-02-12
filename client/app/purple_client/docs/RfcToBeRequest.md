
# RfcToBeRequest

RfcToBeSerializer suitable for displaying full details of a single instance

## Properties

Name | Type
------------ | -------------
`title` | string
`_abstract` | string
`group` | string
`disposition` | string
`externalDeadline` | Date
`internalGoal` | Date
`labels` | Array&lt;number&gt;
`submittedFormat` | string
`pages` | number
`keywords` | string
`boilerplate` | string
`stdLevel` | string
`publicationStdLevel` | string
`stream` | string
`publicationStream` | string
`authors` | [Array&lt;RfcAuthorRequest&gt;](RfcAuthorRequest.md)
`rfcNumber` | number
`consensus` | boolean
`ianaStatusSlug` | [IanaStatusSlugEnum](IanaStatusSlugEnum.md)

## Example

```typescript
import type { RfcToBeRequest } from ''

// TODO: Update the object below with actual values
const example = {
  "title": null,
  "_abstract": null,
  "group": null,
  "disposition": null,
  "externalDeadline": null,
  "internalGoal": null,
  "labels": null,
  "submittedFormat": null,
  "pages": null,
  "keywords": null,
  "boilerplate": null,
  "stdLevel": null,
  "publicationStdLevel": null,
  "stream": null,
  "publicationStream": null,
  "authors": null,
  "rfcNumber": null,
  "consensus": null,
  "ianaStatusSlug": null,
} satisfies RfcToBeRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as RfcToBeRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


