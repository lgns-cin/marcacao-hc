<script setup lang="ts">
// Tipo aceito para as variantes do botão
type ButtonVariant = 'primary' | 'secondary' | 'tertiary';

// Propriedades do componente com valores padrão
withDefaults(
  defineProps<{
    variant?: ButtonVariant;
    type?: 'button' | 'submit' | 'reset';
    disabled?: boolean;
  }>(),
  {
    variant: 'primary',
    type: 'button',
    disabled: false,
  }
);
</script>

<template>
  <button
    :type="type"
    :disabled="disabled"
    :class="[
      // Classes Base
      'flex gap-[0.8rem] items-center justify-center transition duration-150 ease-in-out font-bold focus:outline-none cursor-pointer disabled:cursor-not-allowed',
      
      // Classes por Variante
      variant === 'primary' && [
        'rounded-full',
        'bg-govbr-primary',
        'px-5 py-2',
        'text-sm text-white',
        'hover:bg-govbr-primary-hover',
        'disabled:bg-govbr-border'
      ],

      variant === 'secondary' && [
        'rounded-full',
        'border border-govbr-primary',
        'px-4 py-1.5',
        'text-sm text-govbr-primary',
        'hover:bg-govbr-bg'
      ],

      variant === 'tertiary' && [
        'text-sm',
        'text-govbr-primary',
        'hover:underline'
      ]
    ]"
  >
    <slot></slot>
  </button>
</template>