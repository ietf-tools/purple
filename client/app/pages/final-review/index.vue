<template>
  <div>
    <TitleBlock
      title="Final Review (formerly AUTH48)"
      summary="Where the magic mercifully stops happening."/>

    <FinalReviewInProgress />
    <FinalReviewDone />
    <FinalReviewForPublication />
  </div>
</template>

<script setup lang="ts">

const api = useApi()

api.final

</script>
