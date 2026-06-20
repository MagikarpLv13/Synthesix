"use strict";(()=>{var Et=Object.defineProperty;var wt=Object.getOwnPropertyDescriptor;var h=(i,t,e,s)=>{for(var r=s>1?void 0:s?wt(t,e):t,o=i.length-1,n;o>=0;o--)(n=i[o])&&(r=(s?n(t,e,r):n(r))||r);return s&&r&&Et(t,e,r),r};var x=`
:host {
  --accent: #2563EB;
  --accent-strong: #1D4ED8;
  --accent-soft: #DBEAFE;
  --accent-ink: #1D4ED8;
  --surface: #FFFFFF;
  --surface-2: #F1F5F9;
  --text: #0F172A;
  --muted: #64748B;
  --line: #CBD5E1;
  --success: #16A34A;
  --success-soft: #DCFCE7;
  --success-ink: #166534;
  --danger: #DC2626;
  --radius-sm: 6px;
  --radius-md: 8px;
  --shadow-soft: 0 8px 22px rgba(15, 23, 42, 0.18);
}
`;var I=globalThis,Y=I.ShadowRoot&&(I.ShadyCSS===void 0||I.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,J=Symbol(),lt=new WeakMap,R=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==J)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(Y&&t===void 0){let s=e!==void 0&&e.length===1;s&&(t=lt.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&lt.set(e,t))}return t}toString(){return this.cssText}},E=i=>new R(typeof i=="string"?i:i+"",void 0,J),_=(i,...t)=>{let e=i.length===1?i[0]:t.reduce((s,r,o)=>s+(n=>{if(n._$cssResult$===!0)return n.cssText;if(typeof n=="number")return n;throw Error("Value passed to 'css' function must be a 'css' function result: "+n+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(r)+i[o+1],i[0]);return new R(e,i,J)},ct=(i,t)=>{if(Y)i.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let s=document.createElement("style"),r=I.litNonce;r!==void 0&&s.setAttribute("nonce",r),s.textContent=e.cssText,i.appendChild(s)}},Z=Y?i=>i:i=>i instanceof CSSStyleSheet?(t=>{let e="";for(let s of t.cssRules)e+=s.cssText;return E(e)})(i):i;var{is:Ct,defineProperty:St,getOwnPropertyDescriptor:Pt,getOwnPropertyNames:kt,getOwnPropertySymbols:Mt,getPrototypeOf:Ut}=Object,V=globalThis,ht=V.trustedTypes,Nt=ht?ht.emptyScript:"",Tt=V.reactiveElementPolyfillSupport,H=(i,t)=>i,D={toAttribute(i,t){switch(t){case Boolean:i=i?Nt:null;break;case Object:case Array:i=i==null?i:JSON.stringify(i)}return i},fromAttribute(i,t){let e=i;switch(t){case Boolean:e=i!==null;break;case Number:e=i===null?null:Number(i);break;case Object:case Array:try{e=JSON.parse(i)}catch{e=null}}return e}},X=(i,t)=>!Ct(i,t),dt={attribute:!0,type:String,converter:D,reflect:!1,useDefault:!1,hasChanged:X};Symbol.metadata??=Symbol("metadata"),V.litPropertyMetadata??=new WeakMap;var y=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=dt){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let s=Symbol(),r=this.getPropertyDescriptor(t,s,e);r!==void 0&&St(this.prototype,t,r)}}static getPropertyDescriptor(t,e,s){let{get:r,set:o}=Pt(this.prototype,t)??{get(){return this[e]},set(n){this[e]=n}};return{get:r,set(n){let l=r?.call(this);o?.call(this,n),this.requestUpdate(t,l,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??dt}static _$Ei(){if(this.hasOwnProperty(H("elementProperties")))return;let t=Ut(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(H("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(H("properties"))){let e=this.properties,s=[...kt(e),...Mt(e)];for(let r of s)this.createProperty(r,e[r])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[s,r]of e)this.elementProperties.set(s,r)}this._$Eh=new Map;for(let[e,s]of this.elementProperties){let r=this._$Eu(e,s);r!==void 0&&this._$Eh.set(r,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let s=new Set(t.flat(1/0).reverse());for(let r of s)e.unshift(Z(r))}else t!==void 0&&e.push(Z(t));return e}static _$Eu(t,e){let s=e.attribute;return s===!1?void 0:typeof s=="string"?s:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return ct(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ET(t,e){let s=this.constructor.elementProperties.get(t),r=this.constructor._$Eu(t,s);if(r!==void 0&&s.reflect===!0){let o=(s.converter?.toAttribute!==void 0?s.converter:D).toAttribute(e,s.type);this._$Em=t,o==null?this.removeAttribute(r):this.setAttribute(r,o),this._$Em=null}}_$AK(t,e){let s=this.constructor,r=s._$Eh.get(t);if(r!==void 0&&this._$Em!==r){let o=s.getPropertyOptions(r),n=typeof o.converter=="function"?{fromAttribute:o.converter}:o.converter?.fromAttribute!==void 0?o.converter:D;this._$Em=r;let l=n.fromAttribute(e,o.type);this[r]=l??this._$Ej?.get(r)??l,this._$Em=null}}requestUpdate(t,e,s,r=!1,o){if(t!==void 0){let n=this.constructor;if(r===!1&&(o=this[t]),s??=n.getPropertyOptions(t),!((s.hasChanged??X)(o,e)||s.useDefault&&s.reflect&&o===this._$Ej?.get(t)&&!this.hasAttribute(n._$Eu(t,s))))return;this.C(t,e,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:s,reflect:r,wrapped:o},n){s&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,n??e??this[t]),o!==!0||n!==void 0)||(this._$AL.has(t)||(this.hasUpdated||s||(e=void 0),this._$AL.set(t,e)),r===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[r,o]of this._$Ep)this[r]=o;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[r,o]of s){let{wrapped:n}=o,l=this[r];n!==!0||this._$AL.has(r)||l===void 0||this.C(r,void 0,o,l)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(e)):this._$EM()}catch(s){throw t=!1,this._$EM(),s}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};y.elementStyles=[],y.shadowRootOptions={mode:"open"},y[H("elementProperties")]=new Map,y[H("finalized")]=new Map,Tt?.({ReactiveElement:y}),(V.reactiveElementVersions??=[]).push("2.1.2");var it=globalThis,pt=i=>i,K=it.trustedTypes,ut=K?K.createPolicy("lit-html",{createHTML:i=>i}):void 0,$t="$lit$",w=`lit$${Math.random().toFixed(9).slice(2)}$`,xt="?"+w,Lt=`<${xt}>`,k=document,j=()=>k.createComment(""),q=i=>i===null||typeof i!="object"&&typeof i!="function",ot=Array.isArray,Rt=i=>ot(i)||typeof i?.[Symbol.iterator]=="function",G=`[ 	
\f\r]`,F=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,ft=/-->/g,mt=/>/g,S=RegExp(`>|${G}(?:([^\\s"'>=/]+)(${G}*=${G}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),bt=/'/g,gt=/"/g,_t=/^(?:script|style|textarea|title)$/i,nt=i=>(t,...e)=>({_$litType$:i,strings:t,values:e}),g=nt(1),Xt=nt(2),Kt=nt(3),M=Symbol.for("lit-noChange"),d=Symbol.for("lit-nothing"),vt=new WeakMap,P=k.createTreeWalker(k,129);function yt(i,t){if(!ot(i)||!i.hasOwnProperty("raw"))throw Error("invalid template strings array");return ut!==void 0?ut.createHTML(t):t}var Ht=(i,t)=>{let e=i.length-1,s=[],r,o=t===2?"<svg>":t===3?"<math>":"",n=F;for(let l=0;l<e;l++){let a=i[l],u,f,c=-1,$=0;for(;$<a.length&&(n.lastIndex=$,f=n.exec(a),f!==null);)$=n.lastIndex,n===F?f[1]==="!--"?n=ft:f[1]!==void 0?n=mt:f[2]!==void 0?(_t.test(f[2])&&(r=RegExp("</"+f[2],"g")),n=S):f[3]!==void 0&&(n=S):n===S?f[0]===">"?(n=r??F,c=-1):f[1]===void 0?c=-2:(c=n.lastIndex-f[2].length,u=f[1],n=f[3]===void 0?S:f[3]==='"'?gt:bt):n===gt||n===bt?n=S:n===ft||n===mt?n=F:(n=S,r=void 0);let A=n===S&&i[l+1].startsWith("/>")?" ":"";o+=n===F?a+Lt:c>=0?(s.push(u),a.slice(0,c)+$t+a.slice(c)+w+A):a+w+(c===-2?l:A)}return[yt(i,o+(i[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),s]},z=class i{constructor({strings:t,_$litType$:e},s){let r;this.parts=[];let o=0,n=0,l=t.length-1,a=this.parts,[u,f]=Ht(t,e);if(this.el=i.createElement(u,s),P.currentNode=this.el.content,e===2||e===3){let c=this.el.content.firstChild;c.replaceWith(...c.childNodes)}for(;(r=P.nextNode())!==null&&a.length<l;){if(r.nodeType===1){if(r.hasAttributes())for(let c of r.getAttributeNames())if(c.endsWith($t)){let $=f[n++],A=r.getAttribute(c).split(w),B=/([.?@])?(.*)/.exec($);a.push({type:1,index:o,name:B[2],strings:A,ctor:B[1]==="."?tt:B[1]==="?"?et:B[1]==="@"?st:N}),r.removeAttribute(c)}else c.startsWith(w)&&(a.push({type:6,index:o}),r.removeAttribute(c));if(_t.test(r.tagName)){let c=r.textContent.split(w),$=c.length-1;if($>0){r.textContent=K?K.emptyScript:"";for(let A=0;A<$;A++)r.append(c[A],j()),P.nextNode(),a.push({type:2,index:++o});r.append(c[$],j())}}}else if(r.nodeType===8)if(r.data===xt)a.push({type:2,index:o});else{let c=-1;for(;(c=r.data.indexOf(w,c+1))!==-1;)a.push({type:7,index:o}),c+=w.length-1}o++}}static createElement(t,e){let s=k.createElement("template");return s.innerHTML=t,s}};function U(i,t,e=i,s){if(t===M)return t;let r=s!==void 0?e._$Co?.[s]:e._$Cl,o=q(t)?void 0:t._$litDirective$;return r?.constructor!==o&&(r?._$AO?.(!1),o===void 0?r=void 0:(r=new o(i),r._$AT(i,e,s)),s!==void 0?(e._$Co??=[])[s]=r:e._$Cl=r),r!==void 0&&(t=U(i,r._$AS(i,t.values),r,s)),t}var Q=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:s}=this._$AD,r=(t?.creationScope??k).importNode(e,!0);P.currentNode=r;let o=P.nextNode(),n=0,l=0,a=s[0];for(;a!==void 0;){if(n===a.index){let u;a.type===2?u=new O(o,o.nextSibling,this,t):a.type===1?u=new a.ctor(o,a.name,a.strings,this,t):a.type===6&&(u=new rt(o,this,t)),this._$AV.push(u),a=s[++l]}n!==a?.index&&(o=P.nextNode(),n++)}return P.currentNode=k,r}p(t){let e=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}},O=class i{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,r){this.type=2,this._$AH=d,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=r,this._$Cv=r?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=U(this,t,e),q(t)?t===d||t==null||t===""?(this._$AH!==d&&this._$AR(),this._$AH=d):t!==this._$AH&&t!==M&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):Rt(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==d&&q(this._$AH)?this._$AA.nextSibling.data=t:this.T(k.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:s}=t,r=typeof s=="number"?this._$AC(t):(s.el===void 0&&(s.el=z.createElement(yt(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===r)this._$AH.p(e);else{let o=new Q(r,this),n=o.u(this.options);o.p(e),this.T(n),this._$AH=o}}_$AC(t){let e=vt.get(t.strings);return e===void 0&&vt.set(t.strings,e=new z(t)),e}k(t){ot(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,s,r=0;for(let o of t)r===e.length?e.push(s=new i(this.O(j()),this.O(j()),this,this.options)):s=e[r],s._$AI(o),r++;r<e.length&&(this._$AR(s&&s._$AB.nextSibling,r),e.length=r)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let s=pt(t).nextSibling;pt(t).remove(),t=s}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},N=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,r,o){this.type=1,this._$AH=d,this._$AN=void 0,this.element=t,this.name=e,this._$AM=r,this.options=o,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=d}_$AI(t,e=this,s,r){let o=this.strings,n=!1;if(o===void 0)t=U(this,t,e,0),n=!q(t)||t!==this._$AH&&t!==M,n&&(this._$AH=t);else{let l=t,a,u;for(t=o[0],a=0;a<o.length-1;a++)u=U(this,l[s+a],e,a),u===M&&(u=this._$AH[a]),n||=!q(u)||u!==this._$AH[a],u===d?t=d:t!==d&&(t+=(u??"")+o[a+1]),this._$AH[a]=u}n&&!r&&this.j(t)}j(t){t===d?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},tt=class extends N{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===d?void 0:t}},et=class extends N{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==d)}},st=class extends N{constructor(t,e,s,r,o){super(t,e,s,r,o),this.type=5}_$AI(t,e=this){if((t=U(this,t,e,0)??d)===M)return;let s=this._$AH,r=t===d&&s!==d||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,o=t!==d&&(s===d||r);r&&this.element.removeEventListener(this.name,this,s),o&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},rt=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){U(this,t)}};var Dt=it.litHtmlPolyfillSupport;Dt?.(z,O),(it.litHtmlVersions??=[]).push("3.3.3");var At=(i,t,e)=>{let s=e?.renderBefore??t,r=s._$litPart$;if(r===void 0){let o=e?.renderBefore??null;s._$litPart$=r=new O(t.insertBefore(j(),o),o,void 0,e??{})}return r._$AI(i),r};var at=globalThis,m=class extends y{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=At(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return M}};m._$litElement$=!0,m.finalized=!0,at.litElementHydrateSupport?.({LitElement:m});var Ft=at.litElementPolyfillSupport;Ft?.({LitElement:m});(at.litElementVersions??=[]).push("4.2.2");var C=i=>(t,e)=>{e!==void 0?e.addInitializer(()=>{customElements.define(i,t)}):customElements.define(i,t)};var jt={attribute:!0,type:String,converter:D,reflect:!1,hasChanged:X},qt=(i=jt,t,e)=>{let{kind:s,metadata:r}=e,o=globalThis.litPropertyMetadata.get(r);if(o===void 0&&globalThis.litPropertyMetadata.set(r,o=new Map),s==="setter"&&((i=Object.create(i)).wrapped=!0),o.set(e.name,i),s==="accessor"){let{name:n}=e;return{set(l){let a=t.get.call(this);t.set.call(this,l),this.requestUpdate(n,a,i,!0,l)},init(l){return l!==void 0&&this.C(n,void 0,i,l),l}}}if(s==="setter"){let{name:n}=e;return function(l){let a=this[n];t.call(this,l),this.requestUpdate(n,a,i,!0,l)}}throw Error("Unsupported decorator location: "+s)};function p(i){return(t,e)=>typeof e=="object"?qt(i,t,e):((s,r,o)=>{let n=r.hasOwnProperty(o);return r.constructor.createProperty(o,s),n?Object.getOwnPropertyDescriptor(r,o):void 0})(i,t,e)}var v=class extends m{constructor(){super(...arguments);this.open=!1;this.placeholder="Capture name (optional)";this.nameLabel="Capture name";this.viewportLabel="Visible area";this.regionLabel="Select area"}get captureName(){return this.input()?.value.trim()||""}set captureName(e){let s=this.input();s&&(s.value=e)}ensureCaptureName(e){let s=this.input();s&&!s.value.trim()&&(s.value=e)}reset(){this.captureName="",this.open=!1}firstUpdated(){this.renderRoot.querySelectorAll("[data-scope]").forEach(e=>{e.addEventListener("click",()=>{this.choose(e.dataset.scope)})})}render(){return g`
      <input
        type="text"
        maxlength="120"
        placeholder=${this.placeholder}
        aria-label=${this.nameLabel}
      >
      <button type="button" data-scope="viewport">${this.viewportLabel}</button>
      <button type="button" data-scope="region">${this.regionLabel}</button>
    `}input(){return this.renderRoot.querySelector("input")}choose(e){this.open=!1,this.dispatchEvent(new CustomEvent("synthesix-capture-choice",{bubbles:!0,composed:!0,detail:{scope:e,captureName:this.captureName}}))}};v.styles=_`
    ${E(x)}

    :host {
      box-sizing: border-box;
      display: none;
      position: absolute;
      right: 0;
      bottom: 50px;
      width: 180px;
      padding: 6px;
      border: 1px solid var(--line, #cbd5e1);
      border-radius: var(--radius-sm, 6px);
      background: var(--surface, #ffffff);
      box-shadow: 0 14px 32px rgba(15, 23, 42, 0.24);
      color: var(--text, #0f172a);
      font: 600 13px/1.25 system-ui, Arial, sans-serif;
    }

    :host([open]) {
      display: block;
    }

    input {
      all: initial;
      box-sizing: border-box;
      display: block;
      width: 100%;
      margin-bottom: 5px;
      padding: 8px 9px;
      border: 1px solid var(--line, #cbd5e1);
      border-radius: 4px;
      background: var(--surface, #ffffff);
      color: var(--text, #0f172a);
      font: 500 13px/1.2 system-ui, Arial, sans-serif;
    }

    button {
      all: initial;
      box-sizing: border-box;
      display: block;
      width: 100%;
      padding: 9px 10px;
      border-radius: 4px;
      color: var(--text, #0f172a);
      cursor: pointer;
      font: 600 13px/1.2 system-ui, Arial, sans-serif;
    }

    button:hover,
    button:focus-visible {
      background: var(--accent-soft, #eff6ff);
      color: var(--accent-ink, #1d4ed8);
      outline: none;
    }
  `,h([p({type:Boolean,reflect:!0})],v.prototype,"open",2),h([p()],v.prototype,"placeholder",2),h([p({attribute:"name-label"})],v.prototype,"nameLabel",2),h([p({attribute:"viewport-label"})],v.prototype,"viewportLabel",2),h([p({attribute:"region-label"})],v.prototype,"regionLabel",2),v=h([C("sx-overlay-capture-menu")],v);var T=class extends m{constructor(){super(...arguments);this.label=""}render(){return g`<button type="button"></button>`}updated(){let e=this.renderRoot.querySelector("button");if(!e)return;let s=this.getAttribute("label")||this.label;e.textContent=s,e.setAttribute("aria-label",s)}};T.styles=_`
    ${E(x)}

    :host {
      box-sizing: border-box;
      display: none;
      position: fixed;
      left: 0;
      top: 0;
      z-index: 2147483647;
    }

    button {
      all: initial;
      box-sizing: border-box;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      max-width: min(260px, calc(100vw - 16px));
      padding: 7px 9px;
      border: 1px solid var(--accent-strong, #1d4ed8);
      border-radius: 999px;
      background: var(--accent, #2563eb);
      color: #ffffff;
      box-shadow: 0 10px 26px rgba(15, 23, 42, 0.26);
      cursor: pointer;
      font: 700 12px/1.1 system-ui, Arial, sans-serif;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    button:hover,
    button:focus-visible {
      background: var(--accent-strong, #1d4ed8);
      outline: 3px solid rgba(6, 182, 212, 0.45);
      outline-offset: 2px;
    }
  `,h([p()],T.prototype,"label",2),T=h([C("sx-overlay-selection-trigger")],T);var L=class extends m{constructor(){super(...arguments);this.hint="Drag to select evidence \xB7 Esc to cancel";this._selecting=!1;this._startX=0;this._startY=0;this._onKeyDown=e=>{e.key==="Escape"&&(e.preventDefault(),this._emitCancel())};this._onPointerDown=e=>{e.preventDefault(),this._selecting=!0,this._startX=e.clientX,this._startY=e.clientY;let s=this._boxEl;s&&s.classList.add("is-active");try{this.setPointerCapture(e.pointerId)}catch{}};this._onPointerMove=e=>{if(!this._selecting)return;let s=this._boxEl;if(!s)return;let r=Math.min(this._startX,e.clientX),o=Math.min(this._startY,e.clientY);s.style.left=`${r}px`,s.style.top=`${o}px`,s.style.width=`${Math.abs(e.clientX-this._startX)}px`,s.style.height=`${Math.abs(e.clientY-this._startY)}px`};this._onPointerUp=e=>{if(!this._selecting)return;this._selecting=!1;let s=Math.min(this._startX,e.clientX),r=Math.min(this._startY,e.clientY),o=Math.abs(e.clientX-this._startX),n=Math.abs(e.clientY-this._startY);if(o<8||n<8){this._emitCancel();return}this.dispatchEvent(new CustomEvent("synthesix-region-selected",{bubbles:!0,composed:!0,detail:{x:s+window.scrollX,y:r+window.scrollY,width:o,height:n}}))}}connectedCallback(){super.connectedCallback(),document.addEventListener("keydown",this._onKeyDown,!0),this.addEventListener("pointerdown",this._onPointerDown),this.addEventListener("pointermove",this._onPointerMove),this.addEventListener("pointerup",this._onPointerUp)}disconnectedCallback(){document.removeEventListener("keydown",this._onKeyDown,!0),super.disconnectedCallback()}get _boxEl(){return this.renderRoot.querySelector(".box")}_emitCancel(){this.dispatchEvent(new CustomEvent("synthesix-region-cancel",{bubbles:!0,composed:!0}))}render(){return g`
      <div class="hint">${this.hint}</div>
      <div class="box"></div>
    `}};L.styles=_`
    :host {
      all: initial;
      display: block;
      position: fixed;
      inset: 0;
      z-index: 2147483647;
      cursor: crosshair;
      background: rgba(15, 23, 42, 0.16);
      user-select: none;
      touch-action: none;
    }
    .hint {
      position: fixed;
      top: 16px;
      left: 50%;
      transform: translateX(-50%);
      padding: 9px 12px;
      border-radius: 6px;
      background: #0f172a;
      color: #ffffff;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.3);
      font: 600 13px Arial, sans-serif;
      pointer-events: none;
    }
    .box {
      display: none;
      position: fixed;
      border: 2px solid #06b6d4;
      background: rgba(6, 182, 212, 0.12);
      box-shadow: 0 0 0 9999px rgba(15, 23, 42, 0.38);
      pointer-events: none;
    }
    .box.is-active {
      display: block;
    }
  `,h([p()],L.prototype,"hint",2),L=h([C("sx-overlay-selection-box")],L);var b=class extends m{constructor(){super(...arguments);this.variant="primary";this.state="idle";this.label="";this.titleText="";this.ariaText="";this.icon="none";this.iconOnly=!1;this.disabled=!1}render(){return g`
      <button
        type="button"
      >
        ${this.renderIcon()}
        <span data-label></span>
      </button>
    `}updated(){let e=this.renderRoot.querySelector("button"),s=this.getAttribute("label")||this.label;if(!e)return;let r=e.querySelector("[data-label]");r&&(r.textContent=s),e.disabled=this.disabled||this.hasAttribute("disabled"),e.title=this.getAttribute("title-text")||this.titleText||s,e.setAttribute("aria-label",this.getAttribute("aria-text")||this.ariaText||s)}renderIcon(){return this.icon==="mark"?g`
        <svg viewBox="0 0 128 128" aria-hidden="true">
          ${Array.from({length:10},(e,s)=>g`
            <path
              d="M58 12 69 6l9 38-12 9-9-7z"
              transform="rotate(${s*36} 64 64)"
              fill=${s%2===0?"#FFFFFF":"#67E8F9"}
            ></path>
          `)}
          <circle cx="64" cy="64" r="14" fill="#FFFFFF"></circle>
        </svg>
      `:this.icon==="archive"?g`
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M5 3h11l3 3v15H5zM8 3v6h8V3M8 14h8M8 18h6"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linejoin="round"
          ></path>
        </svg>
      `:this.icon==="camera"?g`
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M14.5 4 16 7h3a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h3l1.5-3z"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linejoin="round"
          ></path>
          <circle
            cx="12"
            cy="13"
            r="3"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          ></circle>
        </svg>
      `:d}};b.styles=_`
    ${E(x)}

    :host {
      display: inline-flex;
      --sx-action-bg: var(--accent, #2563eb);
      --sx-action-border: var(--accent-strong, #1d4ed8);
      --sx-action-hover: var(--accent-strong, #1d4ed8);
      --sx-action-hover-border: #1e40af;
    }

    :host([variant="archive"]) {
      --sx-action-bg: #0891b2;
      --sx-action-border: #0e7490;
      --sx-action-hover: #0e7490;
      --sx-action-hover-border: #155e75;
    }

    :host([variant="capture"]) {
      --sx-action-bg: var(--text, #0f172a);
      --sx-action-border: #334155;
      --sx-action-hover: #334155;
      --sx-action-hover-border: #475569;
    }

    :host([state="saving"]),
    :host([state="archiving"]),
    :host([state="capturing"]) {
      --sx-action-bg: #475569;
      --sx-action-border: #334155;
      --sx-action-hover: #475569;
      --sx-action-hover-border: #334155;
    }

    :host([state="saved"]),
    :host([state="archived"]),
    :host([state="captured"]) {
      --sx-action-bg: var(--success, #16a34a);
      --sx-action-border: #047857;
      --sx-action-hover: #047857;
      --sx-action-hover-border: #065f46;
    }

    :host([state="error"]) {
      --sx-action-bg: var(--danger, #dc2626);
      --sx-action-border: #b91c1c;
      --sx-action-hover: #b91c1c;
      --sx-action-hover-border: #991b1b;
    }

    button {
      all: initial;
      box-sizing: border-box;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      height: 42px;
      min-width: 42px;
      padding: 0 14px 0 11px;
      border: 1px solid var(--sx-action-border);
      border-radius: var(--radius-sm, 6px);
      background: var(--sx-action-bg);
      color: #ffffff;
      box-shadow: var(--shadow-soft, 0 8px 22px rgba(15, 23, 42, 0.18));
      cursor: pointer;
      font: 700 14px/1 system-ui, Arial, sans-serif;
      white-space: nowrap;
      transition:
        background-color 140ms ease,
        border-color 140ms ease,
        box-shadow 140ms ease,
        transform 140ms ease;
    }

    :host([icon-only]) button {
      width: 42px;
      padding: 0;
    }

    :host([icon-only]) [data-label] {
      display: none;
    }

    button:hover:not(:disabled) {
      background: var(--sx-action-hover);
      border-color: var(--sx-action-hover-border);
      box-shadow: 0 12px 30px rgba(15, 23, 42, 0.34);
      transform: translateY(-1px);
    }

    button:focus-visible {
      outline: 3px solid rgba(6, 182, 212, 0.55);
      outline-offset: 2px;
    }

    button:disabled {
      cursor: wait;
    }

    svg {
      display: block;
      width: 20px;
      height: 20px;
      flex: 0 0 20px;
    }
  `,h([p({reflect:!0})],b.prototype,"variant",2),h([p({reflect:!0})],b.prototype,"state",2),h([p()],b.prototype,"label",2),h([p({attribute:"title-text"})],b.prototype,"titleText",2),h([p({attribute:"aria-text"})],b.prototype,"ariaText",2),h([p({reflect:!0})],b.prototype,"icon",2),h([p({type:Boolean,attribute:"icon-only",reflect:!0})],b.prototype,"iconOnly",2),h([p({type:Boolean,reflect:!0})],b.prototype,"disabled",2),b=h([C("sx-overlay-action")],b);window.SynthesixOverlay={tokensCss:x,version:"0.1.0"};var is=x;})();
