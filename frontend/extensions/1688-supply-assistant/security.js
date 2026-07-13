(function attachSecurityHelpers() {
  const SENSITIVE_KEYS = /(cookie|session|authorization|password|access[_-]?token|refresh[_-]?token)/i;

  function sanitizeValue(value) {
    if (Array.isArray(value)) {
      return value.map(sanitizeValue);
    }
    if (value && typeof value === "object") {
      const output = {};
      Object.entries(value).forEach(([key, nested]) => {
        if (!SENSITIVE_KEYS.test(key)) {
          output[key] = sanitizeValue(nested);
        }
      });
      return output;
    }
    return value;
  }

  window.__SHANGHANG_EXTENSION_SECURITY__ = {
    sanitizePayload(payload) {
      return sanitizeValue(payload);
    },
    hasSensitiveKeys(payload) {
      if (!payload || typeof payload !== "object") return false;
      const stack = [payload];
      while (stack.length) {
        const current = stack.pop();
        if (Array.isArray(current)) {
          current.forEach((item) => stack.push(item));
          continue;
        }
        if (current && typeof current === "object") {
          for (const [key, value] of Object.entries(current)) {
            if (SENSITIVE_KEYS.test(key)) return true;
            stack.push(value);
          }
        }
      }
      return false;
    }
  };
})();
