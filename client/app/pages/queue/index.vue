<script setup lang="ts">
definePageMeta({
  middleware: [
    function () {
      return navigateTo('/queue/queue')
    }
  ]
})
</script>
