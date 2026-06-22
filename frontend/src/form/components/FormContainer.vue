<template>
    <div class="flex flex-col max-w-[328px] gap-4 px-2.5 py-4 rounded-xl bg-white">
        <div class="flex flex-col gap-4 text-dark-blue font-medium text-2xl">
            <slot name="contents"></slot>
        </div>
        <div class="grid grid-cols-none grid-flow-col auto-cols-auto gap-2">
            <slot name="buttons"></slot>
        </div>
    </div>
</template>