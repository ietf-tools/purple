
# CreateRfcToBeRequest

Serializer for RfcToBe fields that need to be specified explicitly on import

## Properties

Name | Type
------------ | -------------
`submittedFormat` | string
`boilerplate` | string
`stdLevel` | string
`stream` | string
`externalDeadline` | Date
`labels` | Array&lt;number&gt;
`draft` | number
`title` | string
`group` | string
`_abstract` | string
`shepherd` | number
`iesgContact` | number
`pages` | number
`keywords` | string
`ianaStatusSlug` | [IanaStatusSlugEnum](IanaStatusSlugEnum.md)
`consensus` | boolean

## Example

```typescript
import type { CreateRfcToBeRequest } from ''

// TODO: Update the object below with actual values
const example = {
  "submittedFormat": null,
  "boilerplate": null,
  "stdLevel": null,
  "stream": null,
  "externalDeadline": null,
  "labels": null,
  "draft": null,
  "title": null,
  "group": null,
  "_abstract": null,
  "shepherd": null,
  "iesgContact": null,
  "pages": null,
  "keywords": null,
  "ianaStatusSlug": null,
  "consensus": null,
} satisfies CreateRfcToBeRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as CreateRfcToBeRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


