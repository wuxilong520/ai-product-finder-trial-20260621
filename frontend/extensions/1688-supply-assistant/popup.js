const statusNode = document.getElementById("status");
const messageNode = document.getElementById("message");
const apiBaseUrlInput = document.getElementById("apiBaseUrl");
const extensionCodeInput = document.getElementById("extensionCode");
const connectButton = document.getElementById("connectButton");
const syncButton = document.getElementById("syncButton");
const procurementButton = document.getElementById("procurementButton");

function setMessage(text, type = "") {
  messageNode.textContent = text || "";
  messageNode.className = `message ${type}`.trim();
}

function setStatus(connected) {
  statusNode.textContent = connected ? "状态：已连接" : "状态：未连接";
}

async function loadState() {
  const localState = await chrome.storage.local.get(["apiBaseUrl"]);
  const sessionState = await chrome.storage.session.get(["extensionToken", "expiresAt"]);
  apiBaseUrlInput.value = localState.apiBaseUrl || "http://121.4.35.33";
  const connected = Boolean(sessionState.extensionToken && sessionState.expiresAt && Date.now() < sessionState.expiresAt);
  if (!connected) {
    await chrome.storage.session.remove(["extensionToken", "expiresAt"]);
  }
  setStatus(connected);
}

async function connect() {
  const apiBaseUrl = apiBaseUrlInput.value.trim();
  const extensionCode = extensionCodeInput.value.trim();
  if (!apiBaseUrl || !extensionCode) {
    setMessage("先填写商航AI地址和连接码。", "error");
    return;
  }
  connectButton.disabled = true;
  setMessage("正在连接商航AI...");
  try {
    const result = await window.ShanghangExtensionApi.exchangeExtensionCode(apiBaseUrl, extensionCode);
    await chrome.storage.local.set({ apiBaseUrl });
    await chrome.storage.session.set({
      extensionToken: result.access_token,
      expiresAt: Date.now() + result.expires_in_seconds * 1000
    });
    setStatus(true);
    setMessage("已连接，可以开始同步当前商品。", "success");
  } catch (error) {
    setStatus(false);
    setMessage(error instanceof Error ? error.message : "连接失败", "error");
  } finally {
    connectButton.disabled = false;
  }
}

async function syncCurrentProduct() {
  const localState = await chrome.storage.local.get(["apiBaseUrl"]);
  const sessionState = await chrome.storage.session.get(["extensionToken", "expiresAt"]);
  const apiBaseUrl = (localState.apiBaseUrl || "").trim();
  const token = sessionState.extensionToken;
  const expiresAt = sessionState.expiresAt || 0;
  if (!apiBaseUrl || !token || Date.now() >= expiresAt) {
    setStatus(false);
    setMessage("连接已过期，请重新生成连接码并连接。", "error");
    return;
  }
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id || !tab.url || !/1688\.com/i.test(tab.url)) {
    setMessage("请先打开1688商品详情页，再点同步。", "error");
    return;
  }
  syncButton.disabled = true;
  setMessage("正在读取当前商品页面...");
  try {
    const response = await chrome.tabs.sendMessage(tab.id, { type: "SHANGHANG_EXTRACT_SUPPLY" });
    if (!response?.ok || !response?.payload) {
      throw new Error("当前页面没有读到完整商品信息，请确认已经打开商品详情页。");
    }
    setMessage("正在同步到商航AI...");
    const result = await window.ShanghangExtensionApi.importCurrentSupply(apiBaseUrl, token, response.payload);
    setMessage(`同步成功：${result.product_title}`, "success");
  } catch (error) {
    setMessage(error instanceof Error ? error.message : "同步失败", "error");
  } finally {
    syncButton.disabled = false;
  }
}

connectButton.addEventListener("click", () => {
  void connect();
});

syncButton.addEventListener("click", () => {
  void syncCurrentProduct();
});

async function importCurrentProcurement() {
  const localState = await chrome.storage.local.get(["apiBaseUrl"]);
  const sessionState = await chrome.storage.session.get(["extensionToken", "expiresAt"]);
  const apiBaseUrl = (localState.apiBaseUrl || "").trim();
  const token = sessionState.extensionToken;
  const expiresAt = sessionState.expiresAt || 0;
  if (!apiBaseUrl || !token || Date.now() >= expiresAt) {
    setStatus(false);
    setMessage("连接已过期，请重新生成连接码并连接。", "error");
    return;
  }
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id || !tab.url || !/1688\.com/i.test(tab.url)) {
    setMessage("请先打开1688商品详情页，再点同步到采购方案。", "error");
    return;
  }
  procurementButton.disabled = true;
  setMessage("正在读取当前商品页面...");
  try {
    const response = await chrome.tabs.sendMessage(tab.id, { type: "SHANGHANG_EXTRACT_SUPPLY" });
    if (!response?.ok || !response?.payload) {
      throw new Error("当前页面没有读到完整商品信息，请确认已经打开商品详情页。");
    }
    setMessage("正在同步到商航AI采购方案...");
    const result = await window.ShanghangExtensionApi.importCurrentProcurement(apiBaseUrl, token, response.payload);
    setMessage(`已同步到采购方案，商品ID：${result.pool_item_id}`, "success");
  } catch (error) {
    setMessage(error instanceof Error ? error.message : "同步到采购方案失败", "error");
  } finally {
    procurementButton.disabled = false;
  }
}

procurementButton.addEventListener("click", () => {
  void importCurrentProcurement();
});

void loadState();
