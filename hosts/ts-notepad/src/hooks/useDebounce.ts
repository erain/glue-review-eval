/** Debounced effect hook + flushable callback debouncer. */

import { useEffect, useRef } from 'react';

/**
 * Run `effect` after `value` has been stable for `delayMs`.
 *
 * Returns a `flush` function that fires the pending effect immediately
 * (useful for Cmd/Ctrl+S "force save"). If nothing is pending, `flush` is a no-op.
 */
export function useDebouncedEffect<T>(
  value: T,
  delayMs: number,
  effect: (value: T) => void,
): () => void {
  // Hold the latest effect and value in refs so the timer fires with the freshest
  // closures without re-arming each render.
  const effectRef = useRef(effect);
  const valueRef = useRef(value);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pendingRef = useRef(false);

  effectRef.current = effect;
  valueRef.current = value;

  useEffect(() => {
    pendingRef.current = true;
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      pendingRef.current = false;
      timerRef.current = null;
      effectRef.current(valueRef.current);
    }, delayMs);

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [value, delayMs]);

  return () => {
    if (!pendingRef.current) return;
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    pendingRef.current = false;
    effectRef.current(valueRef.current);
  };
}
