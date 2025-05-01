import { defineStore } from 'pinia'
import { LOGIN_PATH, onLoginRoute } from '~/utilities/url'

export type ProfileData = {
  /**
   * Until we fetch their profile their authentication state is unknown which we'll express as `undefined`
   */
  authenticated: undefined | boolean
  id: string | null
  name: string | null
  email: string | null
  avatar: string | null
  rpcPersonId: number | null
  isManager: boolean
}

type PretendingToBe = {
  pretendingToBe: number | null
}

type State = ProfileData & PretendingToBe

const getCurrentRelativePath = (): string => {
  const locationStr = location.toString() // stringify the whole URL including path, query params, hash
  const relativePath = locationStr.substring(locationStr.indexOf(location.host) + location.host.length)
  return relativePath
}

export const useUserStore = defineStore('user', {
  state: () => {
    const defaultState: State = {
      authenticated: undefined,
      id: null,
      name: '',
      email: '',
      avatar: '',
      rpcPersonId: null,
      isManager: false,
      pretendingToBe: null // demo/debug only! FIXME: disallow on prod?
    }
    return defaultState
  },
  getters: {},
  actions: {
    async refreshAuth () {
      const profileData = await $fetch<ProfileData>(
        this.pretendingToBe
          ? `/api/rpc/profile/${this.pretendingToBe}`
          : '/api/rpc/profile/'
      ).catch(e => {
        console.error('Error loading profile', e)
      })

      const isOnLoginPageAlready = onLoginRoute(location.pathname)
      if (!isOnLoginPageAlready && (!profileData || profileData.authenticated === false)) {
        console.log(isOnLoginPageAlready, location.pathname)
        navigateTo(`${LOGIN_PATH}${!isOnLoginPageAlready ? `?next=${encodeURIComponent(getCurrentRelativePath())}` : ''}`)
        return
      }

      if (!profileData) {
        return
      }

      this.authenticated = profileData.authenticated
      if (profileData.authenticated === true) {
        this.id = profileData.id
        this.name = profileData.name
        this.email = profileData.email
        this.avatar = profileData.avatar
        this.rpcPersonId = profileData.rpcPersonId
        this.isManager = profileData.isManager
      }
    },
    async pretendToBe (rpcPersonId: number | null) {
      this.pretendingToBe = rpcPersonId
      return await this.refreshAuth()
    }
  }
})
