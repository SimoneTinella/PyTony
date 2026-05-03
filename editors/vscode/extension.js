const cp = require("node:child_process");
const path = require("node:path");
const vscode = require("vscode");

const DIAGNOSTIC_SOURCE = "pytony";
const LINTABLE_LANGUAGE_IDS = new Set(["pytony", "python"]);
const DEFAULT_DEBOUNCE_MS = 250;

function isLintableDocument(document) {
  if (document.isUntitled) {
    return false;
  }
  if (document.uri.scheme !== "file") {
    return false;
  }
  if (document.languageId === "pytony") {
    return true;
  }
  return (
    document.languageId === "python" &&
    document.fileName.toLowerCase().endsWith(".py")
  );
}

function getLintConfiguration() {
  const config = vscode.workspace.getConfiguration("pytony");
  return {
    enabled: config.get("lint.enabled", true),
    command: config.get("lint.command", "pytony"),
    args: config.get("lint.args", []),
    run: config.get("lint.run", "onType"),
  };
}

function getWorkingDirectory(document) {
  const workspaceFolder = vscode.workspace.getWorkspaceFolder(document.uri);
  if (workspaceFolder) {
    return workspaceFolder.uri.fsPath;
  }
  return path.dirname(document.uri.fsPath);
}

function buildLintArguments(document) {
  const { args } = getLintConfiguration();
  return [...args, "lint", document.uri.fsPath];
}

function toSeverity(code) {
  if (code === "PYL005") {
    return vscode.DiagnosticSeverity.Information;
  }
  return vscode.DiagnosticSeverity.Warning;
}

function makeRange(document, lineNumber, columnNumber) {
  const zeroBasedLine = Math.max(0, lineNumber - 1);
  const zeroBasedColumn = Math.max(0, columnNumber - 1);
  const lineText = document.lineAt(Math.min(zeroBasedLine, document.lineCount - 1));
  const start = new vscode.Position(zeroBasedLine, Math.min(zeroBasedColumn, lineText.text.length));
  const end = new vscode.Position(zeroBasedLine, lineText.text.length);
  return new vscode.Range(start, end);
}

function parseLintDiagnostics(output, document) {
  const diagnostics = [];
  const lines = output.split(/\r?\n/);

  for (const rawLine of lines) {
    const line = rawLine.trimEnd();
    if (!line) {
      continue;
    }
    const lintMatch = line.match(/^(.+?):(\d+):(\d+): \[([A-Z0-9]+)\] (.+)$/);
    if (lintMatch) {
      const [, , lineNumberText, columnText, code, message] = lintMatch;
      const diagnostic = new vscode.Diagnostic(
        makeRange(document, Number(lineNumberText), Number(columnText)),
        message,
        toSeverity(code)
      );
      diagnostic.code = code;
      diagnostic.source = DIAGNOSTIC_SOURCE;
      diagnostics.push(diagnostic);
      continue;
    }

    if (/^\d+ issue\(s\) found in /.test(line)) {
      continue;
    }
    if (/^Clean: /.test(line)) {
      continue;
    }

    const syntaxMatch = line.match(/\(riga (\d+), colonna (\d+)\)/);
    const diagnostic = new vscode.Diagnostic(
      syntaxMatch
        ? makeRange(document, Number(syntaxMatch[1]), Number(syntaxMatch[2]))
        : new vscode.Range(new vscode.Position(0, 0), new vscode.Position(0, 0)),
      line,
      vscode.DiagnosticSeverity.Error
    );
    diagnostic.source = DIAGNOSTIC_SOURCE;
    diagnostics.push(diagnostic);
  }

  return diagnostics;
}

function runLint(document, collection) {
  const config = getLintConfiguration();
  if (!config.enabled || !isLintableDocument(document)) {
    collection.delete(document.uri);
    return Promise.resolve();
  }

  return new Promise((resolve) => {
    const child = cp.spawn(config.command, buildLintArguments(document), {
      cwd: getWorkingDirectory(document),
      shell: false,
    });

    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });

    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });

    child.on("error", (error) => {
      const diagnostic = new vscode.Diagnostic(
        new vscode.Range(new vscode.Position(0, 0), new vscode.Position(0, 0)),
        `Impossibile eseguire \`${config.command}\`: ${error.message}`,
        vscode.DiagnosticSeverity.Error
      );
      diagnostic.source = DIAGNOSTIC_SOURCE;
      collection.set(document.uri, [diagnostic]);
      resolve();
    });

    child.on("close", (code) => {
      const output = [stdout, stderr].filter(Boolean).join("\n");
      if (code === 0) {
        collection.set(document.uri, []);
        resolve();
        return;
      }
      collection.set(document.uri, parseLintDiagnostics(output, document));
      resolve();
    });
  });
}

function activate(context) {
  const diagnostics = vscode.languages.createDiagnosticCollection(DIAGNOSTIC_SOURCE);
  const pendingLintTimers = new Map();

  function clearPendingLint(uri) {
    const key = uri.toString();
    const timer = pendingLintTimers.get(key);
    if (timer) {
      clearTimeout(timer);
      pendingLintTimers.delete(key);
    }
  }

  function scheduleLint(document, reason = "onType") {
    const config = getLintConfiguration();
    if (!config.enabled) {
      diagnostics.delete(document.uri);
      return;
    }
    if (!isLintableDocument(document)) {
      return;
    }
    if (reason === "onType" && config.run !== "onType") {
      return;
    }
    if (reason === "onSave" && config.run === "off") {
      return;
    }

    clearPendingLint(document.uri);
    const key = document.uri.toString();
    const delay = reason === "onType" ? DEFAULT_DEBOUNCE_MS : 0;
    const timer = setTimeout(() => {
      pendingLintTimers.delete(key);
      runLint(document, diagnostics);
    }, delay);
    pendingLintTimers.set(key, timer);
  }

  context.subscriptions.push(
    diagnostics,
    vscode.commands.registerCommand("pytony.runLint", () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) {
        return;
      }
      scheduleLint(editor.document, "onSave");
    }),
    vscode.workspace.onDidOpenTextDocument((document) => {
      scheduleLint(document, "onSave");
    }),
    vscode.workspace.onDidChangeTextDocument((event) => {
      if (event.document.languageId && LINTABLE_LANGUAGE_IDS.has(event.document.languageId)) {
        scheduleLint(event.document, "onType");
      }
    }),
    vscode.workspace.onDidSaveTextDocument((document) => {
      scheduleLint(document, "onSave");
    }),
    vscode.workspace.onDidCloseTextDocument((document) => {
      clearPendingLint(document.uri);
      diagnostics.delete(document.uri);
    }),
    vscode.workspace.onDidChangeConfiguration((event) => {
      if (!event.affectsConfiguration("pytony")) {
        return;
      }
      for (const document of vscode.workspace.textDocuments) {
        scheduleLint(document, "onSave");
      }
    })
  );

  for (const document of vscode.workspace.textDocuments) {
    scheduleLint(document, "onSave");
  }
}

function deactivate() {}

module.exports = {
  activate,
  deactivate,
};
