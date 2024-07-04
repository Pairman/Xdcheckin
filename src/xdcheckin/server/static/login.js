async function afterLoginDuties(auto = false) {
	if (g_logining || !g_logged_in)
		return;
	enablePlayers();
	getCurriculum(with_live = false).then(() => {
		if (g_logining || !g_logged_in)
			return;
		if (localStorage.getItem("fid") == "16820")
			getCurriculum(with_live = true);
	});
	[
		"login-button", "logout-button",
		"player0-scan-button", "player2-scan-button",
		"camera-scan-button",
		"locations-button", "activities-button", "curriculum-button"
	].forEach(displayTag);
	if (!auto)
		alert("Logged in successfully.");
}

async function afterLogoutDuties() {
	if (g_logining || g_logged_in)
		return;
	hideOtherLists();
	[
		"login-button", "logout-button",
		"player0-scan-button", "player2-scan-button",
		"camera-scan-button",
		"locations-button", "activities-button", "curriculum-button"
	].forEach(displayTag);
}

async function promptLogin(auto = false) {
	if (g_logining || g_logged_in)
		return;
	promptLogin.calling = true;
	let username = localStorage.getItem("username");
	let password = localStorage.getItem("password");
	let method = (localStorage.getItem("login_method") === "ids");
	if (!username ||
	   (!auto && !confirm(`Use previously entered account ${username}?`))) {
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
		let force = false, success = await (method ?
				     idsLoginPrepare(username, password, auto):
				     chaoxingLogin(username, password, force,
						   auto));
		assert(success === true, success);
	}
	catch (err) {
		alert(`Login failed. (${err.message})`);
	}
}

async function promptLogout() {
	if (g_logining || !g_logged_in)
		return;
	if (confirm("Logout?")) {
		g_logged_in = false;
		afterLogoutDuties();
	}
}

async function chaoxingLogin(username, password, force = false, auto = false) {
	if (!force) {
		if (g_logining || g_logged_in)
			return;
		g_logining = true;
		g_logged_in = false;
	}
	let ret = false;
	let cookies;
	if (force)
		cookies = localStorage.getItem("cookies");
	else
		cookies = username != localStorage.getItem("username") ||
			  password != localStorage.getItem("password") ?
			  "" : localStorage.getItem("cookies");
	try {
		let res = await post("/chaoxing/login", {
			"username": username,
			"password": password,
			"cookies": cookies
		});
		assert(res.status_code == 200, "Backend error.");
		let data = res.json();
		assert(!data.err, data.err);
		localStorage.setItem("login_method", "chaoxing");
		localStorage.setItem("username", username);
		localStorage.setItem("password", password);
		localStorage.setItem("cookies", data.cookies);
		localStorage.setItem("fid", data.fid);
		g_courses = data.courses;
		ret = true;
	}
	catch (err) {
		ret = err.message;
	}
	if (!force) {
		g_logged_in = (ret === true);
		g_logining = false;
		afterLoginDuties(auto);
	}
	return ret;
}

async function idsLoginPrepare(username, password, auto = false) {
	if (g_logining || g_logged_in)
		return;
	g_logining = true;
	let ret = g_logged_in = false;
	let cookies = username != localStorage.getItem("username") ||
		      password != localStorage.getItem("password") ?
		      "" : localStorage.getItem("cookies");
	try {
		if (cookies) {
			ret = await chaoxingLogin("", "", true);
			if (ret === true) {
				localStorage.setItem("login_method", "ids");
				localStorage.setItem("username", username);
				localStorage.setItem("password", password);
				g_logining = false;
				g_logged_in = true;
				afterLoginDuties(auto);
				return true;
			}
		}
		idsLoginCaptcha(username, password, auto);
		ret = true;
	}
	catch (err) {
		ret = err.message;
	}
	return ret;
}

async function idsLoginCaptcha(username, password, auto = false) {
	let res = await post("/ids/login_prepare");
	assert(res.status_code == 200, "Backend error.");
	let data = res.json();
	assert(!data.err, data.err);
	let b = document.getElementById("login-button");
	let s = document.getElementById("ids-login-captcha-input");
	let c = document.getElementById("ids-login-captcha-container-div");
	let s_img = document.getElementById("ids-login-captcha-small-img");
	s.oninput = () => s_img.style.left =
		     `${(c.offsetWidth - s_img.offsetWidth) * s.value / 280}px`;
	document.getElementById("ids-login-captcha-button").onclick = () => {
		idsLoginFinish(username, password,
			       parseInt(s_img.style.left.split("px")[0] * 280 /
					c.offsetWidth))
		.then(ret => {
			b.disabled = false;
			if (ret === true)
				afterLoginDuties(auto);
			else
				alert(`Login failed. (${ret})`);
		});
		displayTag("ids-login-captcha-div");
	};
	let img = document.getElementById("ids-login-captcha-img");
	img.onload = () => displayTag("ids-login-captcha-div");
	s_img.style.left = `${s.value = 0}px`;
	s_img.src = `data:image/png;base64,${data.captcha.small_img_src}`;
	img.src = `data:image/png;base64,${data.captcha.big_img_src}`;
	b.disabled = true;
}

async function idsLoginFinish(username, password, vcode) {
	if (!g_logining || g_logged_in)
		return;
	let ret = false;
	try {
		let res = await post("/ids/login_finish", {
			"username": username,
			"password": password,
			"vcode": vcode
		});
		assert(res.status_code == 200, "Backend error.");
		let data = res.json();
		assert(!data.err, data.err);
		localStorage.setItem("login_method", "ids");
		localStorage.setItem("username", username);
		localStorage.setItem("password", password);
		localStorage.setItem("cookies", data.cookies);
		localStorage.setItem("fid", data.fid);
		g_courses = data.courses;
		ret = true;
	}
	catch (err) {
		ret = err.message;
	}
	g_logged_in = (ret === true);
	g_logining = false;
	return ret;
}
