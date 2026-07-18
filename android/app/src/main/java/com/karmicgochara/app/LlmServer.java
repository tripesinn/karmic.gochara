package com.karmicgochara.app;

import android.content.Context;
import android.util.Log;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * LlmServer — expose le moteur Gemma on-device (litertlm, backend CPU) en endpoint HTTP
 * consommable par n'importe quel client (l'app elle-même en mode client, ou un outil externe
 * via `adb forward tcp:8088 tcp:8088`).
 *
 * IMPORTANT: implémenté avec java.net.ServerSocket (HTTP/1.1 minimal maison) — PAS
 * com.sun.net.httpserver.HttpServer, qui N'EXISTE PAS sur le runtime Android.
 *
 * Binding: 127.0.0.1 uniquement (loopback). Aucune exposition réseau externe. Port 8099.
 * (8088 évité : occupé par le proxy pipelock local du Mac.)
 *
 * Endpoints:
 *   POST /v1/generate  body {system?,user,type?,lang?} -> {synthesis,local:true,captured:true}
 *   GET  /capture      renvoie le contenu de llm_server_capture.jsonl (pullable adb aussi)
 *   GET  /healthz      {ok:true, running:true, modelReady:true/false}
 */
public class LlmServer {

    public static final int DEFAULT_PORT = 8099;
    private static final String TAG = "LlmServer";

    private final Context context;
    private final GemmaSynthesisPlugin plugin;
    private final int port;
    private ServerSocket serverSocket;
    private Thread acceptThread;
    private final AtomicBoolean running = new AtomicBoolean(false);

    public LlmServer(Context context, GemmaSynthesisPlugin plugin, int port) {
        this.context = context.getApplicationContext();
        this.plugin = plugin;
        this.port = port;
    }

    public synchronized void start() throws IOException {
        if (running.get()) return;
        if (!plugin.isEngineReady()) {
            throw new IllegalStateException("MODEL_NOT_READY — appelez prepareModel() avant llmServer(start).");
        }
        serverSocket = new ServerSocket();
        serverSocket.setReuseAddress(true);
        serverSocket.bind(new InetSocketAddress("127.0.0.1", port));
        running.set(true);
        acceptThread = new Thread(this::acceptLoop, "LlmServerAccept");
        acceptThread.setDaemon(true);
        acceptThread.start();
        Log.i(TAG, "LlmServer démarré sur 127.0.0.1:" + port);
    }

    private void acceptLoop() {
        while (running.get() && !serverSocket.isClosed()) {
            try {
                Socket sock = serverSocket.accept();
                new Thread(() -> handle(sock), "LlmServerConn").start();
            } catch (IOException e) {
                if (running.get()) Log.w(TAG, "accept error: " + e.getMessage());
                break;
            }
        }
    }

    private void handle(Socket sock) {
        try (Socket s = sock) {
            BufferedReader reader = new BufferedReader(new InputStreamReader(s.getInputStream(), StandardCharsets.UTF_8));
            String requestLine = reader.readLine();
            if (requestLine == null) return;
            String[] parts = requestLine.split(" ");
            String method = parts[0];
            String path = parts.length > 1 ? parts[1] : "/";
            // Lire les headers (on cherche Content-Length)
            int contentLength = 0;
            String line;
            while ((line = reader.readLine()) != null && !line.isEmpty()) {
                if (line.toLowerCase().startsWith("content-length:")) {
                    try { contentLength = Integer.parseInt(line.substring(15).trim()); } catch (Exception ignored) {}
                }
            }
            // Lire le corps
            StringBuilder body = new StringBuilder();
            if (contentLength > 0) {
                char[] buf = new char[1024];
                int remaining = contentLength, r;
                while (remaining > 0 && (r = reader.read(buf, 0, Math.min(buf.length, remaining))) != -1) {
                    body.append(buf, 0, r);
                    remaining -= r;
                }
            }
            String responseJson;
            int code;
            if (path.startsWith("/v1/generate")) {
                if (!"POST".equals(method)) { code = 405; responseJson = "{\"error\":\"method not allowed\"}"; }
                else { code = 200; responseJson = doGenerate(body.toString()); }
            } else if (path.startsWith("/capture")) {
                code = 200; responseJson = doCapture();
            } else if (path.startsWith("/healthz")) {
                code = 200; responseJson = doHealthz();
            } else {
                code = 404; responseJson = "{\"error\":\"not found\"}";
            }
            sendResponse(s, code, responseJson);
        } catch (Exception e) {
            Log.w(TAG, "handle error: " + e.getMessage());
        }
    }

    private String doGenerate(String bodyStr) {
        try {
            JSONObject req = new JSONObject(bodyStr != null && !bodyStr.isEmpty() ? bodyStr : "{}");
            String system = req.optString("system", "");
            String user   = req.optString("user", "");
            String type   = req.optString("type", "server");
            String lang   = req.optString("lang", "fr");
            if (user == null || user.isEmpty()) {
                return err(400, "champ 'user' requis");
            }
            String response = plugin.runGenerateForServer(system, user, lang);
            plugin.recordGeneration(system, user, response, type, "server");
            JSONObject out = new JSONObject();
            out.put("synthesis", response);
            out.put("local", true);
            out.put("captured", true);
            out.put("engine", "litertlm-cpu");
            return out.toString();
        } catch (Exception e) {
            Log.e(TAG, "generate error", e);
            return err(500, e.getMessage());
        }
    }

    private String doCapture() {
        java.io.File f = plugin.getCaptureFile();
        StringBuilder sb = new StringBuilder();
        if (f != null && f.exists()) {
            try (java.io.BufferedReader r = new java.io.BufferedReader(new java.io.FileReader(f))) {
                String l;
                while ((l = r.readLine()) != null) sb.append(l).append("\n");
            } catch (IOException ignored) {}
        }
        try {
            JSONObject out = new JSONObject();
            out.put("path", f != null ? f.getAbsolutePath() : null);
            out.put("size", f != null ? f.length() : 0);
            out.put("content", sb.toString());
            return out.toString();
        } catch (Exception e) {
            return err(500, e.getMessage());
        }
    }

    private String doHealthz() {
        try {
            JSONObject out = new JSONObject();
            out.put("ok", true);
            out.put("running", running.get());
            out.put("port", port);
            out.put("modelReady", plugin.isEngineReady());
            return out.toString();
        } catch (Exception e) {
            return err(500, e.getMessage());
        }
    }

    private static String err(int code, String msg) {
        JSONObject o = new JSONObject();
        try { o.put("error", msg); o.put("status", code); } catch (Exception ignored) {}
        return o.toString();
    }

    private static void sendResponse(Socket s, int code, String json) throws IOException {
        byte[] bytes = json.getBytes(StandardCharsets.UTF_8);
        String headers = "HTTP/1.1 " + code + " OK\r\n"
                + "Content-Type: application/json; charset=utf-8\r\n"
                + "Content-Length: " + bytes.length + "\r\n"
                + "Connection: close\r\n\r\n";
        OutputStream os = s.getOutputStream();
        os.write(headers.getBytes(StandardCharsets.UTF_8));
        os.write(bytes);
        os.flush();
    }

    public synchronized void stop() {
        running.set(false);
        if (serverSocket != null) {
            try { serverSocket.close(); } catch (Throwable t) { Log.w(TAG, "stop close: " + t.getMessage()); }
            serverSocket = null;
        }
        Log.i(TAG, "LlmServer arrêté");
    }

    public boolean isRunning() { return running.get(); }
    public int getPort() { return port; }
}
