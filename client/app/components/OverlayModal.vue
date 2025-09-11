<template>
  <HeadlessTransitionRoot as="template" :show="isShown">
    <HeadlessDialog as="div" class="relative z-50" @close="close">
      <!-- Background -->
      <HeadlessTransitionChild as="template" enter="ease-in-out duration-500" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in-out duration-500" leave-from="opacity-100" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500 dark:bg-black bg-opacity-75 dark:bg-opacity-50 transition-opacity backdrop-blur-sm" />
      </HeadlessTransitionChild>
      <!-- MODE: Side -->
      <div v-if="opts.mode === `side`" class="fixed inset-0 overflow-hidden">
        <div class="absolute inset-0 overflow-hidden">
          <div class="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10 sm:pl-16">
            <HeadlessTransitionChild as="template" enter="transform transition ease-in-out duration-500 sm:duration-700" enter-from="translate-x-full" enter-to="translate-x-0" leave="transform transition ease-in-out duration-500 sm:duration-700" leave-from="translate-x-0" leave-to="translate-x-full">
              <HeadlessDialogPanel class="pointer-events-auto w-screen max-w-2xl">
                <component :is="opts.component" v-bind="opts.componentProps" />
              </HeadlessDialogPanel>
            </HeadlessTransitionChild>
          </div>
        </div>
      </div>
      <!-- MODE: Overlay (default) -->
      <div v-else class="fixed inset-0 z-10 w-screen overflow-y-auto p-4 sm:p-6 md:px-20 md:py-10">
        <HeadlessTransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 scale-95" enter-to="opacity-100 scale-100" leave="ease-in duration-200" leave-from="opacity-100 scale-100" leave-to="opacity-0 scale-95">
          <HeadlessDialogPanel class="mx-auto h-full transform divide-y divide-gray-100 overflow-hidden rounded-xl bg-white dark:bg-neutral-800 shadow-2xl ring-1 ring-black ring-opacity-5 transition-all">
            <component :is="opts.component" v-bind="opts.componentProps" />
          </HeadlessDialogPanel>
        </HeadlessTransitionChild>
      </div>
    </HeadlessDialog>
  </HeadlessTransitionRoot>
</template>

<script setup lang="ts">
import type { OverlayModal } from '../providers/providerKeys'
import { overlayModalMethodsKey } from '../providers/providerKeys'
// PROPS / EMITS

type Props = {
  opts: Parameters<OverlayModal['openOverlayModal']>[0]
  isShown: boolean
}

const props = withDefaults(defineProps<Props>(), {
  opts: () => ({}),
  isShown: false
})

const emit = defineEmits<{
  'update:isShown': [isShown: boolean]
  closeOk: [value?: string]
  closeCancel: [reason?: any]
}>()

// PROVIDE

provide(overlayModalMethodsKey, {
  ok: (val?: string) => {
    emit('update:isShown', false)
    emit('closeOk', val)
  },
  cancel: (val?: string) => {
    emit('update:isShown', false)
    emit('closeCancel', val)
  }
})

// METHODS

function close () {
  emit('update:isShown', false)
  emit('closeCancel')
}

</script>

<docs>
## Usage

The `OverlayModal` component lives at the root of the Vue app. It provides an `overlayModal` set of methods to launch and close a modal.

### Create New Component

You must first create a component with the contents of the modal. In this example, we'll name the component `EditUserModal.vue`. Make sure to add at least a close button, which would call either the `ok` or `cancel` methods as shown below.

You must inject methods from `overlayModalMethods` to control the dialog:

```
<script setup lang="ts">
import { overlayModalMethodsKey } from '../providers/providerKeys'

const { ok, cancel } = inject(overlayModalMethodsKey)

function save () {
  // do some logic
  ok()
}

function close () {
  cancel()
}

</script>
```

### Trigger Your Modal

From the page you want to trigger the modal, import the component you just created and inject the methods from `overlayModal`

```
<script setup lang="ts">
  import { overlayModalKey } from '../providers/providerKeys'
  import { UserEditModal } from '#components'

  const { openOverlayModal } = inject(overlayModalKey)

  function editUser (userId) {
    openOverlayModal({
      component: UserEditModal,
      componentProps: {
        id: userId
      }
    })
  }
</script>
```

In the above example, the property `component` refers to the component to display in the modal frame, while the property `componentProps` is an object of properties to bind to the component.

You can also close the modal from the trigger context using the injected method `closeOverlayModal`, e.g.:

```
<script setup lang="ts">
  import { overlayModalKey } from '../providers/providerKeys'
  import { UserEditModal } from '#components'

  const { openOverlayModal, closeOverlayModal } = inject(overlayModalKey)

  function editUser (userId) {
    openOverlayModal({
      component: UserEditModal,
      componentProps: {
        id: userId
      }
    })

    // automatically close after 5 seconds
    setTimeout(() => {
      closeOverlayModal()
    }, 5000)
  }
</script>
```

## Display Options

You can display a modal on the right side of the screen by setting `mode: 'side'` when calling `openOverlayModal()`:

```
openOverlayModal({
  component: UserEditModal,
  componentProps: {
    id: userId
  },
  mode: 'side'
})
```

If omitted, the default is `overlay`.

## Modal Lifecycle

To perform actions after the modal is closed or to pass data back to the context that triggered the modal, you can await the `openOverlayModal` method (which returns a promise).

- Calling `ok()` from the dialog will resolve the promise (with any data passed as an argument).
- Calling `cancel()` from the dialog will reject the promise.

Example usage:

```
async function editUser (userId) {
  try {
    const result = await openOverlayModal({
      component: UserEditModal,
      componentProps: {
        id: userId
      }
    })
    // result = data passed to ok(), e.g. ok({ success: true })
  } catch (err) {
    // the cancel() method was called
  }
}
```
</docs>
