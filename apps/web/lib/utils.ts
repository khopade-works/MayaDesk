type ClassValue = string | number | boolean | undefined | null | ClassValue[];

/**
 * Joins class name fragments, filtering out falsy values. A minimal
 * clsx-style helper so components can compose Tailwind classes without
 * an extra runtime dependency.
 */
export function cn(...inputs: ClassValue[]): string {
  const flatten = (values: ClassValue[]): string[] =>
    values.flatMap((value) => {
      if (!value) return [];
      if (Array.isArray(value)) return flatten(value);
      return [String(value)];
    });

  return flatten(inputs).join(" ");
}
