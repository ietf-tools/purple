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
        [badgeColors.red]: row.value && !row.value.isMatch,
        [badgeColors.green]: row.value && row.value.isMatch,
      }">
        <td class="p-2" :style="row.rowNameListDepth > 0 && `padding-left: ${row.rowNameListDepth}rem`">
          <template v-if="row.rowNameListDepth > 0">&bull;</template>
          {{ row.rowName }}
        </td>
        <td class="p-2">
          <component :is="row.value?.leftValue ?? emptySpan"/>
        </td>
        <td class="align-middle">
          <Icon v-if="row.value && !row.value.isMatch" name="ic:outline-not-equal" size="1rem" aria-label="!=" title="!=" />
          <Icon v-if="row.value && row.value.isMatch" name="ic:outline-equals" size="1rem" aria-label="=" title="="/>
        </td>
        <td class="p-2">
          <component :is="row.value?.rightValue ?? emptySpan"/>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
type Row = {
  rowName: string,
  rowNameListDepth: number,
  value?: { isMatch: boolean, leftValue: string, rightValue: string }
}

type Props = {
  columns: { nameColumn: string, leftColumn: string, rightColumn: string }
  rows: Row[]
}

const emptySpan = h('span')

const props = defineProps<Props>()

type RenderableRow = {
  rowName: string
  rowNameListDepth: number
  value?: {
    isMatch: boolean
    leftValue: ReturnType<typeof h>
    rightValue: ReturnType<typeof h>
  }
}

const invalidCharAttribute = { class: "bg-red-900 dark:bg-red-950 text-white" }

const computedRows = computed((): RenderableRow[] => {
  return props.rows.map(row => {
    if(!row.value) {
      return {
        rowName: row.rowName,
        rowNameListDepth: row.rowNameListDepth,
      }
    }
    const targetLength = Math.max(row.value.leftValue?.length ?? 0, row.value.rightValue.length ?? 0)
    const leftValue = `${(row.value.leftValue).padEnd(targetLength)}`
    const rightValue = `${(row.value.rightValue).padEnd(targetLength)}`
    return {
      rowName: row.rowName,
      rowNameListDepth: row.rowNameListDepth,
      value: {
        isMatch: row.value.isMatch,
        leftValue: h('span', leftValue.split('').map((leftChar, index) => {
          const rightChar = rightValue.charAt(index)
          const isSame = leftChar !== rightChar
          const isWhitespace = leftChar.match(/\s/)
          return h('span', isSame ? invalidCharAttribute : {}, !isSame && isWhitespace ? `${NBSP} ` : leftChar ?? '')
        })),
        rightValue: h('span', rightValue.split('').map((rightChar, index) => {
          const leftChar = leftValue.charAt(index)
          const isSame = leftChar !== rightChar
          const isWhitespace = rightChar.match(/\s/)
          return h('span', isSame ? invalidCharAttribute : {}, !isSame && isWhitespace ? `${NBSP} ` : rightChar ?? '')
        }))
      }
    }
  })
})

</script>
