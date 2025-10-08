export type InterfaceAsRecord<T> = {
  [K in keyof T]: T[K];
};

// don't use arrow function, use function syntax of assertions due to https://stackoverflow.com/a/72689922

export function assert(condition: any, msg?: string): asserts condition {
  if (!condition) {
    console.trace();
    console.warn(msg ?? "Assertion failed");
    throw new Error(msg ?? "Assertion failed");
  }
}

export function assertIsString(val: any): asserts val is string {
  if (typeof val !== "string") {
    console.trace();
    console.warn(`Not a string typeof=${typeof val} "${val}"`);
    throw new Error(`Not a string typeof=${typeof val} "${val}"`);
  }
}

export function assertIsNumber(val: any): asserts val is number {
  if (typeof val !== "number") {
    console.trace();
    console.warn(`Not a number typeof=${typeof val} "${val}"`);
    throw new Error(`Not a number typeof=${typeof val} "${val}"`);
  }
  if (Number.isNaN(val)) {
    console.trace();
    console.warn(`Was a NaN typeof=${typeof val} "${val}"`);
    throw new Error(`Was a NaN typeof=${typeof val} "${val}"`);
  }
}

export function assertIsArrayOfNumbers(val: any): asserts val is number[] {
  if (!Array.isArray(val) || val.some((x) => typeof x !== "number")) {
    console.trace();
    console.warn(
      `Not a number[] typeof=${typeof val} typeof values: "${JSON.stringify(
        Array.isArray(val) ? val.map((x) => typeof x) : val
      )}"`
    );
    throw new Error(
      `Not a number[] typeof=${typeof val} typeof values: "${JSON.stringify(
        Array.isArray(val) ? val.map((x) => typeof x) : val
      )}"`
    );
  }
}

export function assertNever(value: never) {
  console.trace();
  console.warn("Unexpected value: " + value);
  throw new Error("Unexpected value: " + value);
}
