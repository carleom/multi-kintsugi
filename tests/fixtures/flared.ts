// Open this same file in each editor; compare roles, not ANSI names.
type Result<T> = { value: T; count: number; ready: boolean };
const RETRY_LIMIT = 3;

class Repair {
  constructor(private label: string) {}

  apply<T>(value: T): Result<T> {
    const message = `Repair ${this.label}`;
    if (message.length > 0) {
      return { value, count: RETRY_LIMIT, ready: true };
    }
    throw new Error("Missing label");
  }
}

export const repair = new Repair("gold");
