<template>
  <button type="button" :class="[classForBtnType[props.btnType], sizeClasses]">
    <slot />
  </button>
</template>

<script setup lang="ts">
import { classForBtnType, classesForBtnSize,  } from '../utils/button'

type Props = {
  btnType?: keyof (typeof classForBtnType),
  size?: keyof (typeof classesForBtnSize)
}

const props = withDefaults(defineProps<Props>(), { btnType: 'default', size: 'sm' })

const sizeClasses = computed(() => classesForBtnSize[props.size])

</script>
