<template>
  <table class="w-full border-collapse text-sm">
    <thead>
      <tr>
        <th class="border-b border-gray-300 p-2 text-left text-xs">{{ props.columns.nameColumn }}</th>
        <th class="border-b border-gray-300 p-2 text-left text-xs">{{ props.columns.leftColumn }}</th>
        <th class="border-b border-gray-300 p-2"></th>
        <th class="border-b border-gray-300 p-2 text-left text-xs">{{ props.columns.rightColumn }}</th>
      </tr>
    </thead>
    <tbody>
      <template v-if="computedRows.length === 0">
        <tr>
          <td colspan="4" class="text-center italic py-5">No rows</td>
        </tr>
      </template>
      <template v-for="(row, index) in computedRows" :key="index">
        <tr :class="{
          [badgeColors.green]: row.rowValue.isMatch,
          [yellowBackground]: !row.rowValue.isMatch && !row.rowValue.isError,
          [badgeColors.red]: !row.rowValue.isMatch && row.rowValue.isError,
        }">
          <td class="p-2" :style="row.rowNameListDepth > 0 && `padding-left: ${row.rowNameListDepth}rem`">
            <template v-if="row.rowNameListDepth > 0">&bull;</template>
            {{ row.rowName }}
          </td>
          <td class="p-2">
            <component :is="row.renderableLeftValue ?? emptySpan" />
          </td>
          <td class="align-middle">
            <Icon v-if="row.rowValue.isMatch" name="ic:outline-equals" size="1rem" aria-label="=" title="=" />
            <Icon v-else name="ic:outline-not-equal" size="1rem" aria-label="!=" title="!=" />
          </td>
          <td class="p-2">
            <component :is="row.renderableRightValue ?? emptySpan" />
          </td>
        </tr>
        <tr v-if="row.rowValue.detail && row.rowValue.detail.length > 0">
          <td colspan="4" :class="[yellowBackground, 'px-3 py-2']">
            <Icon name="uil:info-circle" size="0.8rem" class="mr-2 align-middle" />
            {{ row.rowValue.detail }}
          </td>
        </tr>
      </template>
    </tbody>
  </table>
</template>

<script setup lang="ts">
import type { DiffRow, DiffColumns } from '../utils/difftable'

type Props = {
  columns: DiffColumns
  rows: DiffRow[]
}

const yellowBackground = 'bg-yellow-200 text-yellow-900 dark:bg-yellow-500 dark:text-yellow-900'

const emptySpan = h('span')

const props = defineProps<Props>()

type RenderableRow = DiffRow & {
  renderableLeftValue: ReturnType<typeof h>
  renderableRightValue: ReturnType<typeof h>
}

const invalidCharAttribute = { class: "bg-red-900 dark:bg-red-950 text-white" }

const computedRows = computed((): RenderableRow[] => {
  return props.rows.map(row => {

    const targetLength = Math.max(row.rowValue.leftValue?.length ?? 0, row.rowValue.rightValue.length ?? 0)

    const leftValueString = `${(row.rowValue.leftValue).padEnd(targetLength)}`
    const renderableLeftValue = h('span', leftValueString.split('').map((leftChar, index) => {
      const rightChar = leftValueString.charAt(index)
      const isSame = leftChar !== rightChar
      const isWhitespace = leftChar.match(/\s/)
      return h('span', isSame ? invalidCharAttribute : {}, !isSame && isWhitespace ? `${NBSP} ` : leftChar ?? '')
    }))

    const rightValueString = `${(row.rowValue.rightValue).padEnd(targetLength)}`

    const renderableRightValue = h('span', rightValueString.split('').map((rightChar, index) => {
      const leftChar = rightValueString.charAt(index)
      const isSame = leftChar !== rightChar
      const isWhitespace = rightChar.match(/\s/)
      return h('span', isSame ? invalidCharAttribute : {}, !isSame && isWhitespace ? `${NBSP} ` : rightChar ?? '')
    }))

    return {
      ...row,
      renderableLeftValue,
      renderableRightValue
    }
  })
})

</script>
