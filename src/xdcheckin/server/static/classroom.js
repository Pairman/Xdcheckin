async function setClassroom(url, name = "Unknown") {
	document.getElementById("xdcheckin-title-div").innerText =
							   `Xdcheckin: ${name}`;
	localStorage.setItem("classroom_name", name);
	localStorage.setItem("classroom", url);
	const params = new URLSearchParams(
				       decodeURIComponent(new URL(url).search));
	const videos = JSON.parse(params.get("info")).videoPath;
	globalThis.g_player_sources[0] = videos.pptVideo || "";
	globalThis.g_player_sources[1] = videos.teacherTrack || "";
	globalThis.g_player_sources[2] = videos.teacherFull || "";
	globalThis.g_player_sources[3] = videos.studentFull || "";
	initPlayers();
}

async function randClassroom() {
	const b = Math.floor(Math.random() * globalThis.g_buildings.length);
	const c = Math.floor(Math.random() * globalThis.g_buildings[b].length);
	setClassroom(globalThis.g_buildings[b][c],
		     globalThis.g_building_names[b][c]);
}

async function inputClassroom() {
	const input = prompt("Input livestream URL to play:");
	if (input === null)
		return;
	if (isValidUrl(input))
		setClassroom(input, "Unknown");
	else
		alert("Invalid URL.");
}

async function listClassrooms() {
	const e = document.getElementById("classrooms-list-div");
	if (!e)
		return;
	e.replaceChildren(newElement("button", {
		onclick: extractClassroom,
		innerText: "Extract"
	}));
	e.appendChild(newElement("button", {
		onclick: inputClassroom,
		innerText: "Load"
	}));
	e.appendChild(newElement("button", {
		onclick: randClassroom,
		innerText: "Random"
	}));
	globalThis.g_buildings = [];
	globalThis.g_building_names = [];
	for (let building_name in globalThis.g_classroom_urls) {
		e.appendChild(newElement("div", {
			innerText: `${building_name}:`
		}));
		const classrooms = [], classroom_names = [];
		const building = globalThis.g_classroom_urls[building_name];
		for (let c_name in building) {
			e.appendChild(newElement("button", {
				onclick: () => setClassroom(building[c_name],
							    c_name),
				innerText: c_name
			}));
			classrooms.push(building[c_name]);
			classroom_names.push(c_name);
		}
		globalThis.g_buildings.push(classrooms);
		globalThis.g_building_names.push(classroom_names);
	}
}

async function extractClassroom() {
	if (!globalThis.g_logged_in)
		return alert("Login to use this feature.");
	const input = prompt("Input liveId or URL to extract livestream URL:");
	if (input === null)
		return;
	let live_id = input;
	if (isValidUrl(input)) {
		const params = new URLSearchParams(
				     decodeURIComponent(new URL(input).search));
		live_id = JSON.parse(params.get("liveId"));
	}
	else if (input === "" || isNaN(input))
		return alert("Invalid input.");
	try {
		const res = await post("/newesxidian/extract_url", live_id);
		const params = new URLSearchParams(
				  decodeURIComponent(new URL(res.text).search));
		const info = JSON.parse(params.get("info"));
		assert(info.type == "1" && Object.keys(info.videoPath).length);
		prompt("Extracted URL:", res.text);
	}
	catch (err) {
		alert("Failed to extract URL.");
	}
}
