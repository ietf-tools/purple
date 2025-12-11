<template>
  {{ person === null ? 'loading...' : person?.name ? `${person.name} ${person.id ? `#${person.id}` : ''}` : '(System)' }}
</template>

<script setup lang="ts">
import type { RpcPerson } from '~/purple_client';

type Props = {
  personId: number,
  people?: RpcPerson[],
}

const props = defineProps<Props>()

const person = computed(() => props.people ? props.people.find(p => p.id === props.personId) : null)
</script>
