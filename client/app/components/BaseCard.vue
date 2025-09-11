<template>
  <div class="rounded-lg bg-white shadow">
    <slot name="header"/>
    <div class="px-4 py-5 sm:p-6">
      <slot/>
    </div>
    <slot name="footer"/>
  </div>
</template>

<script setup lang="ts">

</script>
