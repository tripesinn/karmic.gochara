import{c as r}from"./capacitor-bridge.C3S1TWew.js";import"./index.CRukatdg.js";const t={messages:[{role:"assistant",content:"Welcome! Ask me a question about Karmic Gochara analysis."}],currentAnalysisId:null,isLoading:!1},i=document.getElementById("chat-history"),s=document.getElementById("user-input"),a=document.getElementById("send-button");s&&a&&(s.disabled=!1,a.disabled=!1);const m={generate:async e=>(console.log(`[Web Fallback] Sending light prompt to Gemma: ${e.substring(0,50)}...`),await new Promise(n=>setTimeout(n,1500)),`[Gemma Web Fallback] Based on context: ${e.substring(0,40)}... (Use native Android app for true local Gemma inference).`)},l=()=>{i&&(i.innerHTML="",t.messages.forEach(e=>{const n=document.createElement("div");n.className=`message ${e.role}`,n.innerHTML=`
            <strong class="role-tag">${e.role==="user"?"You":"Assistant"}</strong>
            <p>${e.content}</p>
          `,i.appendChild(n)}),i.scrollTop=i.scrollHeight)},d=async()=>{if(!s||!a)return;const e=s.value.trim();if(!(!e||t.isLoading)){t.messages.push({role:"user",content:e}),s.value="",l(),t.isLoading=!0,s.disabled=!0,a.disabled=!0;try{if(!t.currentAnalysisId){console.log("[Flow] Initiating initial analysis...");const u="rom";t.currentAnalysisId=u}const c=`
    Tu es un oracle karmique.
    Utilise UNIQUEMENT le contexte suivant pour répondre à la question de l'utilisateur.
    
    --- CONTEXT ---
    ${sessionStorage.getItem("last_lecture_output")||"Aucune lecture disponible."}
    --- END CONTEXT ---
    
    Question de l'utilisateur: ${e}
  `;let o="";r.isNative()?(console.log("[Chat] Using Native Gemma Synthesis..."),await r.gemma.prepareModel(!1),o=await r.gemma.generate("Tu es un oracle karmique.",c,"synthesis","fr")||"Oracle local indisponible."):o=await m.generate(c),t.messages.push({role:"assistant",content:o})}catch(n){console.error("Error during message handling:",n),t.messages.push({role:"assistant",content:"Error: Could not process request. Please try again."})}finally{t.isLoading=!1,s.disabled=!1,a.disabled=!1,l(),s.focus()}}};a&&a.addEventListener("click",d);s&&s.addEventListener("keypress",e=>{e.key==="Enter"&&d()});l();
