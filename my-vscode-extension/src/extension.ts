// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from "vscode";

function commentLine() {
  vscode.commands.executeCommand("editor.action.addCommentLine");
}

async function printDefinitionsForActiveEditor() {
  const activeEditor = vscode.window.activeTextEditor;
  console.log("activeEditor: " + activeEditor);
  if (!activeEditor) {
    return;
  }

  const definitions = await vscode.commands.executeCommand<vscode.Location[]>(
    "vscode.executeDefinitionProvider",
    activeEditor.document.uri,
    activeEditor.selection.active
  );

  console.log("definitions: " + definitions);

  for (const definition of definitions) {
    console.log(definition);
  }
}

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {
  // Use the console to output diagnostic information (console.log) and errors (console.error)
  // This line of code will only be executed once when your extension is activated
  console.log(
    'Congratulations, your extension "my-vscode-extension" is now active!'
  );

  // The command has been defined in the package.json file
  // Now provide the implementation of the command with registerCommand
  // The commandId parameter must match the command field in package.json
  const disposable1 = vscode.commands.registerCommand(
    "my-vscode-extension.helloWorld",
    () => {
      // The code you place here will be executed every time your command is executed
      // Display a message box to the user
      vscode.window.showInformationMessage("Hello VS Code!");
    }
  );

  context.subscriptions.push(disposable1);

  const disposable = vscode.commands.registerCommand(
    "my-vscode-extension.showCurrentTime",
    () => {
      // The code you place here will be executed every time your command is executed
      // Display a message box to the user
      vscode.window.showWarningMessage(
        "Current time is" + Date.now().toString()
      );
    }
  );

  context.subscriptions.push(disposable);

  context.subscriptions.push(
    vscode.commands.registerCommand("my-vscode-extension.commentOut", () => {
      commentLine();
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("my-vscode-extension.printDefs", async () => {
      console.log("printDefs");
      await printDefinitionsForActiveEditor();
    })
  );

//   vscode.languages.registerHoverProvider('javascript', {
// 	provideHover(document, position, token) {
// 		console.log("hovered!!");
// 	  return {
// 		contents: ['Hover Content']
// 	  };
// 	}
//   });

  vscode.languages.registerHoverProvider(
    "javascript",
    new (class implements vscode.HoverProvider {
      provideHover(
        _document: vscode.TextDocument,
        _position: vscode.Position,
        _token: vscode.CancellationToken
      ): vscode.ProviderResult<vscode.Hover> {
		    console.log("hovered!!");
        const commentCommandUri = vscode.Uri.parse(
          `command:editor.action.addCommentLine`
        );
        console.log(`commentCommandUri: ${commentCommandUri}`);
        const contents = new vscode.MarkdownString(
          `[Add comment](${commentCommandUri})`
        );

        // To enable command URIs in Markdown content, you must set the `isTrusted` flag.
        // When creating trusted Markdown string, make sure to properly sanitize all the
        // input content so that only expected command URIs can be executed
        contents.isTrusted = true;

        return new vscode.Hover(contents);
      }
    })()
  );

  vscode.languages.registerHoverProvider(
    'javascript',
    new (class implements vscode.HoverProvider {
      provideHover(
        document: vscode.TextDocument,
        _position: vscode.Position,
        _token: vscode.CancellationToken
      ): vscode.ProviderResult<vscode.Hover> {
		    console.log("hovered!!");
        const args = [{ resourceUri: document.uri }];
        const stageCommandUri = vscode.Uri.parse(
          `command:git.stage?${encodeURIComponent(JSON.stringify(args))}`
        );
        const contents = new vscode.MarkdownString(`[Stage file](${stageCommandUri})`);
        contents.isTrusted = true;
        return new vscode.Hover(contents);
      }
    })()
  );
}

// This method is called when your extension is deactivated
export function deactivate() {}
