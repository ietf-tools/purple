
# MailMessageRequest

Mail message serializer

## Properties

Name | Type
------------ | -------------
`msgtype` | [MsgtypeEnum](MsgtypeEnum.md)
`to` | string
`cc` | string
`subject` | string
`body` | string

## Example

```typescript
import type { MailMessageRequest } from ''

// TODO: Update the object below with actual values
const example = {
  "msgtype": null,
  "to": null,
  "cc": null,
  "subject": null,
  "body": null,
} satisfies MailMessageRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as MailMessageRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


