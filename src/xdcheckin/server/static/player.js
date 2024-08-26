async function enableCamera() {
	if (!navigator.mediaDevices)
		return;
	const devices = await navigator.mediaDevices.enumerateDevices();
	if (!devices.filter(v => v.kind == "videoinput").length)
		return;
	[
		"camera-buttons-div", "camera-div", "camera-scanresult-div"
	].forEach(displayTag);
}

async function cameraOn() {
	navigator.mediaDevices.getUserMedia({
		video: {
			facingMode: {exact: "environment"},
			height: {ideal: 1536},
			width: {ideal: 2048}
		},
		audio: false
	}).then(stream => {
		const e = document.getElementById("camera-video");
		e.srcObject = stream;
		e.addEventListener("playing", () => {
			if (!e.height)
				resizePlayers();
		});
		e.play();
	}).catch(() => alert("Error opening camera."));
}

async function cameraOff() {
	const e = document.getElementById("camera-video");
	if (!e.srcObject)
		return;
	e.srcObject.getTracks().forEach(track => track.stop());
	e.srcObject = null;
}

async function resizePlayers() {
	const w = window.innerWidth;
	globalThis.g_player_width = `${w}px`;
	[
		"camera-scanresult-div", "player0-scanresult-div",
		"player2-scanresult-div"
	].forEach(id => document.getElementById(id).style.width =
						     globalThis.g_player_width);
	const e = document.getElementById("camera-video");
	Object.assign(e, {
		height: `${parseInt(w * e.videoHeight / e.videoWidth)}`,
		width: `${w}`
	});
	globalThis.g_player_height = `${parseInt(w / 16 * 9)}px`;
	globalThis.g_players.forEach(player => {
		if (player)
			player.setPlayerSize(globalThis.g_player_width,
					     globalThis.g_player_height);
	});
}

async function initPlayers() {
	globalThis.g_players.forEach((player, i) => {
		if (player)
			player.dispose();
		if (isValidUrl(globalThis.g_player_sources[i]))
			player = globalThis.g_players[i] = new Aliplayer({
				id: `player${i}-div`,
				isLive: true,
				width: globalThis.g_player_width,
				height: globalThis.g_player_height,
				source: globalThis.g_player_sources[i],
				playsinline: true,
				autoplay: i == 0,
				mute: true
			}, () => {});
	});
}

async function enablePlayers() {
	if (enablePlayers.success || enablePlayers.calling ||
	    !["16820", "146332", "147335", "2403"]
	    .includes(localStorage.getItem("fid")))
		return;
	enablePlayers.calling = true;
	[
		"s", "0", "1", "2", "3"
	].forEach(v => displayTag(`player${v}-buttons-div`));
	if (localStorage.getItem("classroom_name"))
		setClassroom(localStorage.getItem("classroom"),
			     localStorage.getItem("classroom_name"));
	else
		randClassroom();
	enablePlayers.success = true;
	enablePlayers.calling = false;
}

async function muteOtherPlayers(player) {
	globalThis.g_players.forEach(v => {
		if (v != player)
			v.mute();
	});
	if (player)
		player.setVolume(1);
}
