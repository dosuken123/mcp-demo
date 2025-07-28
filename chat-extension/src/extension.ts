// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from "vscode";
import * as fs from "fs";
import * as path from "path";
import * as http from "http";
import { workspace, ExtensionContext } from "vscode";

import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  TransportKind,
} from "vscode-languageclient/node";

let client: LanguageClient;

const log = vscode.window.createOutputChannel("Chat Extension", { log: true });

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {
  startLanguageServer(context);
}

// This method is called when your extension is deactivated
export function deactivate() {
  if (!client) {
    return undefined;
  }
  return client.stop();
}

function setupWebviewComponent(context: vscode.ExtensionContext, param: any) {
  const provider = new ChatViewProvider(context.extensionUri, param["address"]);
  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider(
      ChatViewProvider.viewType,
      provider
    )
  );
}

class ChatViewProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = "chat-extension.chat-view";

  private _view?: vscode.WebviewView;

  constructor(
    private readonly _extensionUri: vscode.Uri,
    private readonly _webviewHttpServerUri: string
  ) {}

  public resolveWebviewView(
    webviewView: vscode.WebviewView,
    _context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken
  ) {
    this._view = webviewView;

    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [this._extensionUri],
    };

    webviewView.webview.html = this._getHtmlForWebview();

    webviewView.webview.onDidReceiveMessage((data) => {
      switch (data.type) {
        case "colorSelected": {
          vscode.window.activeTextEditor?.insertSnippet(
            new vscode.SnippetString(`#${data.value}`)
          );
          break;
        }
      }
    });
  }

  private _getHtmlForWebview() {
    const html = `
		<iframe src="${this._webviewHttpServerUri}/" style="width:100%;height:100vh;top:0px;left:0px;position:absolute;border:none;"></iframe>
		`;

    return html;
  }
}

function startLanguageServer(context: vscode.ExtensionContext) {
  // The server is implemented in node
  const serverModule = context.asAbsolutePath(
    path.join("../language-server", "out", "server.js")
  );

  // If the extension is launched in debug mode then the debug server options are used
  // Otherwise the run options are used
  const serverOptions: ServerOptions = {
    run: { module: serverModule, transport: TransportKind.ipc },
    debug: {
      module: serverModule,
      transport: TransportKind.ipc,
    },
  };

  // Options to control the language client
  const clientOptions: LanguageClientOptions = {
    // Register the server for plain text documents
    documentSelector: [{ scheme: "file", language: "plaintext" }],
    synchronize: {
      // Notify the server about file changes to '.clientrc files contained in the workspace
      fileEvents: workspace.createFileSystemWatcher("**/.clientrc"),
    },
  };

  // Create the language client and start the client.
  client = new LanguageClient(
    "languageServerForChatExtension",
    "Language Server for chat extension",
    serverOptions,
    clientOptions
  );

  client.onNotification("http_server_ready", (param) => {
    log.info(`Received 'http_server_ready' notification param: ${param}`);
    setupWebviewComponent(context, param);
  });

  // Start the client. This will also launch the server
  client.start();
}
