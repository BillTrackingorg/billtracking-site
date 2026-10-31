import{A as e,J as g,z as r}from"./bt-chunk-JZ4YJERE.js";import{F as d,O as p,P as N,Q as x,S as b,T as S,U as T,l as h}from"./bt-chunk-KHYOEOZ5.js";import{d as i}from"./bt-chunk-ICI4HODK.js";var _={caption:x},I="bt-notif-panel",P=t=>`bt-notif-tab-${t}`,H=t=>t.join(">"),K=t=>t.split(">"),k=t=>`${i[t].names.short} tracker`;function E(t,a){let{row:o,path:s,isLeaf:$,scope:l}=a,f=s.length-1,n=H(s),y=t.open.has(n),m=k(t.selected),O=p.map(c=>{let u=T(c,t.switches,t.selected,s);return e`<span class="bt-tcell"><input type="checkbox" class="bt-tbox" data-row="${n}"
      data-col="${c}" data-state="${u}"${u==="on"?r(" checked"):r("")}
      aria-label="${b(o,l,m,c)}"></span>`}),w=$?e`<span class="bt-tex" aria-hidden="true"></span>`:e`<button type="button" class="bt-tex" data-open="${n}"
        aria-expanded="${y?"true":"false"}"
        aria-label="${b(o,l,m)}">${g(y?"chevron-down":"chevron-right")}</button>`;return e`<div class="bt-trow" data-depth="${String(f)}">
    <div class="bt-tline">${w}<span class="bt-tlabel${f===0?" is-section":""}">${o.label}</span>${O}</div>
    <p class="bt-tcap">${o.caption}</p>
  </div>`}function C(){return e`<div class="bt-thead"><span class="bt-thgap"></span>${p.map(t=>e`<span class="bt-thcol">${N[t].head}</span>`)}</div>`}function F(t){return G({name:h(d.notifGroup),scope:t.scope,selected:t.selected,tabId:P,panelId:I})}function G(t){return t.scope.length===0?e``:t.scope.length===1?e`<p class="bt-tsolo" id="${t.tabId(t.selected)}">${k(t.selected)}</p>`:e`<div class="bt-tseg" role="tablist" aria-label="${t.name}">${t.scope.map(a=>e`<button type="button" role="tab" id="${t.tabId(a)}"
      data-polity="${a}"${t.mark??r("")} aria-controls="${t.panelId}"
      aria-selected="${a===t.selected?"true":"false"}"${t.labels?.[a]?e` aria-label="${t.labels[a].a11y}"`:r("")}>${t.labels?.[a]?.text??i[a].names.short}</button>`)}</div>`}function M(t){switch(t.state){case"signed-out":case"loading":case"failed":return e``;case"no-scope":return e``;case"ready":break;default:return t}let a=t.scope.length>1?"tabpanel":"group",o=e`${F(t)}<div class="bt-tree" id="${I}" role="${a}"
        aria-labelledby="${P(t.selected)}">${C()}${S(t.selected).filter(({path:s})=>s.every(($,l)=>l===s.length-1||t.open.has(H(s.slice(0,l+1))))).map(s=>E(t,s))}</div>`;return e`<h3 class="acct-eyebrow">${d.notifGroup}</h3>
<p class="bt-row-cap bt-keyword-cap">${_.caption}</p>
<div class="acct-card bt-notif" data-polity="${t.selected}">
  ${o}
</div>`}export{K as a,G as b,M as c};
