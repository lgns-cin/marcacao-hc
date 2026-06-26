<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
    type?: "button" | "submit" | "reset"
    disabled?: boolean
}>();

const buttonClass = computed(() => {
    if (props.disabled) return "bg-dark-blue-transparent"

    return ""
})

</script>

<template>
    <button
        :class="[buttonClass, { 'cursor-not-allowed': props.disabled }]"
        :disabled="props.disabled"
        :type="props.type || 'button'"
        class="
            flex flex-col items-center justify-center
            gap-4 px-3 py-2 rounded-xl bg-dark-blue 
            text-white font-semibold text-3xl
            hover:bg-dark-blue-transparent
            transition duration-100 ease-in-out
        "
    >
        <div class="flex text-white font-semibold text-[32px] gap-4">
            <slot></slot>
        </div>
        <slot name="icon"></slot>
    </button>
</template>