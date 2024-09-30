async function getActivities() {
	if (getActivities.calling)
		return;
	getActivities.calling = true;
	const e = document.getElementById("activities-list-div");
	e.replaceChildren();
	const activities = (await post("/chaoxing/get_activities")).json();
	if (!Object.keys(activities).length)
		e.innerText = "No ongoing activities.";
	for (let class_id in activities) {
		const course_activities = activities[class_id];
		e.appendChild(newElement("div", {
			innerText: class_id in globalThis.g_courses ?
				   `${globalThis.g_courses[class_id].name}: ` :
				   `${class_id}: `
		}));
		course_activities.forEach(a => {
			const type = a.type == "2" ? `Qrcode` : `Location`;
			const ts_a = a.time_start;
			const te_a = a.time_end || "????-??-?? ??:??";
			const ts_y = ts_a.slice(0, 4);
			const ts_md = ts_a.slice(5, 10);
			const ts_hm = ts_a.slice(11, 16);
			const te_y = te_a.slice(0, 4);
			const te_md = te_a.slice(5, 10);
			const te_hm = te_a.slice(11, 16);
			let ts = "", te = "";
			if (ts_y != te_y) {
				ts += `${ts_y}-`;
				te += `${te_y}-`;
			}
			if (ts_y != te_y || ts_md != te_md) {
				ts += `${ts_md} `;
				te += `${te_md} `;
			}
			ts += ts_hm;
			te += te_hm;
			const b = newElement("button", {
				id: `chaoxing-activity-${a.active_id}-button`,
				disabled: a.type == "2",
				innerText: `${a.name} (${type}, ${ts} ~ ${te})`,
				onclick: () => chaoxingCheckinLocationWrapper(a)
			});
			e.appendChild(b);
		});
	}
	getActivities.calling = false;
}

async function chaoxingCheckinCaptcha(e_id_prefix) {
	const res1 = await post("/chaoxing/captcha_get_captcha")
	if (res1.status != 200)
		return [false, res1.status];
	captcha = res1.json();
	const c = document.getElementById(
				`${e_id_prefix}-checkin-captcha-container-div`);
	const s = document.getElementById(
					`${e_id_prefix}-checkin-captcha-input`);
	const si = document.getElementById(
				    `${e_id_prefix}-checkin-captcha-small-img`);
	si.style.left = `${s.value = 0}px`;
	si.src = captcha.small_img_src;
	s.oninput = () => si.style.left =
			`${(c.offsetWidth - si.offsetWidth) * s.value / 320}px`;
	const bi = document.getElementById(
					  `${e_id_prefix}-checkin-captcha-img`);
	await new Promise(resolve => {
		bi.onload = () => resolve();
		bi.src = captcha.big_img_src;
	});
	displayTag(`${e_id_prefix}-checkin-captcha-div`);
	const b = document.getElementById(
				       `${e_id_prefix}-checkin-captcha-button`);
	await new Promise(resolve => {
		b.onclick = () => resolve();
	});
	vcode = parseInt((1 - si.offsetWidth / c.offsetWidth) * s.value);
	displayTag(`${e_id_prefix}-checkin-captcha-div`);
	res2 = await post("/chaoxing/captcha_submit_captcha", data = {
		"captcha": {
			"captcha_id": captcha["captcha_id"],
			"token": captcha["token"], vcode
		}
	});
	if (res2.status != 200)
		return [false, res2.status];
	return [true, res2.json().validate];
}

async function chaoxingCheckinSign(params, e_id_prefix) {
	let result = null;
	for (let i = 0; i < 3; ++i) {
		result = await chaoxingCheckinCaptcha(e_id_prefix);
		if (result[0])
			break;
	}
	if (result[0])
		params.validate = result[1]
	else if (e_id_prefix == "activities") {
		alert(`Checkin error. (CAPTCHA error, ${result[1]})`);
		return;
	}
	const res = await post("/chaoxing/checkin_do_sign", data = {params});
	data = res.json();
	if (e_id_prefix != "activities")
		document.getElementById(`${e_id_prefix}-scanresult-div`)
					 .innerText = unescapeUnicode(data.msg);
	else if (res.status != 200)
			alert(`Checkin error. (Backend error, ${res.status})`);
	if (data.msg.includes("success"))
		alert(unescapeUnicode(data.msg));
}

async function chaoxingCheckinLocation(activity) {
	document.getElementById(`activities-checkin-captcha-div`).style.display
								       = "none";
	const res = await post("/chaoxing/checkin_checkin_location", {
		"location": globalThis.g_location, activity
	});
	const data = res.json();
	if (res.status != 200) {
		alert(`Checkin error. (Backend error, ${res.status})`);
		return;
	}
	alert(unescapeUnicode(data.msg));
	if (data.msg.includes("validate"))
		chaoxingCheckinSign(data.params, "activities");
}

async function chaoxingCheckinLocationWrapper(activity) {
	chaoxingCheckinLocation(activity);
}

async function chaoxingCheckinQrcode(url, result_div_id) {
	const e_id_prefix = result_div_id.split('-')[0];
	document.getElementById(
		   `${e_id_prefix}-checkin-captcha-div`).style.display = "none";
	const data = {
		"location": globalThis.g_location, "video": "", "url": ""
	};
	if (globalThis.g_is_ios && e_id_prefix.startsWith("player"))
		data["video"] = globalThis.g_player_sources[e_id_prefix.substr(
						       e_id_prefix.length - 1)];
	else
		data["url"] = url;
	const res = await post("/chaoxing/checkin_checkin_qrcode_url", data);
	const d = res.json();
	document.getElementById(result_div_id).innerText =
						       unescapeUnicode(d.msg) ||
				`Checkin error. (Backend error, ${res.status})`;
	if (res.status != 200)
		return;
	if (d.msg.includes("success"))
		alert(unescapeUnicode(d.msg));
	else if (d.msg.includes("validate"))
		chaoxingCheckinSign(d.params, result_div_id.split("-")[0]);
};

async function chaoxingCheckinQrcodeWrapper(video, result_div_id) {
	if (video.paused) {
		document.getElementById(result_div_id).innerText =
					     "Checkin error. (No image given.)";
		return;
	}
	try {
		if (globalThis.g_is_ios) {
			chaoxingCheckinQrcode("", result_div_id);
			return;
		}
		const urls = await screenshot_scan(video);
		if (!urls.length) {
			document.getElementById(result_div_id).innerText =
					 "Checkin error. (No Qrcode detected.)";
			return;
		}
		const curls = urls.filter(v => v.includes(
				     "mobilelearn.chaoxing.com/widget/sign/e"));
		if (!curls.length) {
			document.getElementById(result_div_id).innerText =
				`Checkin error. (No checkin URL in [${urls}].)`;
			return;
		}
		chaoxingCheckinQrcode(curls[0], result_div_id);
	}
	catch (e) {
		document.getElementById(result_div_id).innerText =
						`Checkin error. (${e.message})`;
	}
}
