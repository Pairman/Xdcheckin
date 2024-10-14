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
	if (Object.keys(accounts).length)
		e.appendChild(newElement("button", {
			innerText: "Delete", onclick: () => deleteAccount()
		}));
	e.appendChild(document.createElement("br"));
	for (let username in accounts) {
		const login_method = accounts[username].login_method;
		e.appendChild(newElement("button", {
			id: `accounts-${username}-button`,
			innerText: `${username} (${login_method})`,
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
	getCurriculum(false).then(() => {
		if (localStorage.getItem("fid") == "16820")
			getCurriculum(true);
	});
	const username = localStorage.getItem("username");
	document.getElementById("logout-button").innerText =
			    `Logout (*${username.substr(username.length - 4)})`;
	const accounts = JSON.parse(localStorage.getItem("accounts") || "{}");
	accounts[username] = {
		"password": localStorage.getItem("password"),
		"cookies": localStorage.getItem("cookies"),
		"login_method": localStorage.getItem("login_method")
	}
	localStorage.setItem("accounts", JSON.stringify(accounts));
	[
		"logout-button",
		"player0-scan-button", "player2-scan-button",
		"camera-scan-button",
		"locations-button", "activities-button", "curriculum-button"
	].forEach(displayTag);
	document.getElementById("accounts-button").style.display = "none";
	document.getElementById("accounts-list-div").style.display = "none";
	if (auto != 1)
		alert("Logged in successfully.");
}

async function afterLogoutDuties() {
	hideOtherLists();
	[
		"accounts-button", "logout-button",
		"player0-scan-button", "player2-scan-button",
		"camera-scan-button",
		"locations-button", "activities-button", "curriculum-button"
	].forEach(displayTag);
}

async function promptLogin(auto = false) {
	if (globalThis.g_logging_in || globalThis.g_logged_in)
		return;
	let username = localStorage.getItem("username");
	let password = localStorage.getItem("password");
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
	}
	try {
		const ret = await (method ? idsLogin(username, password) :
					    chaoxingLogin(username, password));
		assert(ret === true, ret);
		globalThis.g_logged_in = true;
		afterLoginDuties(auto);
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

async function chaoxingLogin(username, password, force = false) {
	let ret = false;
	const cookies = force ? localStorage.getItem("cookies") :
				(username != localStorage.getItem("username") ||
				 password != localStorage.getItem("password") ?
				 "" : localStorage.getItem("cookies"));
	try {
		const res = await post("/chaoxing/login", {
			"username": username, "password": password,
			"cookies": cookies
		});
		assert(res.status == 200, "Backend Chaoxing login error.");
		const data = res.json();
		assert(!data.err, data.err);
		assert(data.cookies, "Backend Chaoxing login failed.");
		localStorage.setItem("login_method", "chaoxing");
		localStorage.setItem("username", username);
		localStorage.setItem("password", password);
		localStorage.setItem("cookies", data.cookies);
		localStorage.setItem("fid", data.fid);
		globalThis.g_courses = data.courses;
		ret = true;
	}
	catch (err) {
		ret = err.message;
	}
	return ret;
}

async function idsLogin(username, password) {
	let ret = false;
	const cookies = username != localStorage.getItem("username") ||
			password != localStorage.getItem("password") ?
			"" : localStorage.getItem("cookies");
	const l = document.getElementById("accounts-button");
	try {
		if (cookies) {
			ret = await chaoxingLogin("", "", true);
			if (ret === true) {
				localStorage.setItem("login_method", "ids");
				localStorage.setItem("username", username);
				localStorage.setItem("password", password);
				return true;
			}
		}
		l.disabled = true;
		await idsLoginFinish(username, password,
				     await idsLoginPrepareCaptcha());
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

async function idsLoginFinish(username, password, vcode) {
	const res = await post("/ids/login_finish", {
		"username": username, "password": password, "vcode": vcode
	});
	assert(res.status == 200, "Backend IDS login finish error.");
	const data = res.json();
	assert(!data.err, data.err);
	assert(data.cookies, "Backend IDS login failed.");
	localStorage.setItem("login_method", "ids");
	localStorage.setItem("username", username);
	localStorage.setItem("password", password);
	localStorage.setItem("cookies", data.cookies);
	localStorage.setItem("fid", data.fid);
	globalThis.g_courses = data.courses;
	return true;
}
