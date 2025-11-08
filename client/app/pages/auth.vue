<template>
  <div class="w-full h-full min-h-screen bg-gray-200 pt-10">
    <div class="bg-white mx-auto max-w-lg text-center rounded-xl border border-gray-300 shadow-m">
      <h1 class="text-xl font-bold pt-3 pb-2 border-b text-gray-700">You're not logged in</h1>
      <div class="py-10">
        <Anchor :href="`/oidc/authenticate/${nextParam}`" class="mx-auto w-[15em] flex justify-between items-center border bg-sky-900 px-4 py-2 text-white dark:text-neutral-300">
          <span class="font-semibold">Login via Datatracker</span>
          <Icon name="solar:alt-arrow-right-line-duotone" size="1.5em" class="ml-1" />
        </Anchor>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useDefaultHead } from '~/utils/head'

const route = useRoute()

// mozilla_django_oidc supports a url param `next` to return to the current path https://mozilla-django-oidc.readthedocs.io/en/stable/settings.html?highlight=next#OIDC_REDIRECT_FIELD_NAME
const nextParam = computed(() => {
  const { next } = route.query
  return typeof next === 'string' ? `?next=${encodeURIComponent(next)}` : ''
})

useDefaultHead()

definePageMeta({
  layout: false,
})

</script>
