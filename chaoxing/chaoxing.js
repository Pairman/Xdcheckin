function assert(condition, message) {
	if (!condition)
		throw new Error(message ||"Assertion failed");
}

class Chaoxing{
	name = "";
	uid = "";
	/* cookies = undefined; */
	courses = {};
	curriculum = {};
	logined = false;
	/* headers = {
		"User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
	} */

	constructor(username, password) {
		try{
			let login = this.login({"username": username, "password": password});
			this.name = login["name"];
			this.uid = login["uid"];
			/* this.cookies = login["cookies"]; */
			this.courses = this.get_courses();
			assert(Object.keys(this.courses).length);
			this.curriculum = this.get_curriculum();
			this.logined = (login != false);
		}
		catch (error) {
			console.log(error);
			this.logined = false;
		}
	}

	get(url = "", params = {}, headers = this.headers) {
		class _get {
			status_code = "";
			text = "";
			constructor(url, params){
				let status_code = undefined;
				let text = undefined;
				let response = $.ajax({
					cache: true,
					type: "GET",
					async: false,
					xhrFields: {
						withCredentials: true
					},
					/* headers: headers, */
					url: url,
					data: params,
					contentType: "text/plain; charset=utf-8",
					dataType: "text"
				});
				this.status_code = response.status;
				this.text = response.responseText;
			}
			json(){
				try{
					return JSON.parse(this.text);
				}
				catch (error) {
					return undefined;
				}
			}
		}
		return new _get(url, params);
	}

	login(account = {"username": "", "password": ""}) {
		let url1 = "https://passport2-api.chaoxing.com/v11/loginregister";
		let params1 = {
			"code": account["password"],
			"cx_xxt_passport": "json",
			"uname": account["username"],
			"loginType": 1,
			"roleSelect": "true"
		};
		let url2 = "https://sso.chaoxing.com/apis/login/userLogin4Uname.do";
		try {
			let res1 = this.get(url1, params1);
			assert(res1.json()["status"]);
			let res2 = this.get(url2 /*, cookies = res1.cookies*/);
			let data = res2.json();
			assert(data["result"]);
			return {
				"name": data["msg"]["name"],
				"uid": data["msg"]["puid"].toString(),
				/* "cookies": res1.cookies */
			}
		} catch (error) {
			return false;
		}
	}

