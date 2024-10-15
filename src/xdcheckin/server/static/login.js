async function setAccount(username) {
	const account = JSON.parse(
			    localStorage.getItem("accounts") || "{}")[username];
	if (!account) {
		alert("No such account.");
		return;
	}
	localStorage.setItem("username", username);
	localStorage.setItem("password", account.password);
	localStorage.setItem("cookies", account.cookies);
	localStorage.setItem("chaoxing_config", account.chaoxing_config || "{}");
	localStorage.setItem("login_method", account.login_method);
}

async function deleteAccount() {
	const username = prompt("Input username to delete:");
	if (username === null)
		return;
	const accounts = JSON.parse(localStorage.getItem("accounts") || "{}");
	if (Object.keys(accounts).length < 2) {
		alert("Cannot delete the only account.");
	}
	delete accounts[username];
	localStorage.setItem("accounts", JSON.stringify(accounts));
	const b = document.getElementById(`accounts-${username}-button`);
	b.parentElement.removeChild(b);
	if (localStorage.getItem("username") == username) {
		setAccount(Object.keys(accounts)[0]);
		alert("Deleted the active one. Logging in with another.");
		promptLogin(auto = 2);
	}
}

async function reconfAccount() {
	const username = prompt("Input username to reconfigure for Chaoxing:");
	if (username === null)
		return;
	const accounts = JSON.parse(localStorage.getItem("accounts") || "{}");
	if (!(username in accounts)) {
		alert("No such account.");
		return;
	}
	const chaoxing_config = prompt("Modify configurations for Chaoxing:",
				       accounts[username].chaoxing_config ||
				       "{}");
	try {
		assert(JSON.parse(chaoxing_config).constructor == Object);
	}
	catch (err) {
		alert("Invalid configurations.");
		return;
	}
	accounts[username].chaoxing_config = chaoxing_config;
	localStorage.setItem("accounts", JSON.stringify(accounts));
	alert("Configuration updated.");
}

async function listAccounts() {
	if (listAccounts.calling)
		return;
	listAccounts.calling = true;
	document.getElementById("accounts-button").style.display = "none";
	const accounts = JSON.parse(localStorage.getItem("accounts") || "{}");
	const e = document.getElementById("accounts-list-div");
	e.replaceChildren();
	if (Object.keys(accounts).length < 4)
		e.appendChild(newElement("button", {
			innerText: "New", onclick: () => promptLogin()
		}));
	if (Object.keys(accounts).length) {
		e.appendChild(newElement("button", {
			innerText: "Delete", onclick: () => deleteAccount()
		}));
		e.appendChild(newElement("button", {
			innerText: "Reconfigure", onclick: () => reconfAccount()
		}));
	}
	e.appendChild(document.createElement("br"));
	for (let username in accounts) {
		const account = accounts[username];
		const login_method = account.login_method;
		const config_len = Object.keys(JSON.parse(
				       account.chaoxing_config || "{}")).length;
		e.appendChild(newElement("button", {
			id: `accounts-${username}-button`, innerText:
			`${username} (${login_method}, ${config_len} configs)`,
			onclick: () => {
				setAccount(username);
				promptLogin(auto = 2);
			}
		}));
	}
	hideOtherLists('accounts-list-div');
	listAccounts.calling = false;
}

async function afterLoginDuties(auto = false) {
	enablePlayers();
	getCurriculum();
	if (localStorage.getItem("fid") == "16820")
		getCurriculum(true);
	const username = localStorage.getItem("username");
	const chaoxing_config = localStorage.getItem("chaoxing_config");
	document.getElementById("logout-button").innerText =
			 `Logout (*${username.substring(username.length - 4)})`;
	const accounts = JSON.parse(localStorage.getItem("accounts") || "{}");
	accounts[username] = {
		"password": localStorage.getItem("password"),
		"cookies": localStorage.getItem("cookies"),
		"login_method": localStorage.getItem("login_method"),
		chaoxing_config
	}
	localStorage.setItem("accounts", JSON.stringify(accounts));
	["accounts-button", "accounts-list-div"].forEach(
						   e_id => displayTag(e_id, 0));
	[
		"logout-button",
		"player0-scan-button", "player2-scan-button",
		"camera-scan-button",
		"locations-button", "activities-button", "curriculum-button"
	].forEach(e_id => displayTag(e_id, 1));
	if (auto == 1)
		return;
	alert(`Logged in successfully as ${username}.\n\n` +
	      `Configurations for Chaoxing:\n` +
	      `${JSON.stringify(JSON.parse(chaoxing_config), null, '    ')}`);
}

async function afterLogoutDuties() {
	hideOtherLists();
	[
		"logout-button",
		"player0-scan-button", "player2-scan-button",
		"camera-scan-button",
		"locations-button", "activities-button", "curriculum-button"
	].forEach(e_id => displayTag(e_id, 0));
	displayTag("accounts-button", 1);
}

