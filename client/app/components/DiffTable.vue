<template>
  <table class="w-full border-collapse text-sm">
    <thead>
      <tr>
        <th class="border-b border-gray-300 p-2 text-left text-xs">Name</th>
        <th class="border-b border-gray-300 p-2 text-left text-xs">Database</th>
        <th class="border-b border-gray-300 p-2"></th>
        <th class="border-b border-gray-300 p-2 text-left text-xs">Document</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="row in computedRows" :class="{
        [badgeColors.red]: !row.isMatch,
        [badgeColors.green]: row.isMatch,
      }">
        <td class="p-2" :style="row.rowNameListDepth > 0 && `padding-left: ${row.rowNameListDepth}rem`">
          <template v-if="row.rowNameListDepth > 0">&bull;</template>
          {{ row.rowName }}
        </td>
        <td class="p-2">
          <component :is="row.leftValue"/>
        </td>
        <td class="align-middle">
          <Icon v-if="!row.isMatch" name="ic:outline-not-equal" size="1rem" aria-label="!=" title="!=" />
          <Icon v-if="row.isMatch" name="ic:outline-equals" size="1rem" aria-label="=" title="="/>
        </td>
        <td class="p-2">
          <component :is="row.rightValue"/>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
type Row = { rowName: string, rowNameListDepth: number, leftValue?: string, rightValue?: string }

type Props = {
  columns: { nameColumn: string, leftColumn: string, rightColumn: string }
  rows: Row[]
}

const props = defineProps<Props>()

type RenderableRow = {
  rowName: string
  rowNameListDepth: number
  isMatch: boolean
  leftValue: ReturnType<typeof h>
  rightValue: ReturnType<typeof h>
}

const invalidCharAttribute = { class: "bg-red-900 dark:bg-red-950 text-white" }

const computedRows = computed((): RenderableRow[] => {
  return props.rows.map(row => {
    const targetLength = Math.max(row.leftValue?.length ?? 0, row.rightValue?.length ?? 0)
    const leftValue = `${(row.leftValue ?? '').padEnd(targetLength)}`
    const rightValue = `${(row.rightValue ?? '').padEnd(targetLength)}`
    return {
      rowName: row.rowName,
      rowNameListDepth: row.rowNameListDepth,
      isMatch: row.leftValue === row.rightValue,
      leftValue: h('span', leftValue.split('').map((leftChar, index) => {
        const rightChar = rightValue.charAt(index)
        const isSame = leftChar !== rightChar
        const isWhitespace = leftChar.match(/\s/)
        return h('span', isSame ? invalidCharAttribute : undefined, !isSame && isWhitespace ? `${NBSP} ` : leftChar)
      })),
      rightValue: h('span', rightValue.split('').map((rightChar, index) => {
        const leftChar = leftValue.charAt(index)
        const isSame = leftChar !== rightChar
        const isWhitespace = rightChar.match(/\s/)
        return h('span', isSame ? invalidCharAttribute : undefined, !isSame && isWhitespace ? `${NBSP} ` : rightChar)
      }))
    }
  })
})

</script>
