async function setLocation(loc, name) {
	g_location = {
		"latitude": loc.latitude,
		"longitude": loc.longitude,
		"address": loc.address
	};
	localStorage.setItem("location_", JSON.stringify(g_location));
	localStorage.setItem("location_name", name);
	document.getElementById("location-current-div").innerText =
						     `Current location ${name}`;
}

async function inputLocation() {
	let latitude, longitude, address;
	if (!(latitude = prompt("Input latitude:")) || isNaN(latitude))
		return latitude === null ? undefined : alert("Invalid input.");
	if (!(longitude = prompt("Input latitude:")) || isNaN(longitude))
		return longitude === null ? undefined : alert("Invalid input.");
	if (!(address = prompt("Input address:")) || /[()\[\]{}]/.test(address))
		return address === null ? undefined : alert("Invalid input.");
	setLocation({
		"latitude": latitude,
		"longitude": longitude,
		"address": address
	}, `Input(${latitude}, ${longitude}, ${address})`);
}

async function listLocations() {
	let e = document.getElementById("locations-list-div");
	e.appendChild(newElement("button", {
		innerText: "Input",
		onclick: inputLocation
	}));
	for (let buildingName in g_locations) {
		e.appendChild(newElement("button", {
			innerText: buildingName,
			onclick: () => setLocation(g_locations[buildingName],
						   buildingName),
		}));
	}
	let loc = localStorage.getItem('location_');
	if (!loc) {
		setLocation(g_locations["B楼"], "B楼");
	}
	else
		setLocation(JSON.parse(loc),
			    localStorage.getItem('location_name'));
}
