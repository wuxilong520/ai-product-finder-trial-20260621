import net from "node:net";
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const host = "0.0.0.0";
const basePort = Number(process.env.PORT || 3000);
const maxPort = basePort + 20;
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const root = path.resolve(__dirname, "..");
const nextBin = path.join(root, "node_modules", ".bin", "next");

function canListen(port) {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.once("error", () => resolve(false));
    server.once("listening", () => {
      server.close(() => resolve(true));
    });
    server.listen(port, host);
  });
}

async function findPort() {
  for (let port = basePort; port <= maxPort; port += 1) {
    // eslint-disable-next-line no-await-in-loop
    if (await canListen(port)) {
      return port;
    }
  }
  throw new Error(`没有找到可用端口，已检查 ${basePort}-${maxPort}`);
}

const port = await findPort();

console.log(`Starting Next.js production server on http://${host}:${port}`);

const child = spawn(nextBin, ["start", "-H", host, "-p", String(port)], {
  stdio: "inherit",
  env: {
    ...process.env,
    PORT: String(port),
  },
});

child.on("exit", (code) => {
  process.exit(code ?? 0);
});
