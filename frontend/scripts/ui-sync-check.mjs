import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const root = path.resolve(__dirname, "..");
const appDir = path.join(root, "app");
const componentsDir = path.join(root, "components");
const reportPath = path.join(root, "..", "UI_SYNC_REPORT.md");

const requiredLayoutPages = [
  "app/insights/page.tsx",
  "app/action-center/page.tsx",
  "app/products/page.tsx",
  "app/products/[id]/page.tsx",
];

const pageDelegatedLayoutMarkers = {};

const forbiddenImport = "@/components/ui/";
const forbiddenPatterns = [
  /text-slate-\d+/g,
  /bg-slate-\d+/g,
  /border-slate-\d+/g,
  /text-gray-\d+/g,
  /bg-gray-\d+/g,
  /border-gray-\d+/g,
  /text-blue-600/g,
];

function walk(dir) {
  const output = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === "ui" || entry.name === "node_modules" || entry.name === ".next") {
      continue;
    }
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      output.push(...walk(fullPath));
    } else if (entry.isFile() && /\.(ts|tsx|js|jsx|md)$/.test(entry.name)) {
      output.push(fullPath);
    }
  }
  return output;
}

function rel(file) {
  return path.relative(root, file).replaceAll(path.sep, "/");
}

const scanTargets = [...walk(appDir), ...walk(componentsDir)];
const violations = [];
const checked = [];

for (const file of scanTargets) {
  const relative = rel(file);
  const content = fs.readFileSync(file, "utf8");
  checked.push(relative);

  if (
    relative.endsWith(".tsx") &&
    !relative.startsWith("components/ui/") &&
    !relative.startsWith("design-system/") &&
    content.includes(forbiddenImport)
  ) {
    violations.push({
      file: relative,
      reason: "直接引用了旧 UI 组件入口，应改为 `@/design-system/components`。",
    });
  }

  for (const pattern of forbiddenPatterns) {
    if (pattern.test(content)) {
      violations.push({
        file: relative,
        reason: `仍然含有旧风格类名：\`${pattern}\`。`,
      });
      break;
    }
  }
}

const allowedLayoutMarkers = ["AppShell", "PageLayout", "NewDashboardLayout", "XBorderLayout"];

for (const page of requiredLayoutPages) {
  const fullPath = path.join(root, page);
  const content = fs.readFileSync(fullPath, "utf8");
  const delegatedMarkers = pageDelegatedLayoutMarkers[page] || [];
  const hasDirectLayout = allowedLayoutMarkers.some((marker) => content.includes(marker));
  const hasDelegatedLayout = delegatedMarkers.some((marker) => content.includes(marker));
  if (!hasDirectLayout && !hasDelegatedLayout) {
    violations.push({
      file: page,
      reason: "这个页面没有接入统一布局 `AppShell / PageLayout / NewDashboardLayout`。",
    });
  }
}

const status = violations.length === 0 ? "PASS" : "FAIL";
const lines = [
  "# UI Sync Report",
  "",
  `- 检查时间：${new Date().toISOString()}`,
  `- 检查状态：${status}`,
  `- 扫描文件数：${checked.length}`,
  `- 统一布局强制页数：${requiredLayoutPages.length}`,
  `- 发现问题数：${violations.length}`,
  "",
  "## 当前统一规则",
  "",
  "- 业务页面必须使用 `AppShell`、`PageLayout`、`NewDashboardLayout` 或 `XBorderLayout`。",
  "- 页面与组件禁止直接引用旧 UI 目录，统一走 `@/design-system/components`。",
  "- 页面与业务组件禁止继续使用旧的 `slate / gray / blue-600` 这一套零散浅色风格类名。",
  "- 新页面默认继承深色主题、统一卡片、统一按钮、统一输入框和统一语言切换。",
  "",
  "## 检查结果",
  "",
];

if (violations.length === 0) {
  lines.push("- 没有发现跑偏页面，当前全站保持统一 SaaS 风格。");
} else {
  for (const item of violations) {
    lines.push(`- ${item.file}：${item.reason}`);
  }
}

lines.push("", "## 已覆盖页面", "");
for (const page of requiredLayoutPages) {
  lines.push(`- ${page}`);
}

fs.writeFileSync(reportPath, `${lines.join("\n")}\n`, "utf8");

if (violations.length > 0) {
  console.error(`UI sync check failed. See ${reportPath}`);
  process.exit(1);
}

console.log(`UI sync check passed. Report written to ${reportPath}`);
