<template>
  <div class="rounded-lg text-black bg-white dark:text-white dark:bg-black dark:border dark:border-gray-200 shadow">
    <slot name="header"/>
    <div class="px-4 py-5 sm:p-6">
      <slot/>
    </div>
    <slot name="footer"/>
  </div>
</template>
