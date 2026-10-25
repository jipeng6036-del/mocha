import fs from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { createRequire } from "node:module";
import { createHash } from "node:crypto";
const tree = process.env.MOCHA_TREE || "/tmp/mocha1893/baseline";
const label = process.env.MOCHA_LABEL || "baseline";
const require = createRequire(path.join(tree, "package.json"));
const { chromium } = require("@playwright/test");
const original = JSON.parse(await fs.readFile("/evidence/original-title.json", "utf8"));
const bundle = await fs.readFile(path.join(tree, "mocha.js"));
const server = http.createServer((request, response) => {
  if (request.url === "/mocha.js") {
    response.writeHead(200, { "content-type": "text/javascript" }); response.end(bundle); return;
  }
  const titles = request.url.startsWith("/original") ? ["ASCII before", original, "ASCII after"] : ["ASCII before", "plain middle", "ASCII after"];
  response.writeHead(200, { "content-type": "text/html; charset=utf-8" });
  response.end(`<!doctype html><html><body><div id="mocha"></div><script src="/mocha.js"></script><script>
    mocha.setup({ui:"bdd",reporter:"html"});
    describe("IDNA", function(){ for (const title of ${JSON.stringify(titles)}) it(title, function(){}); });
    window.__executed=[]; window.__finished=false;window.__observedFailures=[];
    window.__runner=mocha.run(function(){window.__finished=true;});
    window.__runner.on("pass",function(test){window.__executed.push(test.fullTitle());});
    window.__runner.prependListener("fail",function(test,error){window.__observedFailures.push({title:test.fullTitle(),message:error.message,stack:error.stack});});
  </script></body></html>`);
});
await new Promise(resolve => server.listen(0,"127.0.0.1",resolve));
const browser = await chromium.launch({headless:true});
const results=[];
try {
  for (const mode of ["plain","original"]) {
    const page=await browser.newPage(); const errors=[];page.on("pageerror", error=>errors.push({message:error.message,stack:error.stack}));
    await page.goto(`http://127.0.0.1:${server.address().port}/${mode}`);
    let completed=true;try {await page.waitForFunction(()=>window.__finished, null,{timeout:1500});}catch {completed=false;}
    const data=await page.evaluate(()=>({finished:window.__finished,executed:window.__executed,observedFailures:window.__observedFailures,stats:{passes:window.__runner.stats.passes,failures:window.__runner.stats.failures,tests:window.__runner.stats.tests},replays:[...document.querySelectorAll("#mocha-report .test .replay")].map(x=>x.getAttribute("href"))}));
    const diagnostic = mode === "original" && !completed ? await page.evaluate(() => { try { return {url:Mocha.reporters.HTML.prototype.testURL(window.__runner.test)}; } catch(error) { return {name:error.name,message:error.message,stack:error.stack}; } }) : undefined;
    const row={mode,completed,errors,diagnostic,...data};results.push(row);console.log(JSON.stringify(row));
    if(mode==="original") await page.screenshot({path:`/evidence/${label}-original.png`,fullPage:true});
    if(mode==="original" && completed) {
      await page.locator("#mocha-report .test .replay").nth(1).click();
      await page.waitForFunction(()=>window.__finished,null,{timeout:1500});
      const replay=await page.evaluate(()=>({finished:window.__finished,executed:window.__executed,tests:window.__runner.stats.tests}));results.push({mode:"replay",url:page.url(),...replay});console.log("REPLAY",JSON.stringify(replay));
    }
    await page.close();
  }
  await fs.writeFile(`/evidence/${label}-browser-repro.json`,JSON.stringify({node:process.version,chromium:browser.version(),bundle_sha256:createHash("sha256").update(bundle).digest("hex"),original_code_units:Array.from({length:original.length},(_,i)=>original.charCodeAt(i)),results},null,2));
}finally {await browser.close(); await new Promise(resolve=>server.close(resolve));}