	get_courses() {
		let url = "https://mooc1-1.chaoxing.com/visit/courselistdata";
		let params = {
			"courseType": 1,
			"courseFolderId": 0,
			"courseFolderSize": 0
		};
		try {
			let res = this.get(url, params);
			let arr = Array.from(res.text.matchAll(/courseId=\"(.*?)\" clazzId=\"(.*?)\".*?title=\"(.*?)\".*?title=\".*?\".*?title=\"(.*?)\"/sg));
			let courses = {};
			for (let i in arr) {
				courses[arr[i][2]] = {"course_id": arr[i][1], "name": arr[i][3], "teacher": arr[i][4].split("，")}
			}
			assert(Object.keys(courses).length);
			return courses;
		}		
		catch (error) {
			return false;
		}
	}

	get_curriculum(week = "") {
		let url = "https://kb.chaoxing.com/curriculum/getMyLessons";
		let params = {
			"week": week
		};
		try {
			let res = this.get(url, params);
			let data = res.json()["data"]["lessonArray"];
			let curriculum = {};
			function add_lesson(lesson) {
				let lesson_class_id = lesson["classId"].toString();
				let lesson_ = {
					"course_id": lesson["courseId"].toString(),
					"name": lesson["name"],
					"location": lesson["location"],
					"teacher": [lesson["teacherName"]],
					"time":[{
						"day": lesson["dayOfWeek"].toString(),
						"period": lesson["beginNumber"].toString() + "-" + (lesson["beginNumber"] + lesson["length"] - 1).toString()
					}]
				};
				if (!(lesson_class_id in curriculum)) {
					curriculum[lesson_class_id] = lesson_;
					return;
				}
				if (!(curriculum[lesson_class_id]["time"].includes(lesson_["time"][0])))
					curriculum[lesson_class_id]["time"].push(lesson_["time"][0]);
				if (!(curriculum[lesson_class_id]["teacher"].includes(lesson_["teacher"][0])))
					curriculum[lesson_class_id]["teacher"].push(lesson_["teacher"][0]);
			}
			for (let i in data) {
				let lesson = data[i];
				add_lesson(lesson);
				for (let key in lesson["conflictLessons"]) {
					let conflict = lesson["conflictLessons"][key];
					add_lesson(conflict);
				}
			}
			assert(Object.keys(curriculum).length);
			return curriculum;
		}
		catch (error) {
			console.log(error);
			return false;
		}
	}


	get_course_activities(course = {"course_id": "", "class_id": ""}) {
		let url = "https://mobilelearn.chaoxing.com/v2/apis/active/student/activelist";
		let params = {
			"fid": 0,
			"courseId": course["course_id"] ? course["course_id"] : this.courses[course["class_id"]]["course_id"],
			"classId": course["class_id"],
			"showNotStartedActive": 0
		};
		try {
			let res = this.get(url, params);
			let data = res.json()["data"]["activeList"];
			let activities = [];
			for (let i in data) {
				let activity = data[i];
				if (activity["status"] == 1 && (activity["otherId"] == "4" || activity["otherId"] == "2"))
					activities.push({"active_id": activity["id"], "type": activity["otherId"], "time_left": activity["nameFour"]});
			}
			assert(activities.length);
			return activities;
		}
		catch (error) {
			return false;
		}
	}

	get_activities() {
		try {
			let activities = {};
			for (let class_id in this.courses) {
				let course_id = this.courses[class_id]["course_id"];
				let activity = this.get_course_activities({"course_id": course_id, "class_id": class_id});
				if (Object.keys(activity).length)
					activities[class_id] = activity;
			}
			assert(Object.keys(activities).length);
			return activities;
		}
		catch (error) {
			return false;
		}
	}

	checkin_get_details(activity = {"active_id": ""}) {
		let url = "https://mobilelearn.chaoxing.com/newsign/signDetail";
		let params = {
			"activePrimaryId": activity["active_id"],
			"type": "1"
		};
		try {
			let res = this.get(url, params);
			let details = res.json();
			assert(Object.keys(details).length);
			for (let key in details) {
				if (typeof(details[key]) === "number")
					details[key] = details[key].toString();
			}
			return details;
		}
		catch (error) {
			return false;
		}
	}

	checkin_do_presign(activity = {"active_id": "", "class_id": ""}) {
		let url = "https://mobilelearn.chaoxing.com/newsign/preSign";
		let params = {
			"courseId": this.courses[activity["class_id"]]["course_id"] ? this.courses[activity["class_id"]]["course_id"] : "",
			"classId": activity["class_id"],
			"activePrimaryId": activity["active_id"],
			"general": "1",
			"sys": "1",
			"ls": "1",
			"appType": "15",
			"tid": "",
			"uid": this.uid,
			"ut": "s"
		};
		try {
			let res = this.get(url, params);
			return res.status_code == 200;
		}
		catch (error) {
			return false;
		}
	}	

	checkin_do_analysis(activity = {"active_id": ""}) {
		let url1 = "https://mobilelearn.chaoxing.com/pptSign/analysis";
		let params1 = {
			"vs": "1",
			"DB_STRATEGY": "RANDOM",
			"aid": activity["active_id"]
		};
		let url2 = "https://mobilelearn.chaoxing.com/pptSign/analysis2";
		let params2 = {
			"DB_STRATEGY": "RANDOM",
			"code": ""
		};
		try {
			let res1 = this.get(url1, params1);
			params2["code"] = res1.text.match("code=+(.*?),")[1].slice(3, 35);
			let res2 = this.get(url2, params2);
			return res2.text == "success";
		}
		catch (error) {
			return false;
		}
	}

	checkin_check_designatedplace(activity = {"active_id": ""}) {
		let url = "https://mobilelearn.chaoxing.com/v2/apis/active/getPPTActiveInfo";
		let params = {
			"activeId": activity["active_id"]
		};
		try {
			let res = this.get(url, params);
			let s = res.text.match("\"locationRange\":(.*?),")[1];
			return s != "null";
		}
		catch (error) {
			return true;
		}
	}

	checkin_checkin_location(activity = {"active_id": ""}, location = {"latitude": -1, "longitude": -1, "address": ""}) {
		let sign_details = this.checkin_get_details(activity);
		activity["class_id"] = sign_details["clazzId"];
		assert(this.checkin_do_presign(activity));
		assert(this.checkin_do_analysis(activity));
		let ranged = + this.checkin_check_designatedplace(activity);
		let url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax";
		let params = {
			"address": ranged ? location["address"] : "",
			"activeId": activity["active_id"],
			"latitude": ranged ? location["latitude"] : -1,
			"longitude": ranged ? location["longitude"] : -1,
			"fid": 0,
			"appType": 15,
			"ifTiJiao": ranged
		};
		try {
			let res = this.get(url, params);
			return res.text == "success" || res.text == "您已签到过了";
		}
		catch (error) {
			return false;
		}
	}

	checkin_checkin_qrcode(activity = {"active_id": "", "enc": ""}, location = {"latitude": -1, "longitude": -1, "address": ""}) {
		let sign_details = this.checkin_get_details(activity);
		activity["class_id"] = sign_details["clazzId"];
		assert(this.checkin_do_presign(activity));
		assert(this.checkin_do_analysis(activity));
		let ranged = + this.checkin_check_designatedplace(activity);
		let url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax";
		let params = {
			"enc": activity["enc"],
			"activeId": activity["active_id"],
			"location": ranged ? "{\"result\":1,\"latitude\":" + location["latitude"].toString() + ",\"longitude\":" + location["longitude"].toString() + ",\"address\":\"" + location["address"] + "\"}" : "",
			"latitude": ranged ? -1 : location["latitude"],
			"longitude": ranged ? -1 : location["longitude"],
			"fid": 0
		};
		try {
			let res = this.get(url, params);
			return res.text == "success" || res.text == "您已签到过了";
		}
		catch (error) {
			return false;
		}
	}

	checkin_checkin_qrcode_url(qr_url = "", location = {"latitude": -1, "longitude": -1, "address": ""}) {
		if (qr_url.indexOf("https://mobilelearn.chaoxing.com/widget/sign/e"))
			return false;
		let params = Object.fromEntries((new URL(qr_url)).searchParams);
		try {
			activity = {
				"active_id": params["id"],
				"enc": params["enc"]
			}
			return this.checkin_checkin_qrcode(activity, location);
		}
		catch (error) {
			return false;
		}
	}
}
