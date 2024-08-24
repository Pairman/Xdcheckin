async function getCurriculum(with_live = false) {
	if (getCurriculum.calling)
		return;
	getCurriculum.calling = true;
	const curriculum = (await post("/chaoxing/get_curriculum",
				    with_live)).json();
	const d = newElement("div", {
		innerText: `Current year ${curriculum.details.year}, ` +
			   `semester ${curriculum.details.semester}, ` +
			   `week ${curriculum.details.week}.`
	});
	document.getElementById("curriculum-list-div").replaceChildren(d);
	if (!Object.keys(curriculum.lessons).length) {
		d.innerText += " No curriculum.";
		return getCurriculum.calling = false;
	}
	const table = newElement("table", {
		style: "border = 1"
	});
	const tb = table.appendChild(newElement("tbody"));
	const timetable = curriculum.details.time.timetable;
	for (let class_id in curriculum.lessons) {
		const lesson = curriculum.lessons[class_id];
		const tr = tb.appendChild(newElement("tr"));
		let td = tr.appendChild(newElement("td"));
		td.appendChild(document.createTextNode(lesson.name));
		td = tr.appendChild(newElement("td"));
		lesson.teachers.forEach((v, i) => {
			if (i)
				td.appendChild(newElement("br"));
			td.appendChild(document.createTextNode(v));
		});
		td = tr.appendChild(newElement("td"));
		lesson.times.forEach((v, i) => {
			if (i)
				td.appendChild(newElement("br"));
			const bgn = timetable[v.period_begin - 1].slice(0, 5);
			const end = timetable[v.period_end - 1].slice(6, 11);
			td.appendChild(document.createTextNode(`${v.day}  ` +
							      `${bgn}-${end}`));

		});
		td = tr.appendChild(newElement("td"));
		if (!lesson.livestreams)
			lesson.locations.forEach((v, i) => {
				if (i)
					td.appendChild(newElement("br"));
				td.appendChild(document.createTextNode(v));
			});
		else
			lesson.livestreams.forEach((v, i) => {
				if (i)
					td.appendChild(newElement("br"));
				td.appendChild(newElement("button", {
					innerText: v.location,
					onclick: () => setClassroom(v.url,
								    v.location)
				}));
			});
	}
	document.getElementById("curriculum-list-div").appendChild(table);
	getCurriculum.calling = false;
}
