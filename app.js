const categories = {
  "Broadcast Graphics": "onair-graphics.json",
  "Newsroom & NRCS": "newsroom.json",
  "Playout & Automation": "playout.json",
  "IP / SMPTE 2110": "ip-video.json",
  "Audio Technology": "audio.json",
  "Cloud & AI": "cloud-ai.json"
};

const container = document.getElementById("content");

for (const [title, file] of Object.entries(categories)) {
  fetch(`data/${file}`)
    .then(res => res.json())
    .then(items => {
      const section = document.createElement("section");
      section.innerHTML = `<h2>${title}</h2>`;

      items.slice(0, 10).forEach(i => {
        section.innerHTML += `
          <article>
            <img src="${i.image || 'assets/fallback.jpg'}"
                 onerror="this.src='assets/fallback.jpg'">
            <div>
              <a href="${i.link}" target="_blank">${i.title}</a>
              <p>${i.source}</p>
            </div>
          </article>`;
      });

      container.appendChild(section);
    });
}
