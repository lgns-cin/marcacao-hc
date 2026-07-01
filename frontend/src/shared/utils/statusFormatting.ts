const ESTADOS_FINALIZADOS = ['CONFIRMADO', 'PROBLEMA_REPORTADO'] as const;

const STATUS_CLASSES: Record<string, string> = {
  ALTA: 'bg-govbr-error-bg text-govbr-error',
  MÉDIA: 'bg-amber-100 text-amber-800',
  BAIXA: 'bg-green-100 text-green-800',
};

export function isFinalizado(estado?: string): boolean {
  return !!estado && (ESTADOS_FINALIZADOS as readonly string[]).includes(estado);
}


export function getStatusClasses(status: string): string {
  return STATUS_CLASSES[status] ?? 'bg-gray-100 text-gray-800';
}
