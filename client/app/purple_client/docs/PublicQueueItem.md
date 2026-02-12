
# PublicQueueItem

RfcToBe serializer for the public view of the RFC Editor queue

## Properties

Name | Type
------------ | -------------
`id` | number
`name` | string
`title` | string
`draftUrl` | string
`disposition` | string
`externalDeadline` | Date
`labels` | [Array&lt;Label&gt;](Label.md)
`cluster` | [SimpleCluster](SimpleCluster.md)
`assignmentSet` | [Array&lt;PublicAssignment&gt;](PublicAssignment.md)
`actionholderSet` | [Array&lt;ActionHolder&gt;](ActionHolder.md)
`pendingActivities` | [Array&lt;RpcRole&gt;](RpcRole.md)
`rfcNumber` | number
`pages` | number
`enqueuedAt` | Date
`finalApproval` | [Array&lt;FinalApproval&gt;](FinalApproval.md)
`ianaStatus` | [IanaStatus](IanaStatus.md)
`blockingReasons` | [Array&lt;RfcToBeBlockingReason&gt;](RfcToBeBlockingReason.md)
`authors` | [Array&lt;PublicQueueAuthor&gt;](PublicQueueAuthor.md)

## Example

```typescript
import type { PublicQueueItem } from ''

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "name": null,
  "title": null,
  "draftUrl": null,
  "disposition": null,
  "externalDeadline": null,
  "labels": null,
  "cluster": null,
  "assignmentSet": null,
  "actionholderSet": null,
  "pendingActivities": null,
  "rfcNumber": null,
  "pages": null,
  "enqueuedAt": null,
  "finalApproval": null,
  "ianaStatus": null,
  "blockingReasons": null,
  "authors": null,
} satisfies PublicQueueItem

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as PublicQueueItem
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