async function promptLogin(auto = false) {
	if (globalThis.g_logging_in || globalThis.g_logged_in)
		return;
	let username = localStorage.getItem("username");
	let password = localStorage.getItem("password");
	let chaoxing_config = localStorage.getItem("chaoxing_config") || "{}";
	let method = (localStorage.getItem("login_method") === "ids");
	if (!username || !auto) {
		method = !confirm("Login?\nChoose account type: " +
				 "confirm for Chaoxing, else IDS.");
		username = prompt("Input username:");
		if (username === null)
			return;
		assert(username, "Invalid username.");
		password = prompt("Input password:");
		if (password === null)
			return;
		assert(password, "Invalid password.");
		chaoxing_config = prompt("(Optional) " +
					 "Input configurations for Chaoxing " +
					 "(in JSON string):") || "{}";
		try {
			assert(JSON.parse(chaoxing_config).constructor ==
			       Object);
		}
		catch (err) {
			throw new Error("Invalid configurations.");
		}
	}
	try {
		const ret = await (method ? idsLogin(username, password,
						     chaoxing_config =
						     chaoxing_config) :
					    chaoxingLogin(username, password,
							  force = false,
							  chaoxing_config =
							  chaoxing_config));
		assert(ret === true, ret);
		globalThis.g_logged_in = true;
		afterLoginDuties(auto = auto);
	}
	catch (err) {
		globalThis.g_logged_in = false;
		alert(`Login failed. (${err.message})`);
	}
	globalThis.g_logging_in = false;
}

async function promptLogout() {
	if (globalThis.g_logging_in || !globalThis.g_logged_in)
		return;
	if (confirm("Logout?")) {
		globalThis.g_logged_in = false;
		afterLogoutDuties();
	}
}

async function chaoxingLogin(username, password, force = false,
			     chaoxing_config = "{}") {
	let ret = false;
	const cookies = force ? localStorage.getItem("cookies") :
				(username != localStorage.getItem("username") ||
				 password != localStorage.getItem("password") ?
				 "" : localStorage.getItem("cookies"));
	try {
		const res = await post("/chaoxing/login", {
			"username": username, "password": password,
			"cookies": cookies, "chaoxing_config": chaoxing_config
		});
		assert(res.status == 200, "Backend Chaoxing login error.");
		const data = res.json();
		assert(!data.err, data.err);
		assert(data.cookies, "Backend Chaoxing login failed.");
		localStorage.setItem("login_method", "chaoxing");
		localStorage.setItem("username", username);
		localStorage.setItem("password", password);
		localStorage.setItem("cookies", data.cookies);
		localStorage.setItem("chaoxing_config", chaoxing_config);
		localStorage.setItem("fid", data.fid);
		globalThis.g_courses = data.courses;
		ret = true;
	}
	catch (err) {
		ret = err.message;
	}
	return ret;
}

async function idsLogin(username, password, chaoxing_config = "{}") {
	let ret = false;
	const cookies = username != localStorage.getItem("username") ||
			password != localStorage.getItem("password") ?
			"" : localStorage.getItem("cookies");
	const l = document.getElementById("accounts-button");
	try {
		if (cookies) {
			ret = await chaoxingLogin("", "", force = true,
						  chaoxing_config =
						  chaoxing_config);
			if (ret === true) {
				localStorage.setItem("login_method", "ids");
				localStorage.setItem("username", username);
				localStorage.setItem("password", password);
				return true;
			}
		}
		l.disabled = true;
		await idsLoginFinish(username, password,
				     await idsLoginPrepareCaptcha(),
				     chaoxing_config = chaoxing_config);
		ret = true;
	}
	catch (err) {
		ret = err.message;
	}
	l.disabled = false;
	return ret;
}

async function idsLoginPrepareCaptcha() {
	const res = await post("/ids/login_prepare");
	assert(res.status == 200, "Backend IDS login prepare error.");
	const data = res.json();
	assert(!data.err, data.err);
	const l = document.getElementById("accounts-button");
	l.disabled = true;
	const c = document.getElementById("ids-login-captcha-container-div");
	const s = document.getElementById("ids-login-captcha-input");
	const si = document.getElementById("ids-login-captcha-small-img");
	si.style.left = `${s.value = 0}px`;
	si.src = `data:image/png;base64,${data.captcha.small_img_src}`;
	s.oninput = () => si.style.left =
			`${(c.offsetWidth - si.offsetWidth) * s.value / 280}px`;
	const bi = document.getElementById("ids-login-captcha-img");
	await new Promise(resolve => {
		bi.onload = () => resolve();
		bi.src = `data:image/png;base64,${data.captcha.big_img_src}`;
	});
	displayTag("ids-login-captcha-div");
	const b = document.getElementById("ids-login-captcha-button");
	await new Promise(resolve => {
		b.onclick = () => resolve();
	});
	vcode = parseInt((1 - si.offsetWidth / c.offsetWidth) * s.value);
	displayTag("ids-login-captcha-div");
	return vcode;
}

async function idsLoginFinish(username, password, vcode,
			      chaoxing_config = "{}") {
	const res = await post("/ids/login_finish", {
		"username": username, "password": password, "vcode": vcode,
		"chaoxing_config": chaoxing_config
	});
	assert(res.status == 200, "Backend IDS login finish error.");
	const data = res.json();
	assert(!data.err, data.err);
	assert(data.cookies, "Backend IDS login failed.");
	localStorage.setItem("login_method", "ids");
	localStorage.setItem("username", username);
	localStorage.setItem("password", password);
	localStorage.setItem("cookies", data.cookies);
	localStorage.setItem("chaoxing_config", chaoxing_config);
	localStorage.setItem("fid", data.fid);
	globalThis.g_courses = data.courses;
	return true;
}
