import { onMounted, onUnmounted, type Ref } from 'vue';

export function useAutoRefresh(
  callback: () => Promise<unknown>,
  intervalMs: number,
  pauseWhen?: Ref<boolean>,
) {
  let timer: ReturnType<typeof setInterval> | undefined;

  onMounted(() => {
    timer = setInterval(async () => {
      if (pauseWhen?.value) return;
      try {
        await callback();
      } catch {
        // Falha silenciosa: a próxima rodada tenta novamente.
      }
    }, intervalMs);
  });

  onUnmounted(() => {
    clearInterval(timer);
  });
}
