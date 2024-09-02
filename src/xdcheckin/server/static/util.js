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
		const res = await fetch(url, {
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
	const e = (typeof(tag) != "object") ? document.createElement(tag) : tag;
	return Object.assign(e, properties);
}

async function displayTag(e_id) {
	const e = document.getElementById(e_id);
	e.style.display = e.style.display == "none" ? "" : "none";
}

async function hideOtherLists(e_id) {
	const e_ids = [
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

function unescapeUnicode(s) {
	return s.replace(/\\u[\dA-Fa-f]{4}/g, match => String.fromCharCode(
						parseInt(match.substr(2), 16)));
}

async function qrcode_scanner_init() {
	const scanner = await zbarWasm.getDefaultScanner();
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
	const data = ctx.getImageData(0, 0, canvas.width, canvas.height);
	return (await zbarWasm.scanImageData(data)).map(s => s.decode());
}

async function checkEula() {
	const msg = "This APP provides utilities for Chaoxing check-ins " +
		  "and classroom livestreams exclusively for XDUers.\n\n" +
		  "By confirming you agree to the following terms:\n" +
		  "    1. This APP is for study use only.\n" +
		  "    2. This work comes with absolutely no warranty.\n\n" +
		  "You have been warned.";
	if (!localStorage.getItem("xdcheckin_eula"))
		if (confirm(msg))
			localStorage.setItem("xdcheckin_eula", "1");
		else
			document.getElementById("main-body").style.display =
									 "none";
}

async function xdcheckinCheckUpdates() {
	const ver = (await post("/xdcheckin/get_version")).text;
	document.getElementById("footer-link-a").innerText += ` ${ver}`;
	const update = (await post("/xdcheckin/get_update")).json();
	if (update && update.updatable)
		document.getElementById("xdcheckin-update-div").innerHTML =
			`<a href='${update.html_url}'>` +
			`Version ${update.tag_name} released.` +
			`</a><br>${update.body.replaceAll('\r\n', '<br>')}`;
}
