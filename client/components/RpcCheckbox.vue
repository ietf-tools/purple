<template>
  <div :class="['relative flex items-start', props.class]">
    <div class="flex h-6 items-center">
      <input
        v-bind="$attrs"
        ref="input-element"
        :id="inputId"
        :aria-describedby="desc ? descriptionId : undefined"
        :checked="checked"
        type="checkbox"
        @change="handleChange"
        :class="[caution ? 'border-rose-300 dark:border-rose-500 text-rose-700 dark:text-rose-700 hover:border-rose-400 focus:ring-rose-600' : 'border-gray-300 dark:border-neutral-500 text-violet-600 dark:text-violet-500 hover:border-violet-400 dark:hover:border-violet-500 focus:ring-violet-600 dark:focus:ring-violet-500', 'h-4 w-4 bg-white dark:bg-neutral-900 rounded border-2']"
      >
    </div>
    <div :class="{
      'ml-3 leading-6': true,
      'text-sm': props.size === 'medium',
      'text-xs': props.size === 'small',
    }">
      <label
        :for="inputId"
        :class="[caution ? 'text-rose-800 dark:text-rose-400' : 'text-gray-900 dark:text-neutral-200', 'font-medium']">
        {{ label }}
      </label>
      <p
        v-if="desc"
        :id="descriptionId"
        :class="[caution ? 'text-rose-700 dark:text-rose-500' : 'text-gray-500 dark:text-neutral-400', 'text-xs']">
        {{ desc }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { watch, useAttrs, onMounted } from 'vue'
import { CHECKBOX_INDETERMINATE } from '~/utilities/checkbox'
import type { VueStyleClass } from '~/utilities/vue'

// Fallthrough attributes are applied to an internal element via v-bind="$attrs"
defineOptions({ inheritAttrs: false })

type Props = {
  caution?: boolean
  desc?: string
  id?: string
  label: string
  class?: VueStyleClass
  size?: 'medium' | 'small'
  checked: CheckboxTristate
  hasIndeterminate?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  caution: false,
  desc: undefined,
  id: undefined,
  size: 'medium'
})

const componentId = useId()

// COMPUTED

const inputId = computed(() => props.id || componentId)
const descriptionId = computed(() => props.desc && `${inputId.value}-desc`)
const attrs = useAttrs()
const inputElementRef = useTemplateRef('input-element')
const checkCounter = ref<number>(props.hasIndeterminate && props.checked === CHECKBOX_INDETERMINATE ? 2 : props.checked ? 1 : 0)

const setIndeterminate = () => {
  if(!props.hasIndeterminate) {
    throw Error('Cannot set indeterminate without has-indeterminate prop')
  }
  const { value: inputElement } = inputElementRef
  if(!inputElement) {
    throw Error('Unable to get checkbox element from ref. This is a bug.')
  }
  // enable tri-state checkbox
  inputElement.indeterminate = true
}

const handleChange = (e: Event) => {
  const { onChange } = attrs
  if(!onChange) {
    console.warn('No @change handler on rpcCheckbox')
    return
  }
  if(props.hasIndeterminate) {
    // use our internal state instead of event.target.checked state
    checkCounter.value++
    // Use modulus to track clicks
    // mod3 === 0 is false
    // mod3 === 1 is true
    // mod3 === 2 is indeterminate see
    // https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/indeterminate
    const mod3 = checkCounter.value % 3

    onChange(mod3 === 2 ? CHECKBOX_INDETERMINATE : Boolean(mod3))
    if(mod3 === 2) {
      setIndeterminate()
    }
  } else {
    onChange(e)
  }
}

onMounted(() => {
  if(props.checked !== CHECKBOX_INDETERMINATE) {
    return
  }
  setIndeterminate()
})
</script>
