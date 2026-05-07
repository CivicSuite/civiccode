const { spawn } = require("node:child_process");
const { mkdir } = require("node:fs/promises");
const http = require("node:http");
const path = require("node:path");
const { chromium } = require("playwright");

const port = Number(process.env.CIVICCODE_BROWSER_QA_PORT || "18022");
const baseUrl = `http://127.0.0.1:${port}`;
const artifactDir = process.env.CIVICCODE_BROWSER_QA_ARTIFACT_DIR || "";
const staffHeaders = {
  "X-CivicCode-Role": "staff",
  "X-CivicCode-Actor": "browser-qa@example.gov",
};

const scenarios = [
  { name: "staff-code-access-mobile", path: "/staff/code", width: 390, height: 900, status: 403 },
  { name: "staff-code-workspace-desktop", path: "/staff/code", width: 1440, height: 1100, status: 200, headers: staffHeaders },
  { name: "staff-sources-access-mobile", path: "/staff/sources", width: 390, height: 900, status: 403 },
  { name: "staff-sources-workspace-desktop", path: "/staff/sources", width: 1440, height: 1100, status: 200, headers: staffHeaders },
  { name: "staff-imports-access-mobile", path: "/staff/imports", width: 390, height: 900, status: 403 },
  { name: "staff-imports-workspace-desktop", path: "/staff/imports", width: 1440, height: 1100, status: 200, headers: staffHeaders },
  { name: "staff-sync-access-mobile", path: "/staff/sync", width: 390, height: 900, status: 403 },
  { name: "staff-sync-workspace-desktop", path: "/staff/sync", width: 1440, height: 1100, status: 200, headers: staffHeaders },
];

const server = spawn(
  process.env.PYTHON || "python",
  ["-m", "uvicorn", "civiccode.main:app", "--host", "127.0.0.1", "--port", String(port)],
  {
    env: { ...process.env, CIVICCODE_DEMO_SEED: "true" },
    stdio: ["ignore", "pipe", "pipe"],
  },
);

let stdout = "";
let stderr = "";
server.stdout.on("data", (chunk) => {
  stdout += chunk.toString();
});
server.stderr.on("data", (chunk) => {
  stderr += chunk.toString();
});

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

async function main() {
  try {
    await waitForHealth();
    if (artifactDir) {
      await mkdir(artifactDir, { recursive: true });
    }
    const browser = await chromium.launch();
    try {
      const rows = [];
      for (const scenario of scenarios) {
        const context = await browser.newContext({
          viewport: { width: scenario.width, height: scenario.height },
          extraHTTPHeaders: scenario.headers || {},
        });
        const page = await context.newPage();
        const consoleErrors = [];
        const pageErrors = [];
        page.on("console", (message) => {
          if (["error", "warning"].includes(message.type())) {
            consoleErrors.push(message.text());
          }
        });
        page.on("pageerror", (error) => {
          pageErrors.push(error.message);
        });

        const response = await page.goto(`${baseUrl}${scenario.path}`, { waitUntil: "networkidle" });
        const status = response?.status();
        const evidence = await page.evaluate(() => {
          const main = document.querySelectorAll("main#content").length;
          const skip = document.querySelectorAll('a[href="#content"]').length;
          const fixPaths = [...document.querySelectorAll(".fix-path")];
          const fixReadable = fixPaths.every((node) => {
            const style = window.getComputedStyle(node);
            const rect = node.getBoundingClientRect();
            const radius = Number.parseFloat(style.borderTopLeftRadius);
            return (
              style.display === "block" &&
              radius <= 8 &&
              rect.width <= document.documentElement.clientWidth &&
              style.overflowWrap !== "normal"
            );
          });
          const horizontalOverflow = document.documentElement.scrollWidth > document.documentElement.clientWidth + 1;
          return { main, skip, fixCount: fixPaths.length, fixReadable, horizontalOverflow };
        });
        await page.keyboard.press("Tab");
        const firstFocus = await page.evaluate(() => document.activeElement?.textContent?.trim() || "");
        if (artifactDir) {
          await page.screenshot({ path: path.join(artifactDir, `${scenario.name}.png`), fullPage: true });
        }
        await context.close();

        const unexpectedConsoleErrors =
          scenario.status === 403
            ? consoleErrors.filter((message) => !message.includes("Failed to load resource"))
            : consoleErrors;
        const requiresFixPath = scenario.status !== 200 || scenario.path !== "/staff/sources";
        const passed =
          status === scenario.status &&
          evidence.main === 1 &&
          evidence.skip === 1 &&
          (!requiresFixPath || evidence.fixCount > 0) &&
          evidence.fixReadable &&
          !evidence.horizontalOverflow &&
          firstFocus.includes("Skip") &&
          unexpectedConsoleErrors.length === 0 &&
          pageErrors.length === 0;
        rows.push({
          scenario: scenario.name,
          status,
          firstFocus,
          ...evidence,
          consoleErrors,
          unexpectedConsoleErrors,
          pageErrors,
          passed,
        });
      }

      console.table(
        rows.map((row) => ({
          scenario: row.scenario,
          status: row.status,
          main: row.main,
          skip: row.skip,
          fixReadable: row.fixReadable,
          overflow: row.horizontalOverflow,
          focus: row.firstFocus,
          console: row.unexpectedConsoleErrors.length,
          pageErrors: row.pageErrors.length,
          passed: row.passed,
        })),
      );
      const failed = rows.filter((row) => !row.passed);
      if (failed.length) {
        throw new Error(`Browser staff QA failed for: ${failed.map((row) => row.scenario).join(", ")}`);
      }
    } finally {
      await browser.close();
    }
  } finally {
    server.kill();
  }
}

async function waitForHealth() {
  const deadline = Date.now() + 30_000;
  while (Date.now() < deadline) {
    if (await healthOk()) {
      return;
    }
    await new Promise((resolve) => setTimeout(resolve, 300));
  }
  throw new Error(`Timed out waiting for ${baseUrl}/health\nstdout:\n${stdout}\nstderr:\n${stderr}`);
}

function healthOk() {
  return new Promise((resolve) => {
    const request = http.get(`${baseUrl}/health`, (response) => {
      response.resume();
      resolve(response.statusCode === 200);
    });
    request.on("error", () => resolve(false));
    request.setTimeout(1000, () => {
      request.destroy();
      resolve(false);
    });
  });
}
