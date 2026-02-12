
# RfcToBe

RfcToBeSerializer suitable for displaying full details of a single instance

## Properties

Name | Type
------------ | -------------
`id` | number
`name` | string
`title` | string
`_abstract` | string
`group` | string
`draft` | [Draft](Draft.md)
`disposition` | string
`externalDeadline` | Date
`internalGoal` | Date
`labels` | Array&lt;number&gt;
`cluster` | [SimpleCluster](SimpleCluster.md)
`submittedFormat` | string
`pages` | number
`keywords` | string
`boilerplate` | string
`stdLevel` | string
`publicationStdLevel` | string
`stream` | string
`publicationStream` | string
`authors` | [Array&lt;RfcAuthor&gt;](RfcAuthor.md)
`shepherd` | [BaseDatatrackerPerson](BaseDatatrackerPerson.md)
`iesgContact` | [BaseDatatrackerPerson](BaseDatatrackerPerson.md)
`assignmentSet` | [Array&lt;Assignment&gt;](Assignment.md)
`actionholderSet` | [Array&lt;ActionHolder&gt;](ActionHolder.md)
`pendingActivities` | [Array&lt;RpcRole&gt;](RpcRole.md)
`rfcNumber` | number
`publishedAt` | Date
`consensus` | boolean
`subseries` | [Array&lt;SubseriesMember&gt;](SubseriesMember.md)
`ianaStatus` | [IanaStatus](IanaStatus.md)

## Example

```typescript
import type { RfcToBe } from ''

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "name": null,
  "title": null,
  "_abstract": null,
  "group": null,
  "draft": null,
  "disposition": null,
  "externalDeadline": null,
  "internalGoal": null,
  "labels": null,
  "cluster": null,
  "submittedFormat": null,
  "pages": null,
  "keywords": null,
  "boilerplate": null,
  "stdLevel": null,
  "publicationStdLevel": null,
  "stream": null,
  "publicationStream": null,
  "authors": null,
  "shepherd": null,
  "iesgContact": null,
  "assignmentSet": null,
  "actionholderSet": null,
  "pendingActivities": null,
  "rfcNumber": null,
  "publishedAt": null,
  "consensus": null,
  "subseries": null,
  "ianaStatus": null,
} satisfies RfcToBe

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as RfcToBe
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


