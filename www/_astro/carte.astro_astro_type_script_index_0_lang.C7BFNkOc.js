import{a as m}from"./api.DVb6-CDe.js";import"./index.CRukatdg.js";async function p(){try{const e=await m.profile(),s=document.getElementById("carte-loading"),r=document.getElementById("carte-content");if(s&&(s.style.display="none"),e.ok&&e.profile){r&&r.classList.remove("hidden");const t=e.profile;t.birth_date&&(document.getElementById("chart-date").textContent=t.birth_date),t.birth_time&&(document.getElementById("chart-time").textContent=t.birth_time),t.birth_location&&(document.getElementById("chart-location").textContent=t.birth_location);const i=t.planets_info||[];if(i.length>0){const a=document.getElementById("chart-no-planets");a&&(a.style.display="none");const d=document.getElementById("chart-planets-table");d&&d.classList.remove("hidden");const c=document.getElementById("chart-planets-body");c&&(c.innerHTML="",i.forEach(n=>{const l=n.retrograde,o=document.createElement("tr");o.className="border-b border-cosmic-border/50 last:border-b-0",o.innerHTML=`
                  <td class="py-2 pr-3 text-cosmic-gold font-display text-sm">
                    ${l?"℞ ":""}${n.name||"Inconnu"}
                  </td>
                  <td class="py-2 pr-3 text-cosmic-text">${n.sign||"-"}</td>
                  <td class="py-2 pr-3 text-cosmic-text">${n.degree||0}°</td>
                  <td class="py-2 pr-3 text-cosmic-text">${n.house||"-"}</td>
                  <td class="py-2 text-cosmic-text-dim text-xs italic">
                    ${l?"Retrograde":"Direct"}
                  </td>
                `,c.appendChild(o)}))}}}catch(e){console.error("Erreur checkAccess Carte Astrale:",e)}}p();
