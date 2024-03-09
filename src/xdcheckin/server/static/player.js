async function cameraOn() {
	if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia)
		return;
	navigator.mediaDevices.getUserMedia({
		video: {
			facingMode: {exact: "environment"},
			height: {ideal: 1536},
			width: {ideal: 2048}
		},
		audio: false
	}).then((stream) => {
		let e = document.getElementById("camera-video");
		e.srcObject = stream;
		e.addEventListener("playing", () => {
			if (!e.height)
				resizePlayers();
		});
		e.play();
	}).catch(() => {
		alert("Camera not found or inaccessible. ");
	});
}

async function cameraOff() {
	let e = document.getElementById("camera-video");
	if (!e.srcObject)
		return;
	e.srcObject.getTracks().forEach((track) => {
		track.stop();
	});
	e.srcObject = null;
}

async function resizePlayers() {
	let w = window.innerWidth - getScrollBarWidth();
	document.getElementById("camera-scanresult-div").style.width = w;
	document.getElementById("player0-scanresult-div").style.width =
						      g_player_width = `${w}px`;
	let e = document.getElementById("camera-video");
	Object.assign(e, {
		height: `${parseInt(w * e.videoHeight / e.videoWidth)}`,
		width: `${w}`
	});
	g_player_height = `${parseInt(w / 16 * 9)}px`;
	g_players.forEach((player) => {
		if (player)
			player.setPlayerSize(g_player_width, g_player_height);
	});
}

async function initPlayers() {
	if (initPlayers.calling)
		return;
	initPlayers.calling = true;
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
	initPlayers.calling = false;
}

async function enablePlayers() {
	if (enablePlayers.success || enablePlayers.calling ||
	    !(localStorage.getItem("fid") == "16820"))
		return;
	enablePlayers.calling = true;
	document.getElementById("xdcheckin-title-div").style.display = "flex";
	["s", "0", "1", "2", "3"].forEach((v) => {
		let e = document.getElementById(`player${v}-buttons-div`);
		e.style.display = "flex";
	});
	if (localStorage.getItem("classroom_name"))
		setClassroom(localStorage.getItem("classroom"),
			     localStorage.getItem("classroom_name"))
	else
		randClassroom();
	enablePlayers.success = true;
	enablePlayers.calling = false;
}

async function muteOtherPlayers(player) {
	g_players.forEach((v) => {
		if (v != player)
			v.mute();
	});
	if (player)
		player.setVolume(1);
}
