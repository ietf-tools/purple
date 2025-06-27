export const sortObject = <T extends Record<string, unknown>>(obj: T): T => {
    return Object.keys(obj).sort().reduce(function (result, _key) {
        const key: keyof T = _key
        result[key] = obj[key];
        return result;
    }, {} as T);
}
