/**
 * Debounce function to limit the rate at which a function can be called.
 * @param func The function to debounce.
 * @param waitFor The delay in milliseconds.
 * @returns A debounced version of the function.
 */
export function debounce<F extends (...args: any[]) => void>(func: F, waitFor: number) {
  let timeout: ReturnType<typeof setTimeout> | null = null;

  return (...args: Parameters<F>): void => {
    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(() => func(...args), waitFor);
  };
} 