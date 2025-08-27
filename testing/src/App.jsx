import React, { useState } from "react";
import Editor from "react-simple-code-editor"; 
import Prism from "prismjs"; 
import "prismjs/themes/prism-tomorrow.css"; 
import "prismjs/components/prism-json";

const App = () => {
  const [apiUrl, setApiUrl] = useState("");
  const [jsonData, setJsonData] = useState("{\n  \n}");
  const [otherData, setOtherData] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [method, setMethod] = useState("POST");

  const highlight = code =>
    Prism.highlight(code, Prism.languages.json, "json");

  const handleSend = async () => {
    setLoading(true);
    setResponse(null);
    try {
      let body;
      let headers = {};

      if (otherData.trim()) {
        body = otherData;
        headers["Content-Type"] = "text/plain";
      } else {
        body = jsonData;
        headers["Content-Type"] = "application/json";
      }

      const res = await fetch(apiUrl, {
        method,
        headers,
        body: method === "GET" ? undefined : body,
      });

      const contentType = res.headers.get("content-type");
      let data;
      if (contentType && contentType.includes("application/json")) {
        data = await res.json();
      } else {
        data = await res.text();
      }
      setResponse(data);
    } catch (err) {
      setResponse({ error: err.message });
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col items-center py-10 px-4">
      <div className="w-full max-w-2xl bg-slate-800 rounded-xl shadow-lg p-8 space-y-6">
        <h1 className="text-3xl font-bold text-slate-100 mb-2 text-center">
          API Tester
        </h1>
        {/* API URL Input */}
        <div>
          <label className="block text-slate-300 mb-1 font-medium">
            API URL
          </label>
          <input
            type="text"
            className="w-full px-3 py-2 rounded bg-slate-700 text-slate-100 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="https://api.example.com/endpoint"
            value={apiUrl}
            onChange={e => setApiUrl(e.target.value)}
          />
        </div>
        {/* HTTP Method Selector */}
        <div>
          <label className="block text-slate-300 mb-1 font-medium">
            HTTP Method
          </label>
          <select
            className="w-full px-3 py-2 rounded bg-slate-700 text-slate-100 border border-slate-600 focus:outline-none"
            value={method}
            onChange={e => setMethod(e.target.value)}
          >
            <option>GET</option>
            <option>POST</option>
            <option>PUT</option>
            <option>PATCH</option>
            <option>DELETE</option>
          </select>
        </div>
        {/* JSON Data Editor */}
        <div>
          <label className="block text-slate-300 mb-1 font-medium">
            JSON Data
            <span className="text-xs text-slate-400 ml-2">(optional)</span>
          </label>
          <div className="rounded bg-slate-700 border border-slate-600 overflow-hidden">
            <Editor
              value={jsonData}
              onValueChange={setJsonData}
              highlight={highlight}
              padding={12}
              style={{
                fontFamily: "Fira Mono, monospace",
                fontSize: 14,
                minHeight: 120,
                background: "transparent",
                color: "#f8fafc",
              }}
              textareaClassName="focus:outline-none"
            />
          </div>
        </div>
        {/* Other Data Input */}
        <div>
          <label className="block text-slate-300 mb-1 font-medium">
            Other Data (raw, e.g. XML, form data, etc)
            <span className="text-xs text-slate-400 ml-2">(optional)</span>
          </label>
          <textarea
            className="w-full px-3 py-2 rounded bg-slate-700 text-slate-100 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={4}
            placeholder="Paste raw data here (overrides JSON if filled)"
            value={otherData}
            onChange={e => setOtherData(e.target.value)}
          />
        </div>
        {/* Send Button */}
        <div className="flex justify-end">
          <button
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-2 rounded shadow transition disabled:opacity-50"
            onClick={handleSend}
            disabled={loading || !apiUrl}
          >
            {loading ? "Sending..." : "Send"}
          </button>
        </div>
        {/* Response Output */}
        {response !== null && (
          <div className="mt-6">
            <label className="block text-slate-300 mb-1 font-medium">
              Response
            </label>
            <pre className="bg-slate-950 rounded p-4 text-slate-200 overflow-x-auto text-sm max-h-64">
              {typeof response === "object"
                ? JSON.stringify(response, null, 2)
                : response}
            </pre>
          </div>
        )}
      </div>
      <footer className="mt-10 text-slate-500 text-xs text-center">
        Developed by Meeth - 2025
      </footer>
    </div>
  );
};

export default App;