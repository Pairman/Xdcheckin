if (typeof globalThis === "undefined")
	(function() {
		if (typeof self !== "undefined")
			self.globalThis = self;
		else if (typeof window !== "undefined")
			window.globalThis = window;
		else if (typeof global !== "undefined")
			global.globalThis = global;
		else
			this.globalThis = this;
	})();

(function() {
	function assign(target, ...sources) {
		if (target == null)
			throw new TypeError(
				  "Cannot convert undefined or null to object");
		const t = Object(target);
		for (const s of sources)
			if (s != null)
				for (const k in s)
					if (s.hasOwnProperty(k))
						t[k] = s[k];
		return t;
	};
	if (typeof Object.assign !== "function")
		Object.assign = assign;
	else {
		const o = document.createElement("div");
		try {
			Object.assign(o, {"style": "display = block"});
		}
		catch (e) {
			if (e instanceof TypeError)
				Object.assign = assign;
		}
	}
})();

if (!Element.prototype.replaceChildren)
	Element.prototype.replaceChildren = function(...nodes) {
		while (this.firstChild)
			this.firstChild.remove();
		this.append(...nodes);
	}

globalThis.zbarWasmReady = new Promise(function (resolve, reject) {
	if (typeof WebAssembly === "object") {
		const script = document.createElement("script");
		script.src =
		"https://cdn.jsdelivr.net/npm/@undecaf/zbar-wasm@0.11.0/dist/index.js";
		script.onload = function() {
			zbarWasm.getDefaultScanner().then(function (s) {
				s.setConfig(0, 0, 0);
				s.setConfig(64, 0, 1);
				resolve();
			});
		}
		script.onerror = reject;
		document.head.appendChild(script);
	}
	else {
		const script = document.createElement("script");
		globalThis.module = {};
		script.src =
		"https://cdn.jsdelivr.net/npm/llqrcode@1.0.0/index.min.js";
		async function scanImageData(data) {
			const canvas = document.createElement("canvas");
			canvas.height = data.height;
			canvas.width = data.width;
			const ctx = canvas.getContext("2d");
			ctx.putImageData(data, 0, 0);
			let nh = data.height, nw = data.width;
			if (data.height * data.width > qrcode.maxImgSize) {
				const r = data.width / data.height;
				nh = Math.sqrt(qrcode.maxImgSize / r);
				nw = r * nh;
			}
			const ncanvas = document.createElement("canvas");
			qrcode.height = ncanvas.height = nh;
			qrcode.width = ncanvas.width = nw;
			const nctx = ncanvas.getContext("2d");
			nctx.drawImage(canvas, 0, 0, data.width, data.height,
				       0, 0, nw, nh);
			qrcode.imagedata = nctx.getImageData(0, 0, nw, nh);
			try {
				qrcode.result = qrcode.process(nctx);
				return [{"decode": function() {
					return qrcode.result;
				}}];
			}
			catch (e) {
				if (typeof e === "string" &&
				    e.startsWith("Couldn't find enough"))
					return [];
				else
					throw e;
			}
		}
		script.onload = function() {
			globalThis.zbarWasm = {};
			zbarWasm.scanImageData = scanImageData;
			resolve();
		}
		script.onerror = reject;
		document.head.appendChild(script);
	}
});
