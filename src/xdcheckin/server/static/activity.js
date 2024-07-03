async function getActivities() {
	if (getActivities.calling)
		return;
	getActivities.calling = true;
	let e = document.getElementById("activities-list-div");
	e.replaceChildren();
	let activities = (await post("/chaoxing/get_activities")).json();
	if (!Object.keys(activities).length)
		e.innerText = "No ongoing activities.";
	for (let class_id in activities) {
		let course_activities = activities[class_id];
		e.appendChild(newElement("div", {
			innerText: `${g_courses[class_id].name}: `
		}));
		course_activities.forEach(a => {
			let type = a.type == "2" ? `Qrcode` : `Location`;
			let ts = a.time_start;
			let te = a.time_end || "????-??-?? ??:??";
			let ts_y = ts.slice(0, 4);
			let ts_md = ts.slice(5, 10);
			let ts_hm = ts.slice(11, 16);
			let te_y = te.slice(0, 4);
			let te_md = te.slice(5, 10);
			let te_hm = te.slice(11, 16);
			ts = "", te = "";
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
			let b = newElement("button", {
				id: `chaoxing-activity-${a.active_id}-button`,
				disabled: a.type == "2",
				onclick: () => chaoxingCheckinLocationWrapper(a,
									  b.id),
				innerText: `${a.name} (${type}, ${ts} ~ ${te})`
			});
			e.appendChild(b);
		});
	}
	getActivities.calling = false;
}

async function chaoxingCheckinCaptcha(params, captcha, e_id_prefix) {
	let res = await post("/chaoxing/captcha_get_captcha", data = {
		"captcha": captcha
	})
	if (res.status_code != 200 && e_id_prefix == "activities") {
		alert(`Checkin error. (Backend error, ${res.status_code})`);
		return;
	}
	captcha = res.json()
	let s = document.getElementById(`${e_id_prefix}-checkin-captcha-input`);
	let c = document.getElementById(`${e_id_prefix}-checkin-captcha-` +
					`container-div`);
	let s_img = document.getElementById(`${e_id_prefix}-checkin-captcha-` +
					    `small-img`);
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
	let img = document.getElementById(`${e_id_prefix}-checkin-captcha-img`);
	img.onload = () => displayTag(`${e_id_prefix}-checkin-captcha-div`);
	s_img.style.left = `${s.value = 0}px`;
	s_img.src = captcha.small_img_src;
	img.src = captcha.big_img_src;
}

async function chaoxingCheckinLocation(activity) {
	document.getElementById(`activities-checkin-captcha-div`).style.display
								       = "none";
	let res = await post("/chaoxing/checkin_checkin_location", {
		"location": g_location, "activity": activity
	});
	let data = res.json();
	if (res.status_code != 200) {
		alert(`Checkin error. (Backend error, ${res.status_code})`);
		return;
	}
	alert(unescapeUnicode(data.msg));
	if (data.msg.includes("validate"))
		chaoxingCheckinCaptcha(data.params, data.captcha,
				       "activities");
}

async function chaoxingCheckinLocationWrapper(activity, b_id) {
	chaoxingCheckinLocation(activity);
	onclickCooldown(b_id);
}

async function chaoxingCheckinQrcode(url, result_div_id) {
	document.getElementById(`${result_div_id.split('-')[0]}-checkin-` +
				`captcha-div`).style.display = "none";
	let res = await post("/chaoxing/checkin_checkin_qrcode_url", {
		"location": g_location, "url": url
	});
	let data = res.json();
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
	urls = await screenshot_scan(video);
	if (!urls.length) {
		document.getElementById(result_div_id).innerText =
					 "Checkin error. (No Qrcode detected.)";
		return;
	}
	urls = urls.filter(v => v.includes(
				     "mobilelearn.chaoxing.com/widget/sign/e"));
	if (!urls.length) {
		document.getElementById(result_div_id).innerText =
				       "Checkin error. (No checkin URL found.)";
		return;
	}
	chaoxingCheckinQrcode(urls[0], result_div_id);
}
