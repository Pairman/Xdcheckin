function assert(cond, msg) {
	if (!cond)
		throw new Error(msg || "Assertion failed.");
}

function isValidUrl(url) {
	try {
		new URL(url);
		return true;
	} catch (err) {
		return false;
	}
}

async function post(url = "", data = {}) {
	let status_code = 404, text = "";
	try {
		let res = await fetch(url, {
			method: "POST",
			body: JSON.stringify(data)
		});
		status_code = res.status;
		text = await res.text();
	} catch (err) {}
	return {
		status_code,
		text,
		json: () => {
			try {
				return JSON.parse(text);
			} catch (err) {
				return {};
			}
		}
	};
}

function newElement(tag, properties = {}) {
	let e;
	if (typeof(tag) != "object")
		e = document.createElement(tag);
	return Object.assign(e, properties);
}

async function displayTag(e_id) {
	let e = document.getElementById(e_id);
	e.style.display = e.style.display == "none" ? "" : "none";
}

async function hideOtherLists(e_id) {
	let e_ids = [
		"curriculum-list-div", "locations-list-div",
		"activities-list-div", "classrooms-list-div"
	];
	for (let i in e_ids) {
		if (e_ids[i] == e_id)
			continue;
		document.getElementById(e_ids[i]).style.display = "none";
	}
	if (e_id)
		displayTag(e_id);
}

async function onclickCooldown(e_id, ms = 1000) {
	let e = document.getElementById(e_id);
	e.style.pointerEvents = "none";
	setTimeout(() => e.style.pointerEvents = "auto", ms);
}

function unescapeUnicode(s) {
	return s.replace(/\\u[\dA-Fa-f]{4}/g, match => String.fromCharCode(
						parseInt(match.substr(2), 16)));
}

async function qrcode_scanner_init() {
	scanner = await zbarWasm.getDefaultScanner();
	scanner.setConfig(zbarWasm.ZBarSymbolType.ZBAR_NONE,
			  zbarWasm.ZBarConfigType.ZBAR_CFG_ENABLE, 0);
	scanner.setConfig(zbarWasm.ZBarSymbolType.ZBAR_QRCODE,
			  zbarWasm.ZBarConfigType.ZBAR_CFG_ENABLE, 1);
}

async function screenshot_scan(video) {
	if (video.readyState < video.HAVE_ENOUGH_DATA)
		return [];
	const canvas = newElement("canvas");
	canvas.height = video.videoHeight;
	canvas.width = video.videoWidth;
	const ctx = canvas.getContext("2d");
	ctx.drawImage(video, 0, 0);
	let img_data = ctx.getImageData(0, 0, canvas.width, canvas.height);
	let syms = await zbarWasm.scanImageData(img_data);
	syms.forEach(s => s.rawData = s.decode());
	return syms.map(s => s.rawData);
}
