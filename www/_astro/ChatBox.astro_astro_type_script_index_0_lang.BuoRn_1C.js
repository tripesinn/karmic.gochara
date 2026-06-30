import{c as l}from"./capacitor-bridge.C3S1TWew.js";import"./index.CRukatdg.js";const t={messages:[{role:"assistant",content:"Welcome! Ask me a question about Karmic Gochara analysis."}],currentAnalysisId:null,isLoading:!1},r=document.getElementById("chat-history"),s=document.getElementById("user-input"),n=document.getElementById("send-button");s&&n&&(s.disabled=!1,n.disabled=!1);const m={generate:async e=>(console.log(`[Web Fallback] Sending light prompt to Gemma: ${e.substring(0,50)}...`),await new Promise(a=>setTimeout(a,1500)),`[Gemma Web Fallback] Based on context: ${e.substring(0,40)}... (Use native Android app for true local Gemma inference).`)},c=()=>{r&&(r.innerHTML="",t.messages.forEach(e=>{const a=document.createElement("div"),o=e.role==="user";a.className=`p-4 rounded-lg max-w-[90%] sm:max-w-[80%] ${o?"ml-auto bg-cosmic-gold/10 border border-cosmic-gold/20":"mr-auto bg-cosmic-void border border-cosmic-border"}`,a.innerHTML=`
            <strong class="block text-xs uppercase tracking-wider mb-2 font-display ${o?"text-cosmic-gold":"text-cosmic-text-dim"}">${o?"Vous":"Oracle"}</strong>
            <p class="text-cosmic-text leading-relaxed whitespace-pre-wrap">${e.content}</p>
          `,r.appendChild(a)}),r.scrollTop=r.scrollHeight)},u=async()=>{if(!s||!n)return;const e=s.value.trim();if(!(!e||t.isLoading)){t.messages.push({role:"user",content:e}),s.value="",c(),t.isLoading=!0,s.disabled=!0,n.disabled=!0;try{if(!t.currentAnalysisId){console.log("[Flow] Initiating initial analysis...");const d="rom";t.currentAnalysisId=d}const o=`
    Tu es un oracle karmique.
    Utilise UNIQUEMENT le contexte suivant pour répondre à la question de l'utilisateur.
    
    --- CONTEXT ---
    ${sessionStorage.getItem("last_lecture_output")||"Aucune lecture disponible."}
    --- END CONTEXT ---
    
    Question de l'utilisateur: ${e}
  `;let i="";l.isNative()?(console.log("[Chat] Using Native Gemma Synthesis..."),await l.gemma.prepareModel(!1),i=await l.gemma.generate("Tu es un oracle karmique.",o,"synthesis","fr")||"Oracle local indisponible."):i=await m.generate(o),t.messages.push({role:"assistant",content:i})}catch(a){console.error("Error during message handling:",a),t.messages.push({role:"assistant",content:"Error: Could not process request. Please try again."})}finally{t.isLoading=!1,s.disabled=!1,n.disabled=!1,c(),s.focus()}}};n&&n.addEventListener("click",u);s&&s.addEventListener("keypress",e=>{e.key==="Enter"&&u()});c();
