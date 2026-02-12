# PurpleApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**apiPubqClustersList**](PurpleApi.md#apipubqclusterslist) | **GET** /api/pubq/clusters/ |  |
| [**apiPubqClustersRetrieve**](PurpleApi.md#apipubqclustersretrieve) | **GET** /api/pubq/clusters/{number}/ |  |
| [**apiPubqQueueList**](PurpleApi.md#apipubqqueuelist) | **GET** /api/pubq/queue/ |  |
| [**assignmentsCreate**](PurpleApi.md#assignmentscreate) | **POST** /api/rpc/assignments/ |  |
| [**assignmentsDestroy**](PurpleApi.md#assignmentsdestroy) | **DELETE** /api/rpc/assignments/{id}/ |  |
| [**assignmentsList**](PurpleApi.md#assignmentslist) | **GET** /api/rpc/assignments/ |  |
| [**assignmentsPartialUpdate**](PurpleApi.md#assignmentspartialupdate) | **PATCH** /api/rpc/assignments/{id}/ |  |
| [**assignmentsRetrieve**](PurpleApi.md#assignmentsretrieve) | **GET** /api/rpc/assignments/{id}/ |  |
| [**assignmentsUpdate**](PurpleApi.md#assignmentsupdate) | **PUT** /api/rpc/assignments/{id}/ |  |
| [**capabilitiesList**](PurpleApi.md#capabilitieslist) | **GET** /api/rpc/capabilities/ |  |
| [**capabilitiesRetrieve**](PurpleApi.md#capabilitiesretrieve) | **GET** /api/rpc/capabilities/{slug}/ |  |
| [**clustersAddDocument**](PurpleApi.md#clustersadddocument) | **POST** /api/rpc/clusters/{number}/add-document/ |  |
| [**clustersCreate**](PurpleApi.md#clusterscreate) | **POST** /api/rpc/clusters/ |  |
| [**clustersList**](PurpleApi.md#clusterslist) | **GET** /api/rpc/clusters/ |  |
| [**clustersPartialUpdate**](PurpleApi.md#clusterspartialupdate) | **PATCH** /api/rpc/clusters/{number}/ |  |
| [**clustersRemoveDocument**](PurpleApi.md#clustersremovedocument) | **POST** /api/rpc/clusters/{number}/remove-document/ |  |
| [**clustersReorderDocuments**](PurpleApi.md#clustersreorderdocuments) | **POST** /api/rpc/clusters/{number}/order/ |  |
| [**clustersRetrieve**](PurpleApi.md#clustersretrieve) | **GET** /api/rpc/clusters/{number}/ |  |
| [**clustersUpdate**](PurpleApi.md#clustersupdate) | **PUT** /api/rpc/clusters/{number}/ |  |
| [**docRelationshipNamesList**](PurpleApi.md#docrelationshipnameslist) | **GET** /api/rpc/doc_relationship_names/ |  |
| [**docRelationshipNamesRetrieve**](PurpleApi.md#docrelationshipnamesretrieve) | **GET** /api/rpc/doc_relationship_names/{slug}/ |  |
| [**documentMailSend**](PurpleApi.md#documentmailsend) | **POST** /api/rpc/documents/{draft_name}/mail |  |
| [**documentsActionHoldersList**](PurpleApi.md#documentsactionholderslist) | **GET** /api/rpc/documents/{draft_name}/action_holders/ |  |
| [**documentsActionHoldersPartialUpdate**](PurpleApi.md#documentsactionholderspartialupdate) | **PATCH** /api/rpc/documents/{draft_name}/action_holders/{id}/ |  |
| [**documentsActionHoldersRetrieve**](PurpleApi.md#documentsactionholdersretrieve) | **GET** /api/rpc/documents/{draft_name}/action_holders/{id}/ |  |
| [**documentsActionHoldersUpdate**](PurpleApi.md#documentsactionholdersupdate) | **PUT** /api/rpc/documents/{draft_name}/action_holders/{id}/ |  |
| [**documentsApprovalLogsCreate**](PurpleApi.md#documentsapprovallogscreate) | **POST** /api/rpc/documents/{draft_name}/approval_logs/ |  |
| [**documentsApprovalLogsDestroy**](PurpleApi.md#documentsapprovallogsdestroy) | **DELETE** /api/rpc/documents/{draft_name}/approval_logs/{id}/ |  |
| [**documentsApprovalLogsList**](PurpleApi.md#documentsapprovallogslist) | **GET** /api/rpc/documents/{draft_name}/approval_logs/ |  |
| [**documentsApprovalLogsPartialUpdate**](PurpleApi.md#documentsapprovallogspartialupdate) | **PATCH** /api/rpc/documents/{draft_name}/approval_logs/{id}/ |  |
| [**documentsApprovalLogsRetrieve**](PurpleApi.md#documentsapprovallogsretrieve) | **GET** /api/rpc/documents/{draft_name}/approval_logs/{id}/ |  |
| [**documentsApprovalLogsUpdate**](PurpleApi.md#documentsapprovallogsupdate) | **PUT** /api/rpc/documents/{draft_name}/approval_logs/{id}/ |  |
| [**documentsAuthorsCreate**](PurpleApi.md#documentsauthorscreate) | **POST** /api/rpc/documents/{draft_name}/authors/ |  |
| [**documentsAuthorsDestroy**](PurpleApi.md#documentsauthorsdestroy) | **DELETE** /api/rpc/documents/{draft_name}/authors/{id}/ |  |
| [**documentsAuthorsList**](PurpleApi.md#documentsauthorslist) | **GET** /api/rpc/documents/{draft_name}/authors/ |  |
| [**documentsAuthorsOrder**](PurpleApi.md#documentsauthorsorder) | **POST** /api/rpc/documents/{draft_name}/authors/order/ |  |
| [**documentsAuthorsPartialUpdate**](PurpleApi.md#documentsauthorspartialupdate) | **PATCH** /api/rpc/documents/{draft_name}/authors/{id}/ |  |
| [**documentsAuthorsRetrieve**](PurpleApi.md#documentsauthorsretrieve) | **GET** /api/rpc/documents/{draft_name}/authors/{id}/ |  |
| [**documentsAuthorsUpdate**](PurpleApi.md#documentsauthorsupdate) | **PUT** /api/rpc/documents/{draft_name}/authors/{id}/ |  |
| [**documentsCommentsCreate**](PurpleApi.md#documentscommentscreate) | **POST** /api/rpc/documents/{draft_name}/comments/ |  |
| [**documentsCommentsList**](PurpleApi.md#documentscommentslist) | **GET** /api/rpc/documents/{draft_name}/comments/ |  |
| [**documentsCommentsPartialUpdate**](PurpleApi.md#documentscommentspartialupdate) | **PATCH** /api/rpc/documents/{draft_name}/comments/{id}/ |  |
| [**documentsCommentsUpdate**](PurpleApi.md#documentscommentsupdate) | **PUT** /api/rpc/documents/{draft_name}/comments/{id}/ |  |
| [**documentsCreate**](PurpleApi.md#documentscreate) | **POST** /api/rpc/documents/ |  |
| [**documentsDestroy**](PurpleApi.md#documentsdestroy) | **DELETE** /api/rpc/documents/{draft__name}/ |  |
| [**documentsFinalApprovalsCreate**](PurpleApi.md#documentsfinalapprovalscreate) | **POST** /api/rpc/documents/{draft_name}/final_approvals/ |  |
| [**documentsFinalApprovalsDestroy**](PurpleApi.md#documentsfinalapprovalsdestroy) | **DELETE** /api/rpc/documents/{draft_name}/final_approvals/{id}/ |  |
| [**documentsFinalApprovalsList**](PurpleApi.md#documentsfinalapprovalslist) | **GET** /api/rpc/documents/{draft_name}/final_approvals/ |  |
| [**documentsFinalApprovalsPartialUpdate**](PurpleApi.md#documentsfinalapprovalspartialupdate) | **PATCH** /api/rpc/documents/{draft_name}/final_approvals/{id}/ |  |
| [**documentsFinalApprovalsRetrieve**](PurpleApi.md#documentsfinalapprovalsretrieve) | **GET** /api/rpc/documents/{draft_name}/final_approvals/{id}/ |  |
| [**documentsFinalApprovalsUpdate**](PurpleApi.md#documentsfinalapprovalsupdate) | **PUT** /api/rpc/documents/{draft_name}/final_approvals/{id}/ |  |
| [**documentsHistoryList**](PurpleApi.md#documentshistorylist) | **GET** /api/rpc/documents/{draft__name}/history/ |  |
| [**documentsList**](PurpleApi.md#documentslist) | **GET** /api/rpc/documents/ |  |
| [**documentsMetadataValidationResultsDestroy**](PurpleApi.md#documentsmetadatavalidationresultsdestroy) | **DELETE** /api/rpc/documents/{draft_name}/metadata_validation_results/{head_sha}/ |  |
| [**documentsMetadataValidationResultsList**](PurpleApi.md#documentsmetadatavalidationresultslist) | **GET** /api/rpc/documents/{draft_name}/metadata_validation_results/ |  |
| [**documentsMetadataValidationResultsRetrieve**](PurpleApi.md#documentsmetadatavalidationresultsretrieve) | **GET** /api/rpc/documents/{draft_name}/metadata_validation_results/{head_sha}/ |  |
| [**documentsPartialUpdate**](PurpleApi.md#documentspartialupdate) | **PATCH** /api/rpc/documents/{draft__name}/ |  |
| [**documentsPublish**](PurpleApi.md#documentspublish) | **POST** /api/rpc/documents/{draft__name}/publish/ |  |
| [**documentsReferencesCreate**](PurpleApi.md#documentsreferencescreate) | **POST** /api/rpc/documents/{draft_name}/references/ |  |
| [**documentsReferencesDestroy**](PurpleApi.md#documentsreferencesdestroy) | **DELETE** /api/rpc/documents/{draft_name}/references/{id}/ |  |
| [**documentsReferencesList**](PurpleApi.md#documentsreferenceslist) | **GET** /api/rpc/documents/{draft_name}/references/ |  |
| [**documentsReferencesPartialUpdate**](PurpleApi.md#documentsreferencespartialupdate) | **PATCH** /api/rpc/documents/{draft_name}/references/{id}/ |  |
| [**documentsReferencesRetrieve**](PurpleApi.md#documentsreferencesretrieve) | **GET** /api/rpc/documents/{draft_name}/references/{id}/ |  |
| [**documentsReferencesUpdate**](PurpleApi.md#documentsreferencesupdate) | **PUT** /api/rpc/documents/{draft_name}/references/{id}/ |  |
| [**documentsRetrieve**](PurpleApi.md#documentsretrieve) | **GET** /api/rpc/documents/{draft__name}/ |  |
| [**documentsUpdate**](PurpleApi.md#documentsupdate) | **PUT** /api/rpc/documents/{draft__name}/ |  |
| [**labelsCreate**](PurpleApi.md#labelscreate) | **POST** /api/rpc/labels/ |  |
| [**labelsDestroy**](PurpleApi.md#labelsdestroy) | **DELETE** /api/rpc/labels/{id}/ |  |
| [**labelsList**](PurpleApi.md#labelslist) | **GET** /api/rpc/labels/ |  |
| [**labelsPartialUpdate**](PurpleApi.md#labelspartialupdate) | **PATCH** /api/rpc/labels/{id}/ |  |
| [**labelsRetrieve**](PurpleApi.md#labelsretrieve) | **GET** /api/rpc/labels/{id}/ |  |
| [**labelsUpdate**](PurpleApi.md#labelsupdate) | **PUT** /api/rpc/labels/{id}/ |  |
| [**mailSend**](PurpleApi.md#mailsend) | **POST** /api/rpc/mail |  |
| [**mailtemplateList**](PurpleApi.md#mailtemplatelist) | **GET** /api/rpc/mailtemplate/{rfctobe_id}/ |  |
| [**metadataValidationResultsCreate**](PurpleApi.md#metadatavalidationresultscreate) | **POST** /api/rpc/documents/{draft_name}/metadata_validation_results/ |  |
| [**metadataValidationResultsSync**](PurpleApi.md#metadatavalidationresultssync) | **POST** /api/rpc/documents/{draft_name}/metadata_validation_results/sync/ |  |
| [**profile**](PurpleApi.md#profile) | **GET** /api/rpc/profile/ |  |
| [**profileRetrieveDemoOnly**](PurpleApi.md#profileretrievedemoonly) | **GET** /api/rpc/profile/{rpc_person_id} |  |
| [**queueList**](PurpleApi.md#queuelist) | **GET** /api/rpc/queue/ |  |
| [**rpcPersonAssignmentsList**](PurpleApi.md#rpcpersonassignmentslist) | **GET** /api/rpc/rpc_person/{person_id}/assignments/ |  |
| [**rpcPersonList**](PurpleApi.md#rpcpersonlist) | **GET** /api/rpc/rpc_person/ |  |
| [**rpcPersonRetrieve**](PurpleApi.md#rpcpersonretrieve) | **GET** /api/rpc/rpc_person/{id}/ |  |
| [**rpcRolesList**](PurpleApi.md#rpcroleslist) | **GET** /api/rpc/rpc_roles/ |  |
| [**rpcRolesRetrieve**](PurpleApi.md#rpcrolesretrieve) | **GET** /api/rpc/rpc_roles/{slug}/ |  |
| [**searchDatatrackerpersons**](PurpleApi.md#searchdatatrackerpersons) | **GET** /api/rpc/search/datatrackerpersons/ |  |
| [**sourceFormatNamesList**](PurpleApi.md#sourceformatnameslist) | **GET** /api/rpc/source_format_names/ |  |
| [**sourceFormatNamesRetrieve**](PurpleApi.md#sourceformatnamesretrieve) | **GET** /api/rpc/source_format_names/{slug}/ |  |
| [**statsLabels**](PurpleApi.md#statslabels) | **GET** /api/rpc/stats/label/ |  |
| [**stdLevelNamesList**](PurpleApi.md#stdlevelnameslist) | **GET** /api/rpc/std_level_names/ |  |
| [**stdLevelNamesRetrieve**](PurpleApi.md#stdlevelnamesretrieve) | **GET** /api/rpc/std_level_names/{slug}/ |  |
| [**streamNamesList**](PurpleApi.md#streamnameslist) | **GET** /api/rpc/stream_names/ |  |
| [**streamNamesRetrieve**](PurpleApi.md#streamnamesretrieve) | **GET** /api/rpc/stream_names/{slug}/ |  |
| [**submissionsImport**](PurpleApi.md#submissionsimport) | **POST** /api/rpc/submissions/{document_id}/import/ |  |
| [**submissionsList**](PurpleApi.md#submissionslist) | **GET** /api/rpc/submissions/ |  |
| [**submissionsRetrieve**](PurpleApi.md#submissionsretrieve) | **GET** /api/rpc/submissions/{document_id}/ |  |
| [**subseriesList**](PurpleApi.md#subserieslist) | **GET** /api/rpc/subseries/ |  |
| [**subseriesMembersCreate**](PurpleApi.md#subseriesmemberscreate) | **POST** /api/rpc/subseries_members/ |  |
| [**subseriesMembersDestroy**](PurpleApi.md#subseriesmembersdestroy) | **DELETE** /api/rpc/subseries_members/{id}/ |  |
| [**subseriesMembersList**](PurpleApi.md#subseriesmemberslist) | **GET** /api/rpc/subseries_members/ |  |
| [**subseriesMembersPartialUpdate**](PurpleApi.md#subseriesmemberspartialupdate) | **PATCH** /api/rpc/subseries_members/{id}/ |  |
| [**subseriesMembersRetrieve**](PurpleApi.md#subseriesmembersretrieve) | **GET** /api/rpc/subseries_members/{id}/ |  |
| [**subseriesRetrieve**](PurpleApi.md#subseriesretrieve) | **GET** /api/rpc/subseries/{subseries_slug}/ |  |
| [**subseriesTypesList**](PurpleApi.md#subseriestypeslist) | **GET** /api/rpc/subseries_types/ |  |
| [**subseriesTypesRetrieve**](PurpleApi.md#subseriestypesretrieve) | **GET** /api/rpc/subseries_types/{slug}/ |  |
| [**tlpBoilerplateChoiceNamesList**](PurpleApi.md#tlpboilerplatechoicenameslist) | **GET** /api/rpc/tlp_boilerplate_choice_names/ |  |
| [**tlpBoilerplateChoiceNamesRetrieve**](PurpleApi.md#tlpboilerplatechoicenamesretrieve) | **GET** /api/rpc/tlp_boilerplate_choice_names/{slug}/ |  |
| [**unusableRfcNumbersCreate**](PurpleApi.md#unusablerfcnumberscreate) | **POST** /api/rpc/unusable_rfc_numbers/ |  |
| [**unusableRfcNumbersDestroy**](PurpleApi.md#unusablerfcnumbersdestroy) | **DELETE** /api/rpc/unusable_rfc_numbers/{number}/ |  |
| [**unusableRfcNumbersList**](PurpleApi.md#unusablerfcnumberslist) | **GET** /api/rpc/unusable_rfc_numbers/ |  |
| [**unusableRfcNumbersPartialUpdate**](PurpleApi.md#unusablerfcnumberspartialupdate) | **PATCH** /api/rpc/unusable_rfc_numbers/{number}/ |  |
| [**unusableRfcNumbersRetrieve**](PurpleApi.md#unusablerfcnumbersretrieve) | **GET** /api/rpc/unusable_rfc_numbers/{number}/ |  |
| [**version**](PurpleApi.md#version) | **GET** /api/rpc/version/ |  |



## apiPubqClustersList

> Array&lt;Cluster&gt; apiPubqClustersList()



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { ApiPubqClustersListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  try {
    const data = await api.apiPubqClustersList();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**Array&lt;Cluster&gt;**](Cluster.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiPubqClustersRetrieve

> Cluster apiPubqClustersRetrieve(number)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { ApiPubqClustersRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number
    number: 56,
  } satisfies ApiPubqClustersRetrieveRequest;

  try {
    const data = await api.apiPubqClustersRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **number** | `number` |  | [Defaults to `undefined`] |

### Return type

[**Cluster**](Cluster.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiPubqQueueList

> Array&lt;PublicQueueItem&gt; apiPubqQueueList(disposition, pendingFinalApproval)



Queue view for the public queue site

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { ApiPubqQueueListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string (optional)
    disposition: disposition_example,
    // boolean | Filter by pending final approval status, true returns drafts with at least one pending final approval, false returns drafts where all final approvals are approved. (optional)
    pendingFinalApproval: true,
  } satisfies ApiPubqQueueListRequest;

  try {
    const data = await api.apiPubqQueueList(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **disposition** | `string` |  | [Optional] [Defaults to `undefined`] |
| **pendingFinalApproval** | `boolean` | Filter by pending final approval status, true returns drafts with at least one pending final approval, false returns drafts where all final approvals are approved. | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;PublicQueueItem&gt;**](PublicQueueItem.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## assignmentsCreate

> Assignment assignmentsCreate(assignmentRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { AssignmentsCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // AssignmentRequest
    assignmentRequest: ...,
  } satisfies AssignmentsCreateRequest;

  try {
    const data = await api.assignmentsCreate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **assignmentRequest** | [AssignmentRequest](AssignmentRequest.md) |  | |

### Return type

[**Assignment**](Assignment.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## assignmentsDestroy

> assignmentsDestroy(id)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { AssignmentsDestroyRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number | A unique integer value identifying this assignment.
    id: 56,
  } satisfies AssignmentsDestroyRequest;

  try {
    const data = await api.assignmentsDestroy(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **id** | `number` | A unique integer value identifying this assignment. | [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | No response body |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## assignmentsList

> Array&lt;Assignment&gt; assignmentsList(ordering)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { AssignmentsListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string | Which field to use when ordering the results. (optional)
    ordering: ordering_example,
  } satisfies AssignmentsListRequest;

  try {
    const data = await api.assignmentsList(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **ordering** | `string` | Which field to use when ordering the results. | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;Assignment&gt;**](Assignment.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## assignmentsPartialUpdate

> Assignment assignmentsPartialUpdate(id, patchedAssignmentRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { AssignmentsPartialUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number | A unique integer value identifying this assignment.
    id: 56,
    // PatchedAssignmentRequest (optional)
    patchedAssignmentRequest: ...,
  } satisfies AssignmentsPartialUpdateRequest;

  try {
    const data = await api.assignmentsPartialUpdate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **id** | `number` | A unique integer value identifying this assignment. | [Defaults to `undefined`] |
| **patchedAssignmentRequest** | [PatchedAssignmentRequest](PatchedAssignmentRequest.md) |  | [Optional] |

### Return type

[**Assignment**](Assignment.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## assignmentsRetrieve

> Assignment assignmentsRetrieve(id)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { AssignmentsRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number | A unique integer value identifying this assignment.
    id: 56,
  } satisfies AssignmentsRetrieveRequest;

  try {
    const data = await api.assignmentsRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **id** | `number` | A unique integer value identifying this assignment. | [Defaults to `undefined`] |

### Return type

[**Assignment**](Assignment.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## assignmentsUpdate

> Assignment assignmentsUpdate(id, assignmentRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { AssignmentsUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number | A unique integer value identifying this assignment.
    id: 56,
    // AssignmentRequest
    assignmentRequest: ...,
  } satisfies AssignmentsUpdateRequest;

  try {
    const data = await api.assignmentsUpdate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **id** | `number` | A unique integer value identifying this assignment. | [Defaults to `undefined`] |
| **assignmentRequest** | [AssignmentRequest](AssignmentRequest.md) |  | |

### Return type

[**Assignment**](Assignment.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## capabilitiesList

> Array&lt;Capability&gt; capabilitiesList()



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { CapabilitiesListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  try {
    const data = await api.capabilitiesList();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**Array&lt;Capability&gt;**](Capability.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## capabilitiesRetrieve

> Capability capabilitiesRetrieve(slug)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { CapabilitiesRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string | A unique value identifying this capability.
    slug: slug_example,
  } satisfies CapabilitiesRetrieveRequest;

  try {
    const data = await api.capabilitiesRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **slug** | `string` | A unique value identifying this capability. | [Defaults to `undefined`] |

### Return type

[**Capability**](Capability.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## clustersAddDocument

> Cluster clustersAddDocument(number, clusterAddRemoveDocumentRequest)



Add a document to a cluster

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { ClustersAddDocumentRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number
    number: 56,
    // ClusterAddRemoveDocumentRequest
    clusterAddRemoveDocumentRequest: {"draft_name":"draft-ietf-example-document"},
  } satisfies ClustersAddDocumentRequest;

  try {
    const data = await api.clustersAddDocument(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **number** | `number` |  | [Defaults to `undefined`] |
| **clusterAddRemoveDocumentRequest** | [ClusterAddRemoveDocumentRequest](ClusterAddRemoveDocumentRequest.md) |  | |

### Return type

[**Cluster**](Cluster.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## clustersCreate

> Cluster clustersCreate(clusterRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { ClustersCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // ClusterRequest
    clusterRequest: ...,
  } satisfies ClustersCreateRequest;

  try {
    const data = await api.clustersCreate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **clusterRequest** | [ClusterRequest](ClusterRequest.md) |  | |

### Return type

[**Cluster**](Cluster.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## clustersList

> Array&lt;Cluster&gt; clustersList(isActive, ordering)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { ClustersListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // boolean | Filter by active status. A cluster is considered active if at least one of its documents is not in terminal state (published/withdrawn). (optional)
    isActive: true,
    // string | Which field to use when ordering the results. (optional)
    ordering: ordering_example,
  } satisfies ClustersListRequest;

  try {
    const data = await api.clustersList(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **isActive** | `boolean` | Filter by active status. A cluster is considered active if at least one of its documents is not in terminal state (published/withdrawn). | [Optional] [Defaults to `undefined`] |
| **ordering** | `string` | Which field to use when ordering the results. | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;Cluster&gt;**](Cluster.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## clustersPartialUpdate

> Cluster clustersPartialUpdate(number, patchedClusterRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { ClustersPartialUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number
    number: 56,
    // PatchedClusterRequest (optional)
    patchedClusterRequest: ...,
  } satisfies ClustersPartialUpdateRequest;

  try {
    const data = await api.clustersPartialUpdate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **number** | `number` |  | [Defaults to `undefined`] |
| **patchedClusterRequest** | [PatchedClusterRequest](PatchedClusterRequest.md) |  | [Optional] |

### Return type

[**Cluster**](Cluster.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## clustersRemoveDocument

> Cluster clustersRemoveDocument(number, clusterAddRemoveDocumentRequest)



Remove a document from a cluster

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { ClustersRemoveDocumentRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number
    number: 56,
    // ClusterAddRemoveDocumentRequest
    clusterAddRemoveDocumentRequest: {"draft_name":"draft-ietf-example-document"},
  } satisfies ClustersRemoveDocumentRequest;

  try {
    const data = await api.clustersRemoveDocument(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **number** | `number` |  | [Defaults to `undefined`] |
| **clusterAddRemoveDocumentRequest** | [ClusterAddRemoveDocumentRequest](ClusterAddRemoveDocumentRequest.md) |  | |

### Return type

[**Cluster**](Cluster.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## clustersReorderDocuments

> Cluster clustersReorderDocuments(number, clusterReorderDocumentsRequest)



Reorder documents in a cluster

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { ClustersReorderDocumentsRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number
    number: 56,
    // ClusterReorderDocumentsRequest
    clusterReorderDocumentsRequest: {"draft_names":["draft-ietf-example-first","draft-ietf-example-second","draft-ietf-example-third"]},
  } satisfies ClustersReorderDocumentsRequest;

  try {
    const data = await api.clustersReorderDocuments(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **number** | `number` |  | [Defaults to `undefined`] |
| **clusterReorderDocumentsRequest** | [ClusterReorderDocumentsRequest](ClusterReorderDocumentsRequest.md) |  | |

### Return type

[**Cluster**](Cluster.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## clustersRetrieve

> Cluster clustersRetrieve(number)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { ClustersRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number
    number: 56,
  } satisfies ClustersRetrieveRequest;

  try {
    const data = await api.clustersRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **number** | `number` |  | [Defaults to `undefined`] |

### Return type

[**Cluster**](Cluster.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## clustersUpdate

> Cluster clustersUpdate(number, clusterRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { ClustersUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number
    number: 56,
    // ClusterRequest
    clusterRequest: ...,
  } satisfies ClustersUpdateRequest;

  try {
    const data = await api.clustersUpdate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **number** | `number` |  | [Defaults to `undefined`] |
| **clusterRequest** | [ClusterRequest](ClusterRequest.md) |  | |

### Return type

[**Cluster**](Cluster.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## docRelationshipNamesList

> Array&lt;Name&gt; docRelationshipNamesList()



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocRelationshipNamesListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  try {
    const data = await api.docRelationshipNamesList();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**Array&lt;Name&gt;**](Name.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## docRelationshipNamesRetrieve

> Name docRelationshipNamesRetrieve(slug)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocRelationshipNamesRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string | A unique value identifying this doc relationship name.
    slug: slug_example,
  } satisfies DocRelationshipNamesRetrieveRequest;

  try {
    const data = await api.docRelationshipNamesRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **slug** | `string` | A unique value identifying this doc relationship name. | [Defaults to `undefined`] |

### Return type

[**Name**](Name.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentMailSend

> MailResponse documentMailSend(draftName, mailMessageRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentMailSendRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // MailMessageRequest
    mailMessageRequest: ...,
  } satisfies DocumentMailSendRequest;

  try {
    const data = await api.documentMailSend(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **mailMessageRequest** | [MailMessageRequest](MailMessageRequest.md) |  | |

### Return type

[**MailResponse**](MailResponse.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsActionHoldersList

> Array&lt;ActionHolder&gt; documentsActionHoldersList(draftName)



ViewSet for ActionHolder entries related to a draft

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsActionHoldersListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
  } satisfies DocumentsActionHoldersListRequest;

  try {
    const data = await api.documentsActionHoldersList(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |

### Return type

[**Array&lt;ActionHolder&gt;**](ActionHolder.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsActionHoldersPartialUpdate

> ActionHolder documentsActionHoldersPartialUpdate(draftName, id, patchedActionHolderRequest)



ViewSet for ActionHolder entries related to a draft

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsActionHoldersPartialUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // number | A unique integer value identifying this action holder.
    id: 56,
    // PatchedActionHolderRequest (optional)
    patchedActionHolderRequest: ...,
  } satisfies DocumentsActionHoldersPartialUpdateRequest;

  try {
    const data = await api.documentsActionHoldersPartialUpdate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **id** | `number` | A unique integer value identifying this action holder. | [Defaults to `undefined`] |
| **patchedActionHolderRequest** | [PatchedActionHolderRequest](PatchedActionHolderRequest.md) |  | [Optional] |

### Return type

[**ActionHolder**](ActionHolder.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsActionHoldersRetrieve

> ActionHolder documentsActionHoldersRetrieve(draftName, id)



ViewSet for ActionHolder entries related to a draft

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsActionHoldersRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // number | A unique integer value identifying this action holder.
    id: 56,
  } satisfies DocumentsActionHoldersRetrieveRequest;

  try {
    const data = await api.documentsActionHoldersRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **id** | `number` | A unique integer value identifying this action holder. | [Defaults to `undefined`] |

### Return type

[**ActionHolder**](ActionHolder.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsActionHoldersUpdate

> ActionHolder documentsActionHoldersUpdate(draftName, id, actionHolderRequest)



ViewSet for ActionHolder entries related to a draft

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsActionHoldersUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // number | A unique integer value identifying this action holder.
    id: 56,
    // ActionHolderRequest (optional)
    actionHolderRequest: ...,
  } satisfies DocumentsActionHoldersUpdateRequest;

  try {
    const data = await api.documentsActionHoldersUpdate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **id** | `number` | A unique integer value identifying this action holder. | [Defaults to `undefined`] |
| **actionHolderRequest** | [ActionHolderRequest](ActionHolderRequest.md) |  | [Optional] |

### Return type

[**ActionHolder**](ActionHolder.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsApprovalLogsCreate

> ApprovalLogMessage documentsApprovalLogsCreate(draftName, approvalLogMessageRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsApprovalLogsCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // ApprovalLogMessageRequest
    approvalLogMessageRequest: ...,
  } satisfies DocumentsApprovalLogsCreateRequest;

  try {
    const data = await api.documentsApprovalLogsCreate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **approvalLogMessageRequest** | [ApprovalLogMessageRequest](ApprovalLogMessageRequest.md) |  | |

### Return type

[**ApprovalLogMessage**](ApprovalLogMessage.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsApprovalLogsDestroy

> documentsApprovalLogsDestroy(draftName, id)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsApprovalLogsDestroyRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // number | A unique integer value identifying this approval log message.
    id: 56,
  } satisfies DocumentsApprovalLogsDestroyRequest;

  try {
    const data = await api.documentsApprovalLogsDestroy(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **id** | `number` | A unique integer value identifying this approval log message. | [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | No response body |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsApprovalLogsList

> Array&lt;ApprovalLogMessage&gt; documentsApprovalLogsList(draftName)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsApprovalLogsListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
  } satisfies DocumentsApprovalLogsListRequest;

  try {
    const data = await api.documentsApprovalLogsList(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |

### Return type

[**Array&lt;ApprovalLogMessage&gt;**](ApprovalLogMessage.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsApprovalLogsPartialUpdate

> ApprovalLogMessage documentsApprovalLogsPartialUpdate(draftName, id, patchedApprovalLogMessageRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsApprovalLogsPartialUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // number | A unique integer value identifying this approval log message.
    id: 56,
    // PatchedApprovalLogMessageRequest (optional)
    patchedApprovalLogMessageRequest: ...,
  } satisfies DocumentsApprovalLogsPartialUpdateRequest;

  try {
    const data = await api.documentsApprovalLogsPartialUpdate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **id** | `number` | A unique integer value identifying this approval log message. | [Defaults to `undefined`] |
| **patchedApprovalLogMessageRequest** | [PatchedApprovalLogMessageRequest](PatchedApprovalLogMessageRequest.md) |  | [Optional] |

### Return type

[**ApprovalLogMessage**](ApprovalLogMessage.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsApprovalLogsRetrieve

> ApprovalLogMessage documentsApprovalLogsRetrieve(draftName, id)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsApprovalLogsRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // number | A unique integer value identifying this approval log message.
    id: 56,
  } satisfies DocumentsApprovalLogsRetrieveRequest;

  try {
    const data = await api.documentsApprovalLogsRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **id** | `number` | A unique integer value identifying this approval log message. | [Defaults to `undefined`] |

### Return type

[**ApprovalLogMessage**](ApprovalLogMessage.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsApprovalLogsUpdate

> ApprovalLogMessage documentsApprovalLogsUpdate(draftName, id, approvalLogMessageRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsApprovalLogsUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // number | A unique integer value identifying this approval log message.
    id: 56,
    // ApprovalLogMessageRequest
    approvalLogMessageRequest: ...,
  } satisfies DocumentsApprovalLogsUpdateRequest;

  try {
    const data = await api.documentsApprovalLogsUpdate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **id** | `number` | A unique integer value identifying this approval log message. | [Defaults to `undefined`] |
| **approvalLogMessageRequest** | [ApprovalLogMessageRequest](ApprovalLogMessageRequest.md) |  | |

### Return type

[**ApprovalLogMessage**](ApprovalLogMessage.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsAuthorsCreate

> CreateRfcAuthor documentsAuthorsCreate(draftName, createRfcAuthorRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsAuthorsCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // CreateRfcAuthorRequest
    createRfcAuthorRequest: ...,
  } satisfies DocumentsAuthorsCreateRequest;

  try {
    const data = await api.documentsAuthorsCreate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **createRfcAuthorRequest** | [CreateRfcAuthorRequest](CreateRfcAuthorRequest.md) |  | |

### Return type

[**CreateRfcAuthor**](CreateRfcAuthor.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsAuthorsDestroy

> documentsAuthorsDestroy(draftName, id)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsAuthorsDestroyRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // number | A unique integer value identifying this rfc author.
    id: 56,
  } satisfies DocumentsAuthorsDestroyRequest;

  try {
    const data = await api.documentsAuthorsDestroy(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **id** | `number` | A unique integer value identifying this rfc author. | [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | No response body |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsAuthorsList

> Array&lt;RfcAuthor&gt; documentsAuthorsList(draftName)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsAuthorsListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
  } satisfies DocumentsAuthorsListRequest;

  try {
    const data = await api.documentsAuthorsList(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |

### Return type

[**Array&lt;RfcAuthor&gt;**](RfcAuthor.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsAuthorsOrder

> AuthorOrderStatus documentsAuthorsOrder(draftName, authorOrderRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsAuthorsOrderRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // AuthorOrderRequest
    authorOrderRequest: ...,
  } satisfies DocumentsAuthorsOrderRequest;

  try {
    const data = await api.documentsAuthorsOrder(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **authorOrderRequest** | [AuthorOrderRequest](AuthorOrderRequest.md) |  | |

### Return type

[**AuthorOrderStatus**](AuthorOrderStatus.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsAuthorsPartialUpdate

> RfcAuthor documentsAuthorsPartialUpdate(draftName, id, patchedRfcAuthorRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsAuthorsPartialUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // number | A unique integer value identifying this rfc author.
    id: 56,
    // PatchedRfcAuthorRequest (optional)
    patchedRfcAuthorRequest: ...,
  } satisfies DocumentsAuthorsPartialUpdateRequest;

  try {
    const data = await api.documentsAuthorsPartialUpdate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **id** | `number` | A unique integer value identifying this rfc author. | [Defaults to `undefined`] |
| **patchedRfcAuthorRequest** | [PatchedRfcAuthorRequest](PatchedRfcAuthorRequest.md) |  | [Optional] |

### Return type

[**RfcAuthor**](RfcAuthor.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsAuthorsRetrieve

> RfcAuthor documentsAuthorsRetrieve(draftName, id)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsAuthorsRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // number | A unique integer value identifying this rfc author.
    id: 56,
  } satisfies DocumentsAuthorsRetrieveRequest;

  try {
    const data = await api.documentsAuthorsRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **id** | `number` | A unique integer value identifying this rfc author. | [Defaults to `undefined`] |

### Return type

[**RfcAuthor**](RfcAuthor.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsAuthorsUpdate

> RfcAuthor documentsAuthorsUpdate(draftName, id, rfcAuthorRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsAuthorsUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // number | A unique integer value identifying this rfc author.
    id: 56,
    // RfcAuthorRequest
    rfcAuthorRequest: ...,
  } satisfies DocumentsAuthorsUpdateRequest;

  try {
    const data = await api.documentsAuthorsUpdate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **id** | `number` | A unique integer value identifying this rfc author. | [Defaults to `undefined`] |
| **rfcAuthorRequest** | [RfcAuthorRequest](RfcAuthorRequest.md) |  | |

### Return type

[**RfcAuthor**](RfcAuthor.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsCommentsCreate

> DocumentComment documentsCommentsCreate(draftName, documentCommentRequest)



ViewSet for comments on an RfcToBe or datatracker Document

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsCommentsCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // DocumentCommentRequest
    documentCommentRequest: ...,
  } satisfies DocumentsCommentsCreateRequest;

  try {
    const data = await api.documentsCommentsCreate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **documentCommentRequest** | [DocumentCommentRequest](DocumentCommentRequest.md) |  | |

### Return type

[**DocumentComment**](DocumentComment.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsCommentsList

> PaginatedDocumentCommentList documentsCommentsList(draftName, limit, offset)



ViewSet for comments on an RfcToBe or datatracker Document

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsCommentsListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // number | Number of results to return per page. (optional)
    limit: 56,
    // number | The initial index from which to return the results. (optional)
    offset: 56,
  } satisfies DocumentsCommentsListRequest;

  try {
    const data = await api.documentsCommentsList(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **limit** | `number` | Number of results to return per page. | [Optional] [Defaults to `undefined`] |
| **offset** | `number` | The initial index from which to return the results. | [Optional] [Defaults to `undefined`] |

### Return type

[**PaginatedDocumentCommentList**](PaginatedDocumentCommentList.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsCommentsPartialUpdate

> DocumentComment documentsCommentsPartialUpdate(draftName, id, patchedDocumentCommentRequest)



ViewSet for comments on an RfcToBe or datatracker Document

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsCommentsPartialUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // number | A unique integer value identifying this rpc document comment.
    id: 56,
    // PatchedDocumentCommentRequest (optional)
    patchedDocumentCommentRequest: ...,
  } satisfies DocumentsCommentsPartialUpdateRequest;

  try {
    const data = await api.documentsCommentsPartialUpdate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **id** | `number` | A unique integer value identifying this rpc document comment. | [Defaults to `undefined`] |
| **patchedDocumentCommentRequest** | [PatchedDocumentCommentRequest](PatchedDocumentCommentRequest.md) |  | [Optional] |

### Return type

[**DocumentComment**](DocumentComment.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsCommentsUpdate

> DocumentComment documentsCommentsUpdate(draftName, id, documentCommentRequest)



ViewSet for comments on an RfcToBe or datatracker Document

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsCommentsUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // number | A unique integer value identifying this rpc document comment.
    id: 56,
    // DocumentCommentRequest
    documentCommentRequest: ...,
  } satisfies DocumentsCommentsUpdateRequest;

  try {
    const data = await api.documentsCommentsUpdate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **id** | `number` | A unique integer value identifying this rpc document comment. | [Defaults to `undefined`] |
| **documentCommentRequest** | [DocumentCommentRequest](DocumentCommentRequest.md) |  | |

### Return type

[**DocumentComment**](DocumentComment.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsCreate

> RfcToBe documentsCreate(rfcToBeRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // RfcToBeRequest
    rfcToBeRequest: ...,
  } satisfies DocumentsCreateRequest;

  try {
    const data = await api.documentsCreate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **rfcToBeRequest** | [RfcToBeRequest](RfcToBeRequest.md) |  | |

### Return type

[**RfcToBe**](RfcToBe.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsDestroy

> documentsDestroy(draftName)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsDestroyRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
  } satisfies DocumentsDestroyRequest;

  try {
    const data = await api.documentsDestroy(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | No response body |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsFinalApprovalsCreate

> CreateFinalApproval documentsFinalApprovalsCreate(draftName, createFinalApprovalRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsFinalApprovalsCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // CreateFinalApprovalRequest
    createFinalApprovalRequest: ...,
  } satisfies DocumentsFinalApprovalsCreateRequest;

  try {
    const data = await api.documentsFinalApprovalsCreate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **createFinalApprovalRequest** | [CreateFinalApprovalRequest](CreateFinalApprovalRequest.md) |  | |

### Return type

[**CreateFinalApproval**](CreateFinalApproval.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsFinalApprovalsDestroy

> documentsFinalApprovalsDestroy(draftName, id)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsFinalApprovalsDestroyRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // number | A unique integer value identifying this final approval.
    id: 56,
  } satisfies DocumentsFinalApprovalsDestroyRequest;

  try {
    const data = await api.documentsFinalApprovalsDestroy(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **id** | `number` | A unique integer value identifying this final approval. | [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | No response body |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsFinalApprovalsList

> Array&lt;FinalApproval&gt; documentsFinalApprovalsList(draftName, approverDatatrackerId, rfcToBeRfcNumber)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsFinalApprovalsListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // number (optional)
    approverDatatrackerId: 56,
    // number (optional)
    rfcToBeRfcNumber: 56,
  } satisfies DocumentsFinalApprovalsListRequest;

  try {
    const data = await api.documentsFinalApprovalsList(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **approverDatatrackerId** | `number` |  | [Optional] [Defaults to `undefined`] |
| **rfcToBeRfcNumber** | `number` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;FinalApproval&gt;**](FinalApproval.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsFinalApprovalsPartialUpdate

> FinalApproval documentsFinalApprovalsPartialUpdate(draftName, id, patchedFinalApprovalRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsFinalApprovalsPartialUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // number | A unique integer value identifying this final approval.
    id: 56,
    // PatchedFinalApprovalRequest (optional)
    patchedFinalApprovalRequest: ...,
  } satisfies DocumentsFinalApprovalsPartialUpdateRequest;

  try {
    const data = await api.documentsFinalApprovalsPartialUpdate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **id** | `number` | A unique integer value identifying this final approval. | [Defaults to `undefined`] |
| **patchedFinalApprovalRequest** | [PatchedFinalApprovalRequest](PatchedFinalApprovalRequest.md) |  | [Optional] |

### Return type

[**FinalApproval**](FinalApproval.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsFinalApprovalsRetrieve

> FinalApproval documentsFinalApprovalsRetrieve(draftName, id)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsFinalApprovalsRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // number | A unique integer value identifying this final approval.
    id: 56,
  } satisfies DocumentsFinalApprovalsRetrieveRequest;

  try {
    const data = await api.documentsFinalApprovalsRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **id** | `number` | A unique integer value identifying this final approval. | [Defaults to `undefined`] |

### Return type

[**FinalApproval**](FinalApproval.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsFinalApprovalsUpdate

> FinalApproval documentsFinalApprovalsUpdate(draftName, id, finalApprovalRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsFinalApprovalsUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // number | A unique integer value identifying this final approval.
    id: 56,
    // FinalApprovalRequest (optional)
    finalApprovalRequest: ...,
  } satisfies DocumentsFinalApprovalsUpdateRequest;

  try {
    const data = await api.documentsFinalApprovalsUpdate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **id** | `number` | A unique integer value identifying this final approval. | [Defaults to `undefined`] |
| **finalApprovalRequest** | [FinalApprovalRequest](FinalApprovalRequest.md) |  | [Optional] |

### Return type

[**FinalApproval**](FinalApproval.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsHistoryList

> Array&lt;RfcToBeHistory&gt; documentsHistoryList(draftName)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsHistoryListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
  } satisfies DocumentsHistoryListRequest;

  try {
    const data = await api.documentsHistoryList(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |

### Return type

[**Array&lt;RfcToBeHistory&gt;**](RfcToBeHistory.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsList

> PaginatedRfcToBeList documentsList(disposition, limit, offset, ordering, publishedWithinDays)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string (optional)
    disposition: disposition_example,
    // number | Number of results to return per page. (optional)
    limit: 56,
    // number | The initial index from which to return the results. (optional)
    offset: 56,
    // string | Which field to use when ordering the results. (optional)
    ordering: ordering_example,
    // number | Show only RFCs published within the last N days. (optional)
    publishedWithinDays: 56,
  } satisfies DocumentsListRequest;

  try {
    const data = await api.documentsList(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **disposition** | `string` |  | [Optional] [Defaults to `undefined`] |
| **limit** | `number` | Number of results to return per page. | [Optional] [Defaults to `undefined`] |
| **offset** | `number` | The initial index from which to return the results. | [Optional] [Defaults to `undefined`] |
| **ordering** | `string` | Which field to use when ordering the results. | [Optional] [Defaults to `undefined`] |
| **publishedWithinDays** | `number` | Show only RFCs published within the last N days. | [Optional] [Defaults to `undefined`] |

### Return type

[**PaginatedRfcToBeList**](PaginatedRfcToBeList.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsMetadataValidationResultsDestroy

> documentsMetadataValidationResultsDestroy(draftName, headSha)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsMetadataValidationResultsDestroyRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // string
    headSha: headSha_example,
  } satisfies DocumentsMetadataValidationResultsDestroyRequest;

  try {
    const data = await api.documentsMetadataValidationResultsDestroy(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **headSha** | `string` |  | [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | No response body |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsMetadataValidationResultsList

> Array&lt;MetadataValidationResults&gt; documentsMetadataValidationResultsList(draftName)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsMetadataValidationResultsListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
  } satisfies DocumentsMetadataValidationResultsListRequest;

  try {
    const data = await api.documentsMetadataValidationResultsList(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |

### Return type

[**Array&lt;MetadataValidationResults&gt;**](MetadataValidationResults.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsMetadataValidationResultsRetrieve

> MetadataValidationResults documentsMetadataValidationResultsRetrieve(draftName, headSha)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsMetadataValidationResultsRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // string
    headSha: headSha_example,
  } satisfies DocumentsMetadataValidationResultsRetrieveRequest;

  try {
    const data = await api.documentsMetadataValidationResultsRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **headSha** | `string` |  | [Defaults to `undefined`] |

### Return type

[**MetadataValidationResults**](MetadataValidationResults.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsPartialUpdate

> RfcToBe documentsPartialUpdate(draftName, patchedRfcToBeRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsPartialUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // PatchedRfcToBeRequest (optional)
    patchedRfcToBeRequest: ...,
  } satisfies DocumentsPartialUpdateRequest;

  try {
    const data = await api.documentsPartialUpdate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **patchedRfcToBeRequest** | [PatchedRfcToBeRequest](PatchedRfcToBeRequest.md) |  | [Optional] |

### Return type

[**RfcToBe**](RfcToBe.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsPublish

> documentsPublish(draftName, publishRfcRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsPublishRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // PublishRfcRequest
    publishRfcRequest: ...,
  } satisfies DocumentsPublishRequest;

  try {
    const data = await api.documentsPublish(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **publishRfcRequest** | [PublishRfcRequest](PublishRfcRequest.md) |  | |

### Return type

`void` (Empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | No response body |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsReferencesCreate

> RpcRelatedDocument documentsReferencesCreate(draftName, createRpcRelatedDocumentRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsReferencesCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // CreateRpcRelatedDocumentRequest
    createRpcRelatedDocumentRequest: {"relationship":"not-received","target_draft_name":"draft-lorem-ipsum-dolor-sit-amet"},
  } satisfies DocumentsReferencesCreateRequest;

  try {
    const data = await api.documentsReferencesCreate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **createRpcRelatedDocumentRequest** | [CreateRpcRelatedDocumentRequest](CreateRpcRelatedDocumentRequest.md) |  | |

### Return type

[**RpcRelatedDocument**](RpcRelatedDocument.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsReferencesDestroy

> documentsReferencesDestroy(draftName, id)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsReferencesDestroyRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // number | A unique integer value identifying this rpc related document.
    id: 56,
  } satisfies DocumentsReferencesDestroyRequest;

  try {
    const data = await api.documentsReferencesDestroy(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **id** | `number` | A unique integer value identifying this rpc related document. | [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | No response body |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsReferencesList

> Array&lt;RpcRelatedDocument&gt; documentsReferencesList(draftName)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsReferencesListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
  } satisfies DocumentsReferencesListRequest;

  try {
    const data = await api.documentsReferencesList(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |

### Return type

[**Array&lt;RpcRelatedDocument&gt;**](RpcRelatedDocument.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsReferencesPartialUpdate

> RpcRelatedDocument documentsReferencesPartialUpdate(draftName, id, patchedRpcRelatedDocumentRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsReferencesPartialUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // number | A unique integer value identifying this rpc related document.
    id: 56,
    // PatchedRpcRelatedDocumentRequest (optional)
    patchedRpcRelatedDocumentRequest: ...,
  } satisfies DocumentsReferencesPartialUpdateRequest;

  try {
    const data = await api.documentsReferencesPartialUpdate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **id** | `number` | A unique integer value identifying this rpc related document. | [Defaults to `undefined`] |
| **patchedRpcRelatedDocumentRequest** | [PatchedRpcRelatedDocumentRequest](PatchedRpcRelatedDocumentRequest.md) |  | [Optional] |

### Return type

[**RpcRelatedDocument**](RpcRelatedDocument.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsReferencesRetrieve

> RpcRelatedDocument documentsReferencesRetrieve(draftName, id)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsReferencesRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // number | A unique integer value identifying this rpc related document.
    id: 56,
  } satisfies DocumentsReferencesRetrieveRequest;

  try {
    const data = await api.documentsReferencesRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **id** | `number` | A unique integer value identifying this rpc related document. | [Defaults to `undefined`] |

### Return type

[**RpcRelatedDocument**](RpcRelatedDocument.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsReferencesUpdate

> RpcRelatedDocument documentsReferencesUpdate(draftName, id, rpcRelatedDocumentRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsReferencesUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // number | A unique integer value identifying this rpc related document.
    id: 56,
    // RpcRelatedDocumentRequest
    rpcRelatedDocumentRequest: ...,
  } satisfies DocumentsReferencesUpdateRequest;

  try {
    const data = await api.documentsReferencesUpdate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **id** | `number` | A unique integer value identifying this rpc related document. | [Defaults to `undefined`] |
| **rpcRelatedDocumentRequest** | [RpcRelatedDocumentRequest](RpcRelatedDocumentRequest.md) |  | |

### Return type

[**RpcRelatedDocument**](RpcRelatedDocument.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsRetrieve

> RfcToBe documentsRetrieve(draftName)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
  } satisfies DocumentsRetrieveRequest;

  try {
    const data = await api.documentsRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |

### Return type

[**RfcToBe**](RfcToBe.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## documentsUpdate

> RfcToBe documentsUpdate(draftName, rfcToBeRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { DocumentsUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
    // RfcToBeRequest
    rfcToBeRequest: ...,
  } satisfies DocumentsUpdateRequest;

  try {
    const data = await api.documentsUpdate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |
| **rfcToBeRequest** | [RfcToBeRequest](RfcToBeRequest.md) |  | |

### Return type

[**RfcToBe**](RfcToBe.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## labelsCreate

> Label labelsCreate(labelRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { LabelsCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // LabelRequest
    labelRequest: ...,
  } satisfies LabelsCreateRequest;

  try {
    const data = await api.labelsCreate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **labelRequest** | [LabelRequest](LabelRequest.md) |  | |

### Return type

[**Label**](Label.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## labelsDestroy

> labelsDestroy(id)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { LabelsDestroyRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number | A unique integer value identifying this label.
    id: 56,
  } satisfies LabelsDestroyRequest;

  try {
    const data = await api.labelsDestroy(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **id** | `number` | A unique integer value identifying this label. | [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | No response body |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## labelsList

> Array&lt;Label&gt; labelsList()



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { LabelsListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  try {
    const data = await api.labelsList();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**Array&lt;Label&gt;**](Label.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## labelsPartialUpdate

> Label labelsPartialUpdate(id, patchedLabelRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { LabelsPartialUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number | A unique integer value identifying this label.
    id: 56,
    // PatchedLabelRequest (optional)
    patchedLabelRequest: ...,
  } satisfies LabelsPartialUpdateRequest;

  try {
    const data = await api.labelsPartialUpdate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **id** | `number` | A unique integer value identifying this label. | [Defaults to `undefined`] |
| **patchedLabelRequest** | [PatchedLabelRequest](PatchedLabelRequest.md) |  | [Optional] |

### Return type

[**Label**](Label.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## labelsRetrieve

> Label labelsRetrieve(id)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { LabelsRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number | A unique integer value identifying this label.
    id: 56,
  } satisfies LabelsRetrieveRequest;

  try {
    const data = await api.labelsRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **id** | `number` | A unique integer value identifying this label. | [Defaults to `undefined`] |

### Return type

[**Label**](Label.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## labelsUpdate

> Label labelsUpdate(id, labelRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { LabelsUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number | A unique integer value identifying this label.
    id: 56,
    // LabelRequest
    labelRequest: ...,
  } satisfies LabelsUpdateRequest;

  try {
    const data = await api.labelsUpdate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **id** | `number` | A unique integer value identifying this label. | [Defaults to `undefined`] |
| **labelRequest** | [LabelRequest](LabelRequest.md) |  | |

### Return type

[**Label**](Label.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## mailSend

> MailResponse mailSend(mailMessageRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { MailSendRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // MailMessageRequest
    mailMessageRequest: ...,
  } satisfies MailSendRequest;

  try {
    const data = await api.mailSend(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **mailMessageRequest** | [MailMessageRequest](MailMessageRequest.md) |  | |

### Return type

[**MailResponse**](MailResponse.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## mailtemplateList

> Array&lt;MailTemplate&gt; mailtemplateList(rfctobeId)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { MailtemplateListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number
    rfctobeId: 56,
  } satisfies MailtemplateListRequest;

  try {
    const data = await api.mailtemplateList(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **rfctobeId** | `number` |  | [Defaults to `undefined`] |

### Return type

[**Array&lt;MailTemplate&gt;**](MailTemplate.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## metadataValidationResultsCreate

> MetadataValidationResults metadataValidationResultsCreate(draftName)



Create a pending metadata validation result and enqueue task

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { MetadataValidationResultsCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    draftName: draftName_example,
  } satisfies MetadataValidationResultsCreateRequest;

  try {
    const data = await api.metadataValidationResultsCreate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` |  | [Defaults to `undefined`] |

### Return type

[**MetadataValidationResults**](MetadataValidationResults.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** |  |  -  |
| **200** |  |  -  |
| **404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## metadataValidationResultsSync

> MetadataValidationResults metadataValidationResultsSync(draftName, syncMetadataRequestRequest)



Sync metadata validation results - update DB fields from XML. Requires head_sha in request body to make sure the right metadata is synced.

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { MetadataValidationResultsSyncRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string | Draft name
    draftName: draftName_example,
    // SyncMetadataRequestRequest
    syncMetadataRequestRequest: ...,
  } satisfies MetadataValidationResultsSyncRequest;

  try {
    const data = await api.metadataValidationResultsSync(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **draftName** | `string` | Draft name | [Defaults to `undefined`] |
| **syncMetadataRequestRequest** | [SyncMetadataRequestRequest](SyncMetadataRequestRequest.md) |  | |

### Return type

[**MetadataValidationResults**](MetadataValidationResults.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |
| **404** |  |  -  |
| **400** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## profile

> Profile profile()



Get profile of current user

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { ProfileRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  try {
    const data = await api.profile();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**Profile**](Profile.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## profileRetrieveDemoOnly

> { [key: string]: any; } profileRetrieveDemoOnly(rpcPersonId)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { ProfileRetrieveDemoOnlyRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number
    rpcPersonId: 56,
  } satisfies ProfileRetrieveDemoOnlyRequest;

  try {
    const data = await api.profileRetrieveDemoOnly(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **rpcPersonId** | `number` |  | [Defaults to `undefined`] |

### Return type

**{ [key: string]: any; }**

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## queueList

> Array&lt;QueueItem&gt; queueList(disposition, pendingFinalApproval)



Queue view for purple application

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { QueueListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string (optional)
    disposition: disposition_example,
    // boolean | Filter by pending final approval status, true returns drafts with at least one pending final approval, false returns drafts where all final approvals are approved. (optional)
    pendingFinalApproval: true,
  } satisfies QueueListRequest;

  try {
    const data = await api.queueList(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **disposition** | `string` |  | [Optional] [Defaults to `undefined`] |
| **pendingFinalApproval** | `boolean` | Filter by pending final approval status, true returns drafts with at least one pending final approval, false returns drafts where all final approvals are approved. | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;QueueItem&gt;**](QueueItem.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## rpcPersonAssignmentsList

> Array&lt;NestedAssignment&gt; rpcPersonAssignmentsList(personId)



Assignments for a specific RPC Person  URL router must provide the &#x60;person_id&#x60; kwarg

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { RpcPersonAssignmentsListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number
    personId: 56,
  } satisfies RpcPersonAssignmentsListRequest;

  try {
    const data = await api.rpcPersonAssignmentsList(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **personId** | `number` |  | [Defaults to `undefined`] |

### Return type

[**Array&lt;NestedAssignment&gt;**](NestedAssignment.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## rpcPersonList

> Array&lt;RpcPerson&gt; rpcPersonList(isActive)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { RpcPersonListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // boolean (optional)
    isActive: true,
  } satisfies RpcPersonListRequest;

  try {
    const data = await api.rpcPersonList(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **isActive** | `boolean` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;RpcPerson&gt;**](RpcPerson.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## rpcPersonRetrieve

> RpcPerson rpcPersonRetrieve(id)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { RpcPersonRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number | A unique integer value identifying this rpc person.
    id: 56,
  } satisfies RpcPersonRetrieveRequest;

  try {
    const data = await api.rpcPersonRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **id** | `number` | A unique integer value identifying this rpc person. | [Defaults to `undefined`] |

### Return type

[**RpcPerson**](RpcPerson.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## rpcRolesList

> Array&lt;RpcRole&gt; rpcRolesList()



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { RpcRolesListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  try {
    const data = await api.rpcRolesList();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**Array&lt;RpcRole&gt;**](RpcRole.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## rpcRolesRetrieve

> RpcRole rpcRolesRetrieve(slug)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { RpcRolesRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string | A unique value identifying this rpc role.
    slug: slug_example,
  } satisfies RpcRolesRetrieveRequest;

  try {
    const data = await api.rpcRolesRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **slug** | `string` | A unique value identifying this rpc role. | [Defaults to `undefined`] |

### Return type

[**RpcRole**](RpcRole.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## searchDatatrackerpersons

> PaginatedBaseDatatrackerPersonList searchDatatrackerpersons(limit, offset, search)



Datatracker person search API  Search for a datatracker person by name/email fragment.

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { SearchDatatrackerpersonsRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number | Number of results to return per page. (optional)
    limit: 56,
    // number | The initial index from which to return the results. (optional)
    offset: 56,
    // string | Name/email fragment for the search (optional)
    search: search_example,
  } satisfies SearchDatatrackerpersonsRequest;

  try {
    const data = await api.searchDatatrackerpersons(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **limit** | `number` | Number of results to return per page. | [Optional] [Defaults to `undefined`] |
| **offset** | `number` | The initial index from which to return the results. | [Optional] [Defaults to `undefined`] |
| **search** | `string` | Name/email fragment for the search | [Optional] [Defaults to `undefined`] |

### Return type

[**PaginatedBaseDatatrackerPersonList**](PaginatedBaseDatatrackerPersonList.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## sourceFormatNamesList

> Array&lt;Name&gt; sourceFormatNamesList()



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { SourceFormatNamesListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  try {
    const data = await api.sourceFormatNamesList();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**Array&lt;Name&gt;**](Name.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## sourceFormatNamesRetrieve

> Name sourceFormatNamesRetrieve(slug)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { SourceFormatNamesRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string | A unique value identifying this source format name.
    slug: slug_example,
  } satisfies SourceFormatNamesRetrieveRequest;

  try {
    const data = await api.sourceFormatNamesRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **slug** | `string` | A unique value identifying this source format name. | [Defaults to `undefined`] |

### Return type

[**Name**](Name.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## statsLabels

> LabelStats statsLabels()



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { StatsLabelsRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  try {
    const data = await api.statsLabels();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**LabelStats**](LabelStats.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## stdLevelNamesList

> Array&lt;Name&gt; stdLevelNamesList()



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { StdLevelNamesListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  try {
    const data = await api.stdLevelNamesList();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**Array&lt;Name&gt;**](Name.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## stdLevelNamesRetrieve

> Name stdLevelNamesRetrieve(slug)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { StdLevelNamesRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string | A unique value identifying this std level name.
    slug: slug_example,
  } satisfies StdLevelNamesRetrieveRequest;

  try {
    const data = await api.stdLevelNamesRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **slug** | `string` | A unique value identifying this std level name. | [Defaults to `undefined`] |

### Return type

[**Name**](Name.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## streamNamesList

> Array&lt;Name&gt; streamNamesList()



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { StreamNamesListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  try {
    const data = await api.streamNamesList();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**Array&lt;Name&gt;**](Name.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## streamNamesRetrieve

> Name streamNamesRetrieve(slug)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { StreamNamesRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string | A unique value identifying this stream name.
    slug: slug_example,
  } satisfies StreamNamesRetrieveRequest;

  try {
    const data = await api.streamNamesRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **slug** | `string` | A unique value identifying this stream name. | [Defaults to `undefined`] |

### Return type

[**Name**](Name.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## submissionsImport

> RfcToBe submissionsImport(documentId, createRfcToBeRequest)



View to import a submission and create an RfcToBe

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { SubmissionsImportRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number
    documentId: 56,
    // CreateRfcToBeRequest
    createRfcToBeRequest: ...,
  } satisfies SubmissionsImportRequest;

  try {
    const data = await api.submissionsImport(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **documentId** | `number` |  | [Defaults to `undefined`] |
| **createRfcToBeRequest** | [CreateRfcToBeRequest](CreateRfcToBeRequest.md) |  | |

### Return type

[**RfcToBe**](RfcToBe.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## submissionsList

> Array&lt;SubmissionListItem&gt; submissionsList()



Retrieve submitted docs not yet in the purple queue  Returns documents in datatracker that have been submitted to the RPC but are not yet in the queue  [     {         \&quot;id\&quot;: 123456,         \&quot;name\&quot;: \&quot;draft-foo-bar\&quot;,         \&quot;stream\&quot;: \&quot;ietf\&quot;,         \&quot;submitted\&quot; : \&quot;2023-09-19\&quot;     }     ... ]  Fed by doing a server-&gt;server API query that returns essentially the union of: &gt;&gt;&gt; Document.objects.filter(states__type_id&#x3D;\&quot;draft-iesg\&quot;, ... states__slug__in&#x3D;[\&quot;approved\&quot;,\&quot;ann\&quot;]) &lt;QuerySet [     &lt;Document: draft-ietf-bess-pbb-evpn-isid-cmacflush&gt;,     &lt;Document: draft-ietf-dnssd-update-lease&gt;,     ... ]&gt; and &gt;&gt;&gt; Document.objects.filter(states__type_id__in&#x3D;[\&quot;draft-stream-iab\&quot;, ... \&quot;draft-stream-irtf\&quot;,\&quot;draft-stream-ise\&quot;],states__slug__in&#x3D;[\&quot;rfc-edit\&quot;]) &lt;QuerySet [     &lt;Document: draft-iab-m-ten-workshop&gt;,     &lt;Document: draft-irtf-cfrg-spake2&gt;,     ... ]&gt; and SOMETHING ABOUT THE EDITORIAL STREAM...  Those queries overreturn - there may be things, particularly not from the IETF stream that are already in the queue. This api will filter those out.

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { SubmissionsListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  try {
    const data = await api.submissionsList();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**Array&lt;SubmissionListItem&gt;**](SubmissionListItem.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## submissionsRetrieve

> Submission submissionsRetrieve(documentId)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { SubmissionsRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number
    documentId: 56,
  } satisfies SubmissionsRetrieveRequest;

  try {
    const data = await api.submissionsRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **documentId** | `number` |  | [Defaults to `undefined`] |

### Return type

[**Submission**](Submission.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## subseriesList

> Array&lt;SubseriesDoc&gt; subseriesList()



List all subseries

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { SubseriesListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  try {
    const data = await api.subseriesList();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**Array&lt;SubseriesDoc&gt;**](SubseriesDoc.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## subseriesMembersCreate

> SubseriesMember subseriesMembersCreate(subseriesMemberRequest)



ViewSet to track which RfcToBes have been assigned to which subseries

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { SubseriesMembersCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // SubseriesMemberRequest
    subseriesMemberRequest: ...,
  } satisfies SubseriesMembersCreateRequest;

  try {
    const data = await api.subseriesMembersCreate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **subseriesMemberRequest** | [SubseriesMemberRequest](SubseriesMemberRequest.md) |  | |

### Return type

[**SubseriesMember**](SubseriesMember.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## subseriesMembersDestroy

> subseriesMembersDestroy(id)



ViewSet to track which RfcToBes have been assigned to which subseries

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { SubseriesMembersDestroyRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number | A unique integer value identifying this subseries member.
    id: 56,
  } satisfies SubseriesMembersDestroyRequest;

  try {
    const data = await api.subseriesMembersDestroy(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **id** | `number` | A unique integer value identifying this subseries member. | [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | No response body |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## subseriesMembersList

> Array&lt;SubseriesMember&gt; subseriesMembersList(number, rfcToBe, type)



ViewSet to track which RfcToBes have been assigned to which subseries

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { SubseriesMembersListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number (optional)
    number: 56,
    // number (optional)
    rfcToBe: 56,
    // string (optional)
    type: type_example,
  } satisfies SubseriesMembersListRequest;

  try {
    const data = await api.subseriesMembersList(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **number** | `number` |  | [Optional] [Defaults to `undefined`] |
| **rfcToBe** | `number` |  | [Optional] [Defaults to `undefined`] |
| **type** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;SubseriesMember&gt;**](SubseriesMember.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## subseriesMembersPartialUpdate

> SubseriesMember subseriesMembersPartialUpdate(id, patchedSubseriesMemberRequest)



ViewSet to track which RfcToBes have been assigned to which subseries

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { SubseriesMembersPartialUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number | A unique integer value identifying this subseries member.
    id: 56,
    // PatchedSubseriesMemberRequest (optional)
    patchedSubseriesMemberRequest: ...,
  } satisfies SubseriesMembersPartialUpdateRequest;

  try {
    const data = await api.subseriesMembersPartialUpdate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **id** | `number` | A unique integer value identifying this subseries member. | [Defaults to `undefined`] |
| **patchedSubseriesMemberRequest** | [PatchedSubseriesMemberRequest](PatchedSubseriesMemberRequest.md) |  | [Optional] |

### Return type

[**SubseriesMember**](SubseriesMember.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## subseriesMembersRetrieve

> SubseriesMember subseriesMembersRetrieve(id)



ViewSet to track which RfcToBes have been assigned to which subseries

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { SubseriesMembersRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number | A unique integer value identifying this subseries member.
    id: 56,
  } satisfies SubseriesMembersRetrieveRequest;

  try {
    const data = await api.subseriesMembersRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **id** | `number` | A unique integer value identifying this subseries member. | [Defaults to `undefined`] |

### Return type

[**SubseriesMember**](SubseriesMember.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## subseriesRetrieve

> SubseriesDoc subseriesRetrieve(subseriesSlug)



Get all RfcToBe items in a specific subseries

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { SubseriesRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string
    subseriesSlug: subseriesSlug_example,
  } satisfies SubseriesRetrieveRequest;

  try {
    const data = await api.subseriesRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **subseriesSlug** | `string` |  | [Defaults to `undefined`] |

### Return type

[**SubseriesDoc**](SubseriesDoc.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## subseriesTypesList

> Array&lt;SubseriesTypeName&gt; subseriesTypesList()



ViewSet for SubseriesTypeName entries (read-only)

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { SubseriesTypesListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  try {
    const data = await api.subseriesTypesList();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**Array&lt;SubseriesTypeName&gt;**](SubseriesTypeName.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## subseriesTypesRetrieve

> SubseriesTypeName subseriesTypesRetrieve(slug)



ViewSet for SubseriesTypeName entries (read-only)

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { SubseriesTypesRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string | A unique value identifying this subseries type name.
    slug: slug_example,
  } satisfies SubseriesTypesRetrieveRequest;

  try {
    const data = await api.subseriesTypesRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **slug** | `string` | A unique value identifying this subseries type name. | [Defaults to `undefined`] |

### Return type

[**SubseriesTypeName**](SubseriesTypeName.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## tlpBoilerplateChoiceNamesList

> Array&lt;Name&gt; tlpBoilerplateChoiceNamesList()



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { TlpBoilerplateChoiceNamesListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  try {
    const data = await api.tlpBoilerplateChoiceNamesList();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**Array&lt;Name&gt;**](Name.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## tlpBoilerplateChoiceNamesRetrieve

> Name tlpBoilerplateChoiceNamesRetrieve(slug)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { TlpBoilerplateChoiceNamesRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // string | A unique value identifying this tlp boilerplate choice name.
    slug: slug_example,
  } satisfies TlpBoilerplateChoiceNamesRetrieveRequest;

  try {
    const data = await api.tlpBoilerplateChoiceNamesRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **slug** | `string` | A unique value identifying this tlp boilerplate choice name. | [Defaults to `undefined`] |

### Return type

[**Name**](Name.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## unusableRfcNumbersCreate

> UnusableRfcNumber unusableRfcNumbersCreate(unusableRfcNumberRequest)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { UnusableRfcNumbersCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // UnusableRfcNumberRequest
    unusableRfcNumberRequest: ...,
  } satisfies UnusableRfcNumbersCreateRequest;

  try {
    const data = await api.unusableRfcNumbersCreate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **unusableRfcNumberRequest** | [UnusableRfcNumberRequest](UnusableRfcNumberRequest.md) |  | |

### Return type

[**UnusableRfcNumber**](UnusableRfcNumber.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## unusableRfcNumbersDestroy

> unusableRfcNumbersDestroy(number)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { UnusableRfcNumbersDestroyRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number | A unique value identifying this unusable rfc number.
    number: 56,
  } satisfies UnusableRfcNumbersDestroyRequest;

  try {
    const data = await api.unusableRfcNumbersDestroy(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **number** | `number` | A unique value identifying this unusable rfc number. | [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | No response body |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## unusableRfcNumbersList

> Array&lt;UnusableRfcNumber&gt; unusableRfcNumbersList()



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { UnusableRfcNumbersListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  try {
    const data = await api.unusableRfcNumbersList();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**Array&lt;UnusableRfcNumber&gt;**](UnusableRfcNumber.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## unusableRfcNumbersPartialUpdate

> UnusableRfcNumber unusableRfcNumbersPartialUpdate(number, patchedUnusableRfcNumberRequest)



Allow PATCH operations only for the comment field

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { UnusableRfcNumbersPartialUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number | A unique value identifying this unusable rfc number.
    number: 56,
    // PatchedUnusableRfcNumberRequest (optional)
    patchedUnusableRfcNumberRequest: ...,
  } satisfies UnusableRfcNumbersPartialUpdateRequest;

  try {
    const data = await api.unusableRfcNumbersPartialUpdate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **number** | `number` | A unique value identifying this unusable rfc number. | [Defaults to `undefined`] |
| **patchedUnusableRfcNumberRequest** | [PatchedUnusableRfcNumberRequest](PatchedUnusableRfcNumberRequest.md) |  | [Optional] |

### Return type

[**UnusableRfcNumber**](UnusableRfcNumber.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## unusableRfcNumbersRetrieve

> UnusableRfcNumber unusableRfcNumbersRetrieve(number)



### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { UnusableRfcNumbersRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  const body = {
    // number | A unique value identifying this unusable rfc number.
    number: 56,
  } satisfies UnusableRfcNumbersRetrieveRequest;

  try {
    const data = await api.unusableRfcNumbersRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **number** | `number` | A unique value identifying this unusable rfc number. | [Defaults to `undefined`] |

### Return type

[**UnusableRfcNumber**](UnusableRfcNumber.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## version

> VersionInfo version()



Get application version information

### Example

```ts
import {
  Configuration,
  PurpleApi,
} from '';
import type { VersionRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new PurpleApi(config);

  try {
    const data = await api.version();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**VersionInfo**](VersionInfo.md)

### Authorization

[cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

