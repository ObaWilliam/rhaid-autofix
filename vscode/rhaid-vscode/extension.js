\
const vscode = require('vscode');
const cp = require('child_process');
const path = require('path');

function runCmd(cmd, args, cwd) {
  return new Promise((resolve, reject) => {
    try {
      const p = cp.spawn(cmd, args, { cwd, shell: process.platform === 'win32' });
      let out = '', err = '';
      p.stdout.on('data', d => out += d.toString());
      p.stderr.on('data', d => err += d.toString());
      p.on('close', code => {
        if (code !== 0) {
          reject(new Error(`Rhaid binary exited with code ${code}.\n${err || out}`));
        } else {
          resolve({ code, out, err });
        }
      });
    } catch (e) {
      reject(e);
    }
  });
}
async function scanWorkspace(diag) {
  const cfg = vscode.workspace.getConfiguration('rhaid');
  const bin = cfg.get('rhaid.pathToBinary', 'rhaid');
  const scanArgs = cfg.get('rhaid.scanArgs', '--json');
  const folder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || process.cwd();
  const args = ['--path', folder, '--mode', 'scan', ...scanArgs.split(' ').filter(Boolean)];
  diag.clear();
  vscode.window.withProgress({ location: vscode.ProgressLocation.Notification, title: 'Rhaid: Scanning workspace...' }, async () => {
    try {
      const res = await runCmd(bin, args, folder);
      const json = JSON.parse(res.out || res.err || '{}');
      if (!json.issues) {
        vscode.window.showInformationMessage('Rhaid: No issues found.');
        return;
      }
      const byFile = {};
      for (const it of json.issues) {
        if (!byFile[it.path]) byFile[it.path] = [];
        const range = new vscode.Range(Math.max((it.line||1)-1,0), Math.max((it.col||1)-1,0), Math.max((it.line||1)-1,0), Math.max((it.col||1)-1,0));
        const sev = it.severity === 'error' ? vscode.DiagnosticSeverity.Error
                  : it.severity === 'warning' ? vscode.DiagnosticSeverity.Warning
                  : vscode.DiagnosticSeverity.Information;
        const d = new vscode.Diagnostic(range, `${it.id}: ${it.message}`, sev);
        d.source = 'rhaid';
        byFile[it.path].push(d);
      }
      for (const [file, diags] of Object.entries(byFile)) {
        const uri = vscode.Uri.file(path.isAbsolute(file) ? file : path.join(folder, file));
        diag.set(uri, diags);
      }
      vscode.window.showInformationMessage(`Rhaid: Scan complete. ${json.issues.length} issues found.`);
    } catch (e) {
      vscode.window.showErrorMessage(`Rhaid scan failed: ${e.message}`);
      if (e.message.includes('not recognized') || e.message.includes('ENOENT')) {
        vscode.window.showWarningMessage('Rhaid binary not found. Please install Rhaid and set "rhaid.pathToBinary" in settings.');
      }
    }
  });
}
async function fixCurrentFile(diag) {
  const cfg = vscode.workspace.getConfiguration('rhaid');
  const bin = cfg.get('rhaid.pathToBinary', 'rhaid');
  const fixArgs = cfg.get('rhaid.fixArgs', '');
  const editor = vscode.window.activeTextEditor;
  if (!editor) return;
  const file = editor.document.uri.fsPath;
  const folder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || path.dirname(file);
  const args = ['--path', file, '--mode', 'fix', '--backup', ...fixArgs.split(' ').filter(Boolean)];
  try {
    await runCmd(bin, args, folder);
    await editor.document.save();
  vscode.window.showInformationMessage('Rhaid: File fixed.');
    await scanWorkspace(diag);
  } catch (e) {
    vscode.window.showErrorMessage(`Rhaid fix failed: ${e.message}`);
    if (e.message.includes('not recognized') || e.message.includes('ENOENT')) {
      vscode.window.showWarningMessage('Rhaid binary not found. Please install Rhaid and set "rhaid.pathToBinary" in settings.');
    }
  }
}
function activate(context) {
  const diag = vscode.languages.createDiagnosticCollection('rhaid');
  context.subscriptions.push(diag);
  context.subscriptions.push(vscode.commands.registerCommand('rhaid.scanWorkspace', () => scanWorkspace(diag)));
  context.subscriptions.push(vscode.commands.registerCommand('rhaid.fixCurrentFile', () => fixCurrentFile(diag)));
  context.subscriptions.push(vscode.commands.registerCommand('rhaid.enterLicenseKey', async () => {
    const key = await vscode.window.showInputBox({ prompt: 'Enter your Rhaid Pro license key', password: true });
    if (key) {
      await vscode.workspace.getConfiguration('rhaid').update('licenseKey', key, vscode.ConfigurationTarget.Global);
      vscode.window.showInformationMessage('Rhaid license key saved.');
    }
  }));
  const selector = [{ scheme: 'file' }];
  context.subscriptions.push(vscode.languages.registerCodeActionsProvider(selector, {
    provideCodeActions(document, range, context, token) {
      const actions = [];
      const hasRhaid = (context.diagnostics || []).some(d => d.source === 'rhaid');
      if (hasRhaid) {
        const action = new vscode.CodeAction('Rhaid: Fix this file', vscode.CodeActionKind.QuickFix);
        action.command = { command: 'rhaid.fixCurrentFile', title: 'Rhaid: Fix this file' };
        actions.push(action);
      }
      return actions;
    }
  }, { providedCodeActionKinds: [vscode.CodeActionKind.QuickFix] }));
  vscode.workspace.onDidSaveTextDocument(async (doc) => {
    const cfg = vscode.workspace.getConfiguration('rhaid');
    // Multi-root support: scan/fix only if doc is in a workspace folder
    const folder = vscode.workspace.getWorkspaceFolder(doc.uri);
    if (!folder) return;
    if (cfg.get('fixOnSave', false)) await fixCurrentFile(diag);
    else await scanWorkspace(diag);
  });
  scanWorkspace(diag);
  vscode.commands.registerCommand('rhaid.openSettings', () => {
    vscode.commands.executeCommand('workbench.action.openSettings', '@ext:camwood.rhaid-vscode');
  });

  // Pass license key to CLI via env
  const licenseKey = vscode.workspace.getConfiguration('rhaid').get('licenseKey', '');
  if (licenseKey) {
    process.env.RHAID_LICENSE_KEY = licenseKey;
  }
}
function deactivate() {}
module.exports = { activate, deactivate };
