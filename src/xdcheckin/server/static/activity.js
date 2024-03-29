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
				innerText: `${a.name} (${type}, ${ts}, ${te})`
			});
			e.appendChild(b);
		});
	}
	getActivities.calling = false;
}
async function chaoxingCheckinLocation(activity) {
	let res = await post("/chaoxing/checkin_checkin_location", {
		"location": g_location,
		"activity": activity
	});
	alert(res.status_code == 200 ? unescapeUnicode(res.text) :
				       `Checkin error. (Backend error, ` +
				       `${res.status_code})`);
}

async function chaoxingCheckinLocationWrapper(activity, b_id) {
	chaoxingCheckinLocation(activity);
	onclickCooldown(b_id);
}

async function chaoxingCheckinQrcode(img_src, result_div_id) {
	var form = new FormData();
	form.append("img_src", img_src);
	form.append("location", localStorage.getItem("location_"));
	let res = await post("/chaoxing/checkin_checkin_qrcode_img", form);
	document.getElementById(result_div_id).innerText =
						    unescapeUnicode(res.text) ||
			   `Checkin error. (Backend error, ${res.status_code})`;
	if (res.status_code == 200 && res.text.indexOf("success") != -1)
		alert(unescapeUnicode(res.text));
};

async function chaoxingCheckinQrcodeWrapper(video, quality, result_div_id) {
	if (video.paused)
		document.getElementById(result_div_id).innerText =
					     "Checkin error. (No image given.)";
	else {
		chaoxingCheckinQrcode(await screenshot(video, quality),
				      result_div_id);
	}
}
