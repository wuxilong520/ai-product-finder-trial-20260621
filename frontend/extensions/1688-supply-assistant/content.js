function textFromSelectors(selectors) {
  for (const selector of selectors) {
    const element = document.querySelector(selector);
    const text = element?.textContent?.trim();
    if (text) return text;
  }
  return "";
}

function attrFromSelectors(selectors, attr) {
  for (const selector of selectors) {
    const element = document.querySelector(selector);
    const value = element?.getAttribute?.(attr)?.trim();
    if (value) return value;
  }
  return "";
}

function collectImages() {
  const nodes = [
    ...document.querySelectorAll("img"),
  ];
  const urls = nodes
    .map((node) => node.getAttribute("src") || node.getAttribute("data-src") || "")
    .filter(Boolean)
    .map((url) => url.startsWith("//") ? `https:${url}` : url)
    .filter((url) => /^https?:\/\//i.test(url));
  return [...new Set(urls)].slice(0, 12);
}

function collectSkuTexts() {
  const selectors = [
    ".sku-item",
    ".skuProp",
    "[data-sku]",
    ".prop-item",
    ".table-sku tr"
  ];
  const items = [];
  selectors.forEach((selector) => {
    document.querySelectorAll(selector).forEach((node) => {
      const text = node.textContent?.replace(/\s+/g, " ").trim();
      if (text) items.push(text);
    });
  });
  return [...new Set(items)].slice(0, 20);
}

function collectDescription() {
  const selectors = [
    ".detail-desc-decorate-richtext",
    ".detail-description",
    ".module-wap-detail-common-description",
    "#desc-lazyload-container"
  ];
  return textFromSelectors(selectors);
}

function buildPayload() {
  const title = textFromSelectors([
    "h1",
    ".title-text",
    ".d-title",
    ".title",
    "[data-testid='title']"
  ]);
  const priceRange = textFromSelectors([
    ".price-range",
    ".price",
    ".price-now",
    ".uniform-banner-box-price",
    "[data-testid='price']"
  ]);
  const moq = textFromSelectors([
    ".moq",
    ".quantity-text",
    ".min-order",
    ".order-info"
  ]);
  const sales = textFromSelectors([
    ".sale-count",
    ".deal-cnt",
    ".volume"
  ]);
  const supplierName = textFromSelectors([
    ".company-name",
    ".supplier-name",
    ".shop-name",
    ".company-title"
  ]);
  const supplierLocation = textFromSelectors([
    ".company-address",
    ".factory-address",
    ".location",
    ".company-info-address"
  ]);
  const factoryInfo = textFromSelectors([
    ".factory-info",
    ".company-summary",
    ".company-intro"
  ]);
  const certification = textFromSelectors([
    ".certification",
    ".company-auth",
    ".auth-tags"
  ]);
  const description = collectDescription();
  const sku = collectSkuTexts();
  const primaryImage = attrFromSelectors([
    ".detail-gallery img",
    ".main-image img",
    ".swipe-pane img"
  ], "src");

  return {
    source: "1688_extension",
    title,
    url: window.location.href,
    price_range: priceRange,
    moq,
    supplier: {
      name: supplierName,
      location: supplierLocation
    },
    images: [...new Set([primaryImage, ...collectImages()].filter(Boolean))],
    metadata: {
      sales,
      sku,
      factory_info: factoryInfo,
      description,
      certification,
      category: textFromSelectors([".crumbs", ".breadcrumb", ".cate-path"])
    }
  };
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type !== "SHANGHANG_EXTRACT_SUPPLY") return;
  const rawPayload = buildPayload();
  const security = window.__SHANGHANG_EXTENSION_SECURITY__;
  const payload = security?.sanitizePayload ? security.sanitizePayload(rawPayload) : rawPayload;
  sendResponse({
    ok: Boolean(payload?.title && payload?.supplier?.name),
    payload,
    pageUrl: window.location.href
  });
  return true;
});
