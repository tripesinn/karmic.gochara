import{c as l}from"./capacitor-bridge.C3S1TWew.js";import"./index.CRukatdg.js";const t={messages:[{role:"assistant",content:"Welcome! Ask me a question about Karmic Gochara analysis."}],currentAnalysisId:null,isLoading:!1},i=document.getElementById("chat-history"),s=document.getElementById("user-input"),a=document.getElementById("send-button");s&&a&&(s.disabled=!1,a.disabled=!1);const m={generate:async e=>(console.log(`[Web Fallback] Sending light prompt to Gemma: ${e.substring(0,50)}...`),await new Promise(n=>setTimeout(n,1500)),`[Gemma Web Fallback] Based on context: ${e.substring(0,40)}... (Use native Android app for true local Gemma inference).`)},c=()=>{i&&(i.innerHTML="",t.messages.forEach(e=>{const n=document.createElement("div"),o=e.role==="user";n.className=`p-4 rounded-lg max-w-[90%] sm:max-w-[80%] ${o?"ml-auto bg-cosmic-gold/10 border border-cosmic-gold/20":"mr-auto bg-cosmic-void border border-cosmic-border"}`,n.innerHTML=`
            <strong class="block text-xs uppercase tracking-wider mb-2 font-display ${o?"text-cosmic-gold":"text-cosmic-text-dim"}">${o?"Vous":"Oracle"}</strong>
            <p class="text-cosmic-text leading-relaxed whitespace-pre-wrap">${e.content}</p>
          `,i.appendChild(n)}),i.scrollTop=i.scrollHeight)},d=async()=>{if(!s||!a)return;const e=s.value.trim();if(!(!e||t.isLoading)){t.messages.push({role:"user",content:e}),s.value="",c(),t.isLoading=!0,s.disabled=!0,a.disabled=!0;try{if(!t.currentAnalysisId){console.log("[Flow] Initiating initial analysis...");const u="rom";t.currentAnalysisId=u}const o=`
    Agis comme un Oracle Karmique sage et profond.
    L'utilisateur va te poser une question ou te soumettre une réflexion basée sur sa lecture astrologique (contexte ci-dessous).
    Ne te contente pas de répéter le contexte. Développe, offre une perspective spirituelle, explique le sens caché des planètes impliquées, et guide l'utilisateur avec bienveillance.
    
    --- CONTEXTE DE LA LECTURE ---
    ${sessionStorage.getItem("last_lecture_output")||"Aucune lecture disponible."}
    --- FIN DU CONTEXTE ---
    
    Message de l'utilisateur: ${e}
    
    Réponse de l'Oracle:
  `;let r="";l.isNative()?(console.log("[Chat] Using Native Gemma Synthesis..."),await l.gemma.prepareModel(!1),r=await l.gemma.generate("Tu es un Oracle Karmique sage, mystique et bienveillant. Fournis des réponses profondes et spirituelles.",o,"synthesis","fr")||"Oracle local indisponible."):r=await m.generate(o),t.messages.push({role:"assistant",content:r})}catch(n){console.error("Error during message handling:",n),t.messages.push({role:"assistant",content:"Error: Could not process request. Please try again."})}finally{t.isLoading=!1,s.disabled=!1,a.disabled=!1,c(),s.focus()}}};a&&a.addEventListener("click",d);s&&s.addEventListener("keypress",e=>{e.key==="Enter"&&d()});c();window.openChatWithQuote=e=>{s&&(s.value=`Peux-tu m'expliquer ce que tu entends par : "${e}" ? `,s.focus())};
