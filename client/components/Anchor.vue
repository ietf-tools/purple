<template>
  <NuxtLink
    v-if="isInternal && !isHash && !isMailTo"
    v-bind="sanitisedAnchorProps"
    data-link-type="nuxt-link"
  >
    <slot />
  </NuxtLink>
  <a
    v-else
    v-bind="sanitisedAnchorProps"
    data-link-type="html-anchor"
  >
    <slot />
  </a>
</template>

<script setup lang="ts">
/**
 * An anchor hyperlink that detects whether to use SPA Vue Router or a conventional hyperlink.
 *
 * If the link is external then target="_blank" and rel="noopener" will be added.
 *
 */
import { computed } from 'vue'
import { EXTERNAL_LINK_REL, TARGET_NEW_WINDOW } from '~/utilities/html'
import { isHashLink, isInternalLink, isMailToLink, isOidcLink } from '~/utilities/url'

type Props = { href?: string; id?: string }

const props = defineProps<Props>()

const isInternal = computed(() => isInternalLink(props.href))
const isOidc= computed(() => isOidcLink(props.href))
const isMailTo = computed(() => isMailToLink(props.href))
const isHash = computed(() => isHashLink(props.href))

const sanitisedAnchorProps = computed(() => {
  const isNuxtLink =
    props.href && isInternal.value && !isMailTo.value && !isHash.value && !isOidc.value
  const isExternalLink =
    props.href && !isInternal.value && !isMailTo.value && !isHash.value && !isOidc.value

  return {
    ...props,
    to: isNuxtLink ? props.href : undefined, // copy `href` to `to` for NuxtLink
    href: isNuxtLink ? undefined : props.href, // clobber 'href' with `undefined` when it's a NuxtLink
    rel: isExternalLink ? EXTERNAL_LINK_REL : undefined,
    target: isExternalLink ? TARGET_NEW_WINDOW : undefined
  }
})
</script>
