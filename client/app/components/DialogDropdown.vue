<template>
  <fieldset class="mb-2 flex items-center gap-5">
    <label class="text-gray-900 w-[160px] text-right text-sm font-bold mr-1" :for="props.id"> {{ props.label }}:</label>
    <div>
      <SelectRoot :id="props.id" v-model="model">
        <SelectTrigger class="block flex justify-between gap-2 text-sm border border-gray-700 px-2 py-1.5 rounded-lg">
          <SelectValue :placeholder="props.placeholder ?? 'Choose...'">
            <span>{{ selectedOption?.label ?? props.placeholder ?? "Choose..." }}</span>
          </SelectValue>
          <span>
            <Icon name="fluent:arrow-bidirectional-up-down-24-filled" size="1.4em" />
          </span>
        </SelectTrigger>
        <SelectPortal>
          <SelectContent class="min-w-[160px] bg-white rounded-lg border shadow-lg z-[100]" :side-offset="5">
            <SelectViewport class="p-1">
              <SelectItem v-for="(option, index) in options" :value="option.value" :key="index"
                class="text-sm leading-none text-black rounded-md flex items-center px-8 py-3 relative select-none data-[disabled]:text-gray-400 data-[disabled]:pointer-events-none data-[highlighted]:outline-none data-[highlighted]:bg-gray-100 data-[highlighted]:text-black">
                <SelectItemText class="flex flex-col">
                  {{ option.label }}
                  <span v-if="option.description" class="text-xs text-gray-600">
                    {{ option.description }}
                  </span>
                </SelectItemText>
                <SelectItemIndicator>…</SelectItemIndicator>
              </SelectItem>
            </SelectViewport>
          </SelectContent>
        </SelectPortal>
      </SelectRoot>
    </div>
  </fieldset>
</template>

<script setup lang="ts">
import type { DialogOption } from '~/utils/dialog';

const model = defineModel<string>({ required: true })

type Props = {
  placeholder?: string
  id: string
  label: string
  options: DialogOption[]
}

const props = defineProps<Props>()

const selectedOption = computed(()=> props.options.find(option => option.value === model.value))

</script>
