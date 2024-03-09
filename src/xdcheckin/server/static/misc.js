async function checkEula() {
	let msg = "This APP provides utilities for Chaoxing check-ins and " +
		  "classroom livestreams exclusively for XDUers.\n\n" +
		  "By confirming you agree to the following terms:\n" +
		  "    1. This APP is for study use only.\n" +
		  "    2. This work comes with absolutely no warranty.\n\n" +
		  "You have been warned.";
	if (!localStorage.getItem("xdcheckin_eula") && confirm(msg))
		localStorage.setItem("xdcheckin_eula", "1");
}

async function xdcheckinCheckUpdates() {
	let ver = (await post("/xdcheckin/get/version")).text;
	document.getElementById("footer-link-a").innerText += ` ${ver}`;
	ver = ver.split(".");
	let release = (await post("/xdcheckin/get/releases/latest")).json();
	if (!Object.keys(release).length)
		return;
	let rel_ver = release.tag_name.split("."), update = false;
	for (let i in ver) {
		let diff = ver[i] - rel_ver[i];
		if (diff > 0)
			break;
		if (diff < 0)
			update = true;
	}
	if (update)
		document.getElementById("xdcheckin-update-div").innerHTML =
			`<a href='${release.html_url}'>` +
			`Version ${release.tag_name} released.` +
			`</a><br>${release.body.replaceAll('\r\n', '<br>')}`;
}
