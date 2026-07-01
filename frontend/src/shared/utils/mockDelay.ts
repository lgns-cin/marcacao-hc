const MOCK_DELAY_MS = {
  fetch: 300,
  action: 200,
  fast: 100,
} as const;

export function mockDelay(type: keyof typeof MOCK_DELAY_MS = 'fetch'): Promise<void> {
  return new Promise((r) => setTimeout(r, MOCK_DELAY_MS[type]));
}
