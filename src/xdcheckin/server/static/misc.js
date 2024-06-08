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
	let ver = (await post("/xdcheckin/get_version")).text;
	document.getElementById("footer-link-a").innerText += ` ${ver}`;
	let update = (await post("/xdcheckin/get_update")).json();
	if (update && update.updatable)
		document.getElementById("xdcheckin-update-div").innerHTML =
			`<a href='${update.html_url}'>` +
			`Version ${update.tag_name} released.` +
			`</a><br>${update.body.replaceAll('\r\n', '<br>')}`;
}
