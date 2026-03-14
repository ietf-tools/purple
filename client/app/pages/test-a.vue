<template>
  <div>
    <h1>Test route (a) please ignore</h1>
    <p>This authenticated route is used to test the overhead of auth. It doesn't make any other API calls.</p>
    <p><Anchor href="/test-b" :class="ANCHOR_STYLE">go to test-b</Anchor></p>
  </div>
</template>

<script setup lang="ts">
import { ANCHOR_STYLE } from '../utils/html'
useHead({
  title: 'Test route (a)'
})
</script>
