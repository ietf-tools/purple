
# VersionInfo

Serialize version information

## Properties

Name | Type
------------ | -------------
`version` | string
`dumpTimestamp` | Date

## Example

```typescript
import type { VersionInfo } from ''

// TODO: Update the object below with actual values
const example = {
  "version": null,
  "dumpTimestamp": null,
} satisfies VersionInfo

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as VersionInfo
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


