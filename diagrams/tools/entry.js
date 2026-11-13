import { convertToExcalidrawElements, exportToSvg, serializeAsJSON, restoreElements } from "@excalidraw/excalidraw";

// spec: { elements: [skeleton...], background?: string }
window.renderDiagram = async (spec) => {
  const elements = convertToExcalidrawElements(spec.elements, { regenerateIds: false });
  const appState = {
    viewBackgroundColor: spec.background || "#ffffff",
    exportBackground: true,
    exportWithDarkMode: false,
    gridSize: null,
  };
  const json = serializeAsJSON(elements, appState, {}, "local");
  const svg = await exportToSvg({
    elements, appState, files: {},
    exportPadding: 24,
  });
  return { json, svg: svg.outerHTML, count: elements.length };
};
window.validateFile = (json) => {
  const data = JSON.parse(json);
  const els = restoreElements(data.elements, null);
  return { type: data.type, version: data.version, count: els.length,
           bound: els.filter((x) => x.startBinding || x.endBinding).length };
};
window.ready = true;
