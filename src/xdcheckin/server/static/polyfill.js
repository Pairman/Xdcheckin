if (typeof globalThis === "undefined")
	(function () {
		if (typeof self !== "undefined")
			self.globalThis = self;
		else if (typeof window !== "undefined")
			window.globalThis = window;
		else if (typeof global !== "undefined")
			global.globalThis = global;
		else
			this.globalThis = this;
	})();

(function () {
	function assign (target, ...sources) {
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
	try {
		if (typeof Object.assign !== "function")
			Object.assign = assign;
		else {
			const o = document.createElement("div");
			Object.assign(o, {"style": "display = block"});
		}
	}
	catch (e) {
		if (e instanceof TypeError)
			Object.assign = assign;
	}
})();

if (!Element.prototype.replaceChildren)
	Element.prototype.replaceChildren = function (...nodes) {
		while (this.firstChild)
			this.firstChild.remove();
		this.append(...nodes);
	}
