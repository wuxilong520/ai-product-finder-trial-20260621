chrome.runtime.onInstalled.addListener(async () => {
  const existing = await chrome.storage.local.get(["apiBaseUrl"]);
  if (!existing.apiBaseUrl) {
    await chrome.storage.local.set({
      apiBaseUrl: "http://121.4.35.33",
    });
  }
});
