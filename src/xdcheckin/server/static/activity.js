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
			innerText: `${globalThis.g_courses[class_id].name}: `
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

async function chaoxingCheckinCaptcha(params, captcha, e_id_prefix) {
	const res = await post("/chaoxing/captcha_get_captcha", data = {
		"captcha": captcha
	})
	if (res.status_code != 200 && e_id_prefix == "activities") {
		alert(`Checkin error. (Backend error, ${res.status_code})`);
		return;
	}
	captcha = res.json();
	const s = document.getElementById(
					`${e_id_prefix}-checkin-captcha-input`);
	const c = document.getElementById(
				`${e_id_prefix}-checkin-captcha-container-div`);
	const s_img = document.getElementById(
				    `${e_id_prefix}-checkin-captcha-small-img`);
	s.oninput = () => s_img.style.left =
		     `${(c.offsetWidth - s_img.offsetWidth) * s.value / 320}px`;
	document.getElementById(`${e_id_prefix}-checkin-captcha-button`)
		.onclick = () => {
		captcha["vcode"] = parseInt(s_img.style.left.split("px")[0] *
					    320 / c.offsetWidth);
		post("/chaoxing/captcha_submit_captcha", data = {
			"captcha": captcha
		}).then(res => {
			if (res.status_code != 200 &&
			    e_id_prefix == "activities") {
				alert(`Checkin error. (Backend or ` +
				      `CAPTCHA error, ${res.status_code})`);
				return;
			}
			captcha = res.json();
			params.validate = captcha.validate;
			post("/chaoxing/checkin_do_sign", data = {
				"params": params
			}).then(res => {
				data = res.json();
				if (res.status_code != 200 &&
				    e_id_prefix == "activities") {
					alert(`Checkin error. (Backend error,` +
					` ${res.status_code})`);
					return;
				}
				if (data.msg.includes("success"))
					alert(unescapeUnicode(data.msg));
				if (e_id_prefix != "activities")
					document.getElementById(
						`${e_id_prefix}-scanresult-div`)
						.innerText =
						      unescapeUnicode(data.msg);
			});
		});
		displayTag(`${e_id_prefix}-checkin-captcha-div`);
	};
	const img = document.getElementById(
					  `${e_id_prefix}-checkin-captcha-img`);
	img.onload = () => displayTag(`${e_id_prefix}-checkin-captcha-div`);
	s_img.style.left = `${s.value = 0}px`;
	s_img.src = captcha.small_img_src;
	img.src = captcha.big_img_src;
}

async function chaoxingCheckinLocation(activity) {
	document.getElementById(`activities-checkin-captcha-div`).style.display
								       = "none";
	const res = await post("/chaoxing/checkin_checkin_location", {
		"location": globalThis.g_location, "activity": activity
	});
	const data = res.json();
	if (res.status_code != 200) {
		alert(`Checkin error. (Backend error, ${res.status_code})`);
		return;
	}
	alert(unescapeUnicode(data.msg));
	if (data.msg.includes("validate"))
		chaoxingCheckinCaptcha(data.params, data.captcha, "activities");
}

async function chaoxingCheckinLocationWrapper(activity) {
	chaoxingCheckinLocation(activity);
}

async function chaoxingCheckinQrcode(url, result_div_id) {
	document.getElementById(`${result_div_id.split('-')[0]}-checkin-` +
				`captcha-div`).style.display = "none";
	const res = await post("/chaoxing/checkin_checkin_qrcode_url", {
		"location": globalThis.g_location, "url": url
	});
	const data = res.json();
	document.getElementById(result_div_id).innerText =
						    unescapeUnicode(data.msg) ||
			   `Checkin error. (Backend error, ${res.status_code})`;
	if (res.status_code != 200)
		return;
	if (data.msg.includes("success"))
		alert(unescapeUnicode(data.msg));
	else if (data.msg.includes("validate"))
		chaoxingCheckinCaptcha(data.params, data.captcha,
				       result_div_id.split("-")[0]);
};

async function chaoxingCheckinQrcodeWrapper(video, result_div_id) {
	if (video.paused) {
		document.getElementById(result_div_id).innerText =
					     "Checkin error. (No image given.)";
		return;
	}
	try {
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
				       "Checkin error. (No checkin URL found.)";
			return;
		}
		chaoxingCheckinQrcode(curls[0], result_div_id);
	}
	catch (e) {
		document.getElementById(result_div_id).innerText =
						`Checkin error. (${e.message})`;
	}
}