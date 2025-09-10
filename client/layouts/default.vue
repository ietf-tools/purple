<template>
  <div>
    <SidebarNav />
    <main class="lg:pl-72">
      <HeaderNav />
      <div class="px-4 py-10 sm:px-6 lg:px-8 lg:py-6">
        <slot  />
      </div>
    </main>
    <OverlayModal
      v-model:is-shown="overlayModalState.isShown"
      :opts="overlayModalState.opts"
      @close-ok="overlayModalState.promiseResolve"
      @close-cancel="overlayModalState.promiseReject"
    />
    <NuxtSnackbar />
  </div>
</template>

<script setup lang="ts">
import { useDefaultHead } from '~/utils/head'
import { overlayModalKey } from '../providers/providerKeys'
import type { OverlayModal } from '../providers/providerKeys'

useDefaultHead()

// OVERLAY MODAL

type OverlayModalState = {
  isShown: boolean
  opts: Parameters<OverlayModal['openOverlayModal']>[0]
  promiseResolve?: (value?: string | PromiseLike<string | undefined>) => void
  promiseReject?: (reason?: any) => void
}

const overlayModalState = shallowReactive<OverlayModalState>({
  isShown: false,
  opts: {
    component: undefined,
    componentProps: undefined
  },
  promiseResolve: undefined,
  promiseReject: undefined
})

provide(overlayModalKey, {
  openOverlayModal: (opts) => {
    overlayModalState.opts = {
      component: opts.component,
      componentProps: opts.componentProps ?? {},
      mode: opts.mode ?? 'overlay'
    }
    return new Promise<string | undefined>((resolve, reject) => {
      overlayModalState.promiseResolve = resolve
      overlayModalState.promiseReject = reject
      overlayModalState.isShown = true
    })
  },
  /**
   * Close the active overlay modal
   */
  closeOverlayModal: () => {
    if (overlayModalState.promiseReject) {
      overlayModalState.isShown = false
      overlayModalState.promiseReject()
    }
  }
})
</script>

<style lang="scss">
:root { font-family: 'Inter', sans-serif; }
@supports (font-variation-settings: normal) {
  :root { font-family: 'Inter var', sans-serif; }
}

body {
  background-color: #f9fafb;
}
.dark body {
  background-color: #0a0a0a;
}
</style>
