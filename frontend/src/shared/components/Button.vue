<script setup lang="ts">
import { computed } from 'vue';

// tipo aceito para as variantes do botão
type ButtonVariant = 'primary' | 'secondary' | 'tertiary';

const props = withDefaults(
  defineProps<{
    variant?: ButtonVariant;
    type?: 'button' | 'submit' | 'reset';
    disabled?: boolean;
    loading?: boolean; // adicionei loading para caso precise no futuro.
  }>(),
  {
    variant: 'primary',
    type: 'button',
    disabled: false,
    loading: false,
  }
);

// propriedade computed
// gerencia as classes baseadas na variante escolhida
const buttonClass = computed(() => {
  // Tratamento de estado desabilitado global para as variantes
  if (props.disabled || props.loading) {
    if (props.variant === 'primary') return 'rounded-full bg-govbr-border px-5 py-2 text-sm text-white cursor-not-allowed';
    if (props.variant === 'secondary') return 'rounded-full border border-govbr-border px-4 py-1.5 text-sm text-govbr-text-secondary cursor-not-allowed';
    return 'px-4 py-2 rounded text-sm text-govbr-text-secondary cursor-not-allowed';
  }

  // Mapeamento das classes
  switch (props.variant) {
    case 'primary':
      return 'rounded-full bg-govbr-primary px-5 py-2 text-sm text-white hover:bg-govbr-primary-hover';
    case 'secondary':
      return 'rounded-full border border-govbr-primary px-4 py-1.5 text-sm text-govbr-primary hover:bg-govbr-bg';
    case 'tertiary':
      return 'text-sm text-govbr-primary hover:underline px-4 py-2 rounded hover:bg-gray-100';
    default:
      return 'rounded-full bg-govbr-primary px-5 py-2 text-sm text-white';
  }
});
</script>

<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="buttonClass"
    class="flex gap-[0.8rem] items-center justify-center text-[16.8px] transition duration-150 ease-in-out font-bold focus:outline-none cursor-pointer"
  >
    <span v-if="$slots.icon" class="flex shrink-0 items-center justify-center">
      <slot name="icon"></slot>
    </span>
    
    <slot></slot>
  </button>
</template>