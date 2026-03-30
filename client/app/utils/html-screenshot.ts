import { JSDOM } from 'jsdom';
import pkg from 'canvas';
const { Canvas, Image } = pkg;
import html2canvas from 'html2canvas-pro';
import fs from 'node:fs';

/**
 * Renders an HTML string to a PNG file using html2canvas-pro logic.
 */
async function renderHtmlToImage(htmlString: string): Promise<void> {
  // 1. Initialize JSDOM
  const dom = new JSDOM(htmlString, {
    resources: "usable",
    pretendToBeVisual: true,
  });

  const { window } = dom;
  const { document } = window;

  // 2. Cast and shim globals
  // We cast to 'any' to bypass TS errors when adding browser globals to Node's 'global'
  const g = global as any;
  g.window = window;
  g.document = document;
  g.HTMLElement = window.HTMLElement;
  g.HTMLCanvasElement = window.HTMLCanvasElement;
  g.Node = window.Node;
  g.Image = Image;
  g.Canvas = Canvas;
  g.requestAnimationFrame = (cb: FrameRequestCallback) => setTimeout(cb, 0);

  try {
    // 3. Render the virtual document body
    // html2canvas-pro will use the shimmed globals automatically
    const canvas = await html2canvas(document.body as HTMLElement, {
      logging: false,
      useCORS: true,
      scale: 2,
    });

    // 4. Convert and save
    const buffer = (canvas as any).toBuffer('image/png');
    fs.writeFileSync('output.png', buffer);
    
    console.log('Successfully exported output.png');
  } catch (error) {
    console.error('Rendering error:', error);
  } finally {
    // 5. Cleanup
    window.close();
  }
}

// Example Usage
const myHtml = `
  <div style="padding: 20px; background: #f0f0f0; border: 5px solid #333; width: 400px; font-family: sans-serif;">
    <h1 style="color: darkblue;">TypeScript Render</h1>
    <p>This image was generated via <b>html2canvas-pro</b> in a Node.js ESM environment.</p>
  </div>
`;

renderHtmlToImage(myHtml);
