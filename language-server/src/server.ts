import {
  createConnection,
  TextDocuments,
  ProposedFeatures,
} from "vscode-languageserver/node";

import { TextDocument } from "vscode-languageserver-textdocument";

import Fastify from "fastify";
import fastifyStatic from "@fastify/static";
import fastifyCors from "@fastify/cors";
import * as path from "path";

const WEBVIEW_HTTP_SERVER_PORT = 41648
let webviewHttpServerReady = false;
let webviewHttpServerCheckInterval;
let webviewHttpServerAddress = "";

function start_webview_http_server() {
  const fastify = Fastify({
    logger: true,
  });

  fastify.register(fastifyCors, {
    origin: "*",
  });

  // Declare a route
  fastify.register(fastifyStatic, {
    root: path.join(__dirname, "../../webview", "public"),
  });

  // `/callback` path is called from backend server for OAuth2.1.
  // Loading index.html where has the handling logic for the callback.
  fastify.get('/callback', function (req, reply) {
    reply.sendFile('index.html');
  });

  // Run the server!
  fastify.listen({ port: WEBVIEW_HTTP_SERVER_PORT }, function (err, address) {
    if (err) {
      fastify.log.error(err);
      process.exit(1);
    }
    webviewHttpServerAddress = address;
  });

  fastify.ready(() => {
    webviewHttpServerReady = true;
  });
}

// Create a connection for the server, using Node's IPC as a transport.
// Also include all preview / proposed LSP features.
const connection = createConnection(ProposedFeatures.all);

// Create a simple text document manager.
const documents = new TextDocuments(TextDocument);

// Examples of LSP message handling https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/

// Handlers for the requests:
// connection.onInitialize();
// connection.onInitialized();
// connection.onDidChangeConfiguration();
// connection.onCompletion();
// connection.onCompletionResolve();
// connection.onDidChangeWatchedFiles();
// connection.languages.diagnostics.on();

// Handlers for text documents:
// documents.onDidClose();

// A handler for the initialized notification.
connection.onInitialized((param) => {
  console.log("Received `initialized` notification from client:", param);

  webviewHttpServerCheckInterval = setInterval(() => {
    console.log("webviewHttpServerCheckInterval: ready?", webviewHttpServerReady);
    if (webviewHttpServerReady) {
      connection.sendNotification("http_server_ready", {"address": webviewHttpServerAddress});
      clearInterval(webviewHttpServerCheckInterval);
    }
  }, 100);
});

// Make the text document manager listen on the connection
// for open, change and close text document events
documents.listen(connection);

start_webview_http_server();

// Listen on the connection
connection.listen();
