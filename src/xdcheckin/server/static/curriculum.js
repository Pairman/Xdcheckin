async function getCurriculum(with_live = false) {
	if (getCurriculum.calling)
		return;
	getCurriculum.calling = true;
	let curriculum = (await post("/chaoxing/get_curriculum",
				    with_live)).json();
	let d = newElement("div", {
		innerText: `Current: year ${curriculum.details.year}, ` +
			   `semester ${curriculum.details.semester}, ` +
			   `week ${curriculum.details.week}.`
	});
	document.getElementById("curriculum-list-div").replaceChildren(d);
	if (!Object.keys(curriculum.lessons).length) {
		d.innerText += " No curriculum.";
		return getCurriculum.calling = false;
	}
	let table = newElement("table", {
		style: "border = 1"
	});
	let tb = table.appendChild(newElement("tbody"));
	let timetable = curriculum.details.time.timetable;
	for (let class_id in curriculum.lessons) {
		let lesson = curriculum.lessons[class_id];
		let tr = tb.appendChild(newElement("tr"));
		let td = tr.appendChild(newElement("td"));
		td.appendChild(document.createTextNode(lesson.name));
		td = tr.appendChild(newElement("td"));
		lesson.teacher.forEach((v, i) => {
			if (i)
				td.appendChild(newElement("br"));
			td.appendChild(document.createTextNode(`${v}`));
		});
		td = tr.appendChild(newElement("td"));
		lesson.time.forEach((v, i) => {
			if (i)
				td.appendChild(newElement("br"));
			let bgn = timetable[v.period_begin - 1].slice(0, 5);
			let end = timetable[v.period_end - 1].slice(6, 11);
			td.appendChild(document.createTextNode(`${v.day}  ` +
							      `${bgn}-${end}`));

		});
		td = tr.appendChild(newElement("td"));
		if (with_live && "livestream" in lesson) {
			let url = lesson.livestream.url;
			let name = lesson.location;
			td.appendChild(newElement("button", {
				innerText: name,
				onclick: () => {
					setClassroom(`${url}`, `${name}`);
				}
			}));
		}
		else
			td.appendChild(document.createTextNode(
							      lesson.location));
	}
	document.getElementById("curriculum-list-div").appendChild(table);
	getCurriculum.calling = false;
}