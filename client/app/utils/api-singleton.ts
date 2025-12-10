import { PurpleApi } from '~/purple_client'

const api = useApi()

const apiSingletonWrapper = <T extends keyof PurpleApi>(method: T) => {
  type ResponsePromise = ReturnType<PurpleApi[T]>
  type Params = Parameters<PurpleApi[T]>

  const promiseCache: Record<string, ResponsePromise> = {}

  return (...params: Params) => {
    const cacheKey = JSON.stringify(
      // normalize object (ie, sort keys deep) before using JSON.stringify() to generate a unique key
      deepSortObject(params))
    if (!promiseCache[cacheKey]) {
      // @ts-ignore
      promiseCache[cacheKey] = api[method](...params)
    }
    const maybePromise = promiseCache[cacheKey]
    if (maybePromise === undefined) {
      throw Error("Internal error this shouldn't happen")
    }
    return maybePromise
  }
}

export const documentsRetrieveSingleton = apiSingletonWrapper('documentsRetrieve')

export const rpcPersonListSingleton = apiSingletonWrapper('rpcPersonList')

export const mailtemplateListSingleton = apiSingletonWrapper('mailtemplateList')

export const assignmentsListSingleton = apiSingletonWrapper('assignmentsList')

export const rfcAssignmentsListSingleton = async (rfcToBeId: number) => {
  const assignments = await assignmentsListSingleton()
  return assignments.filter((a) => a.rfcToBe === rfcToBeId)
}

export const labelsListSingleton = apiSingletonWrapper('labelsList')
