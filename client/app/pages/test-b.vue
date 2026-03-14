<template>
  <div>
    <h1>Test route (b) please ignore</h1>
    <p>This authenticated route is used to test the overhead of auth. It doesn't make any other API calls.</p>
    <p><Anchor href="/test-a" :class="ANCHOR_STYLE">go to test-a</Anchor></p>
  </div>
</template>

<script setup lang="ts">
import { ANCHOR_STYLE } from '../utils/html'
useHead({
  title: 'Test route (b)'
})
</script>
