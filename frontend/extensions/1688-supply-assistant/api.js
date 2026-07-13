async function exchangeExtensionCode(apiBaseUrl, extensionCode) {
  const response = await fetch(`${apiBaseUrl.replace(/\/+$/, "")}/api/v1/supply/extension/session`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ extension_code: extensionCode })
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data?.message || data?.detail || "连接商航AI失败");
  }
  return data;
}

async function importCurrentSupply(apiBaseUrl, token, payload) {
  const response = await fetch(`${apiBaseUrl.replace(/\/+$/, "")}/api/v1/supply/extension/import`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data?.message || data?.detail || "同步供应商数据失败");
  }
  return data;
}

window.ShanghangExtensionApi = {
  exchangeExtensionCode,
  importCurrentSupply
};
