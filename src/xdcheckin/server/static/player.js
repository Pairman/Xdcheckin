async function enableCamera() {
	if (!navigator.mediaDevices)
		return;
	let devices = await navigator.mediaDevices.enumerateDevices();
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
		let e = document.getElementById("camera-video");
		e.srcObject = stream;
		e.addEventListener("playing", () => {
			if (!e.height)
				resizePlayers();
		});
		e.play();
	}).catch(() => alert("Error opening camera."));
}

async function cameraOff() {
	let e = document.getElementById("camera-video");
	if (!e.srcObject)
		return;
	e.srcObject.getTracks().forEach(track => track.stop());
	e.srcObject = null;
}

async function resizePlayers() {
	let w = window.innerWidth;
	document.getElementById("camera-scanresult-div").style.width = `${w}px`;
	document.getElementById("player0-scanresult-div").style.width =
						      g_player_width = `${w}px`;
	let e = document.getElementById("camera-video");
	Object.assign(e, {
		height: `${parseInt(w * e.videoHeight / e.videoWidth)}`,
		width: `${w}`
	});
	g_player_height = `${parseInt(w / 16 * 9)}px`;
	g_players.forEach(player => {
		if (player)
			player.setPlayerSize(g_player_width, g_player_height);
	});
}

async function initPlayers() {
	g_players.forEach((player, i) => {
		if (player)
			player.dispose();
		if (isValidUrl(g_player_sources[i]))
			player = g_players[i] = new Aliplayer({
				id: `player${i}-div`,
				isLive: true,
				width: g_player_width,
				height: g_player_height,
				playsinline: true,
				source: g_player_sources[i]
			}, () => {
				player.mute();
				if (i)
					player.stop();
				else
					player.play();
			});
	});
}

async function enablePlayers() {
	if (enablePlayers.success || enablePlayers.calling ||
	    !(localStorage.getItem("fid") == "16820"))
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
	g_players.forEach(v => {
		if (v != player)
			v.mute();
	});
	if (player)
		player.setVolume(1);
}
