import type { VNode } from 'vue'
import type { ColorEnum } from '~/purple_client'

export type Value = unknown

export type Row = Record<string, Value>

export interface Column {
  key: string
  label: string
  labels?: (row: Row) => string[]
  labelDefaultColor?: ColorEnum
  field?: string
  classes?: string | ((val: Value) => string)
  sortable?: boolean
  link?: string | ((row: Row, val: Value) => string)
  formatType?: 'all'
  format?: (value: Value) => VNode | VNode[] | string
  icon?: string
}

export interface Table {
  columns: Column[]
  rows: Row[]
}
