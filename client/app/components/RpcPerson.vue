<template>
  <span :class="ANCHOR_STYLE">
    {{ person === null ? 'loading...' : person?.name ? person.name : '(System)' }}
    {{  SPACE }}
  </span>
</template>

<script setup lang="ts">
import { SPACE } from '../utils/strings'
import type { RpcPerson } from '~/purple_client';

type Props = {
  personId?: number | null,
  people?: RpcPerson[],
}

const props = defineProps<Props>()

const person = computed(() => props.people ? props.people.find(p => p.id === props.personId) : null)
</script>
