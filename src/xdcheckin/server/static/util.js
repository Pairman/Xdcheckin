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
		let body = data instanceof FormData ? data :
						      JSON.stringify(data);
		let res = await fetch(url, {
			method: "POST",
			body: body
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
	return Object.assign(document.createElement(tag), properties);
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

async function screenshot(video, quality) {
	let canvas = newElement("canvas", {
		height: video.videoHeight,
		width: video.videoWidth
	});
	let ctx = canvas.getContext("2d");
	ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
	let img_src = await new Promise(resolve => canvas.toBlob(
				 blob => resolve(blob), "image/jpeg", quality));
	canvas.remove();
	return img_src;
}
