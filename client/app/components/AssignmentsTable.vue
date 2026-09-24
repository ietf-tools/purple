<template>
  <RpcTable>
    <RpcThead>
      <tr v-for="headerGroup in table.getHeaderGroups()" :key="headerGroup.id">
        <RpcTh
          v-for="header in headerGroup.headers"
          :key="header.id"
          :colSpan="header.colSpan"
          :is-sortable="header.column.getCanSort()"
          :sort-direction="header.column.getIsSorted()"
          :column-name="getVNodeText(header.column.columnDef.header)"
          @click="header.column.getToggleSortingHandler()?.($event)">
          <div class="flex items-center gap-2">
            <FlexRender
              v-if="!header.isPlaceholder"
              :render="header.column.columnDef.header"
              :props="header.getContext()" />
          </div>
        </RpcTh>
      </tr>
    </RpcThead>
    <RpcTbody>
      <tr v-for="row in table.getRowModel().rows" :key="row.id">
        <RpcTd v-for="cell in row.getVisibleCells()" :key="cell.id">
          <FlexRender :render="cell.column.columnDef.cell" :props="cell.getContext()" />
        </RpcTd>
      </tr>
    </RpcTbody>
  </RpcTable>
</template>

<script setup lang="ts" generic="T">
import { FlexRender, type Table } from '@tanstack/vue-table'

defineProps<{ table: Table<T> }>()
</script>
