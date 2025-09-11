<script setup lang="ts">
definePageMeta({
  middleware: [
    function (to, from) {
      return navigateTo('/auth48/inprogress')
    }
  ]
})
</script>
