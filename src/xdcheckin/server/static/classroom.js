async function setClassroom(url, name = "Unknown") {
	document.getElementById("xdcheckin-title-div").innerText =
							   `Xdcheckin: ${name}`;
	localStorage.setItem("classroom_name", name);
	localStorage.setItem("classroom", url);
	let params = new URLSearchParams(
				       decodeURIComponent(new URL(url).search));
	let videos = JSON.parse(params.get("info")).videoPath;
	g_player_sources[0] = videos.pptVideo || "";
	g_player_sources[1] = videos.teacherTrack || "";
	g_player_sources[2] = videos.teacherFull || "";
	g_player_sources[3] = videos.studentFull || "";
	initPlayers();
}

async function randClassroom() {
	let b = Math.floor(Math.random() * g_buildings.length);
	let c = Math.floor(Math.random() * g_buildings[b].length);
	setClassroom(g_buildings[b][c], g_building_names[b][c]);
}

async function inputClassroom() {
	let input = prompt("Input livestream URL to play:");
	if (input === null)
		return;
	if (isValidUrl(input))
		setClassroom(input, "Unknown");
	else
		alert("Invalid URL.");
}

async function listClassrooms() {
	let e = document.getElementById("classrooms-list-div");
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
	g_buildings = [];
	g_building_names = [];
	for (let building_name in g_classroom_urls) {
		e.appendChild(newElement("div", {
			innerText: `${building_name}:`
		}));
		let classrooms = [], classroom_names = [];
		let building = g_classroom_urls[building_name];
		for (let c_name in building) {
			e.appendChild(newElement("button", {
				onclick: () => setClassroom(building[c_name],
							    c_name),
				innerText: c_name
			}));
			classrooms.push(building[c_name]);
			classroom_names.push(c_name);
		}
		g_buildings.push(classrooms);
		g_building_names.push(classroom_names);
	}
}

async function extractClassroom() {
	if (!g_logged_in)
		return alert("Login to use this feature.");
	let input = prompt("Input liveId or URL to extract livestream URL:");
	if (input === null)
		return;
	let live_id = input;
	if (isValidUrl(input)) {
		let params = new URLSearchParams(
				     decodeURIComponent(new URL(input).search));
		live_id = JSON.parse(params.get("liveId"));
	}
	else if (input === "" || isNaN(input))
		return alert("Invalid input.");
	try {
		let res = await post("/newesxidian/extract_url", live_id);
		let params = new URLSearchParams(
				  decodeURIComponent(new URL(res.text).search));
		let info = JSON.parse(params.get("info"));
		assert(info.type == "1" && Object.keys(info.videoPath).length);
		prompt("Extracted URL:", res.text);
	}
	catch (err) {
		alert("Failed to extract URL.");
	}
}
